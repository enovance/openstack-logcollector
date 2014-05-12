# Copyright (C) 2013 eNovance SAS <licensing@enovance.com>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import eventlet
import threading
import os
import uuid
import netifaces

from oslo.config import cfg

from eventlet import greenio
from eventlet import greenthread
from eventlet import patcher
from eventlet import tpool
from eventlet import util as eventlet_util
from logcollector.openstack.common import importutils
from logcollector.openstack.common import periodic_task
from logcollector.openstack.common import log as logging
from logcollector.openstack.common import timeutils


from deploy import HostAgent
from logcollector.remoteExecutor import *
import logcollector.db as db

controller_opts = [
    cfg.StrOpt('collector_driver',
               default='logcollector.sos',
               help='A collection driver syntax library'),
    cfg.StrOpt('task_timeout',
               default=1,
               help='Interval between periodic tasks in seconds'),
    cfg.StrOpt('remote_dir',
               default='/tmp/',
               help='A remote path in which log files will be collected.'),
    ]


CONF = cfg.CONF
CONF.register_opts(controller_opts)
CONF.import_opt('project_dir', 'logcollector.api')


native_threading = patcher.original("threading")
_Queue = patcher.original("Queue")

LOG = logging.getLogger(__name__)


class Controller(object):

    def __init__(self):
        self.active_hosts = {}
        self.db_api = db.get_api()
        self.exec_queue = _Queue.Queue()
        self.hostProxy = HostProxy(self.exec_queue,
                                   self.db_api,
                                   self.active_hosts)
        self._init_executor()

    def _init_executor(self):
        executor = RemoteExecutor(self.exec_queue)
        executor.daemon = True
        executor.start()

    def _create_dir(self, taskUUID):
        task_dir = os.path.join(CONF.project_dir, taskUUID)
        if not os.path.exists(task_dir):
            os.makedirs(task_dir)

    def collect(self, hostList):
        taskUUID = self.db_api.create_task(hostList)
        self._create_dir(taskUUID)
        for host in hostList:
            eventlet.spawn_n(self.hostProxy.collect(host, taskUUID))

    def collect_complete(self, host, filename):
        #TODO: Not sure if a new thread is needed.
        eventlet.spawn_n(self.hostProxy.download(host, filename))

    @periodic_task.periodic_task(spacing=1, external_process_ok=True)
    def process_tasks(self):
        for task in self.db_api.get_all_tasks():
            self._clean_timedout_requests(task)
            if not self.db_api.get_hosts_with_task(task.id):
                self._finalize_task(task)

    def _clean_timedout_requests(self, task):
        if task.created_at + CONF.task_timeout < timeutils.utcnow():
            for host in self.db_api.get_hosts_with_task(task):
                self.db_api.update_host(host, {'task': None})
                self.active_hosts[host.id].release()

    def _finalize_task(self, task):
        self.db_api.delete_task(task.id)
        # tar .xs everything


class LocalCommand(object):

    def __init__(self, args, task):
        self.args = args
        self.task = task

    def execute(self):
        HostAgent().main(self.args, self.task)


class HostProxy(object):

    def __init__(self, exec_queue, db_api, active_hosts, hostType='Linux'):

        self.db_api = db_api
        self.active_hosts = active_hosts
        self.exec_queue = exec_queue
        self.driver = importutils.import_object(CONF.collector_driver)
        self._init_acitve_hosts()

    def _init_acitve_hosts(self):
        host_list = self.db_api.get_all_busy_hosts()
        for host in host_list:
            self.active_hosts[host.id] = eventlet.semaphore.Semaphore()
            self.active_hosts[host.id].aquire()

    def is_local(host):
        ip_addrs = []
        for dev in netifaces.interfaces():
            if netifaces.AF_INET in netifaces.ifaddresses(dev):
                ip_addrs.append(netifaces.ifaddresses(dev)
                                 [netifaces.AF_INET]['addr'])
        return host in ip_addrs

    def collect(self, host, taskID):
        if is_localhost():
            self._local_collect(host, taskID)
        elif CONF.isAsync():
            self._send_async_collect(host, taskID)
        else:
            self._sync_collect(host, taskID)

    def _local_collect(host, taskID):
        host_obj = self.db_api.get_host(targetHost)
        if not host_obj.id in self.active_hosts:
            self.active_hosts[host_obj.id] = eventlet.semaphore.Semaphore()
        with self.active_hosts[host_obj.id]:
            self.db_api.update_host(host_obj.id, {'task': taskID})

            local_command_args = self.driver.prepareLocal(tmpDir='/tmp')
            self.exec_queue.put(LocalCommand(local_command_args))

    def _send_async_collect(self, targetHost, taskID):
        host_obj = self.db_api.get_host(targetHost)
        if not host_obj.id in self.active_hosts:
            self.active_hosts[host_obj.id] = eventlet.semaphore.Semaphore()
        self.active_hosts[host_obj.id].aquire()
        self.db_api.update_host(host_obj.id, {'task': taskID})

        remote_command_args = self.driver.prepare(tmpDir=CONF.remote_dir)
        self.exec_queue.put(CollectCommand(targetHost,
                                           remote_command_args,
                                           remote_path=CONF.remote_dir))

    def _sync_collect(self, targetHost, taskID):
        pass
        #fileName = self.driver.sync_collect()
        #self.download(fileName)

    def download(self, targetHost, fileName):
        self.exec_queue.put(DownloadCommand(targetHost, fileName))
        host_obj = self.db_api.get_host(targetHost)
        self.db_api.update_host(host_obj.id, {'task': None})
        self.active_hosts[host_obj.id].release()
