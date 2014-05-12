# Copyright (C) 2013 eNovance SAS <licensing@enovance.com>
#
# Author: Vladik Romanovsky <vladik.romanovsky@enovance.com>
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

import os
import multiprocessing
import eventlet
import paramiko
import threading
from oslo.config import cfg
from eventlet import greenio
from eventlet import greenthread
from eventlet import patcher
from eventlet import tpool
from eventlet import util as eventlet_util
from logcollector.openstack.common import importutils
from logcollector.openstack.common import log as logging

import logcollector.db

_threading = patcher.original("threading")
_Queue = patcher.original("Queue")

LOG = logging.getLogger(__name__)

executor_opts = [
    cfg.BoolOpt('isAsync',
               default=True,
               help='Indicates whether the log collection'
                    'should be async or sync.'),
    cfg.StrOpt('path_to_priv_key_file',
               default='/var/lib/nova',
               help='Path to a private key'),
    cfg.StrOpt('username',
               default='nova',
               help='User name under which runs the service.'),
    cfg.StrOpt('deploy_file',
               default='deploy.py',
               help='File to be executed on the remote host to'
                    'control collection'),
    ]


CONF = cfg.CONF
CONF.register_opts(executor_opts)


# TODO: Add sessions cache
class SSHCommand(object):
    def __init__(self, host, command=None, port=22, username='nova'):
        self.targetHost = host
        self.remoteCommand = command
        self.trans = paramiko.Transport((host, port))
        self.trans.connect(username=username,
                           key_filename=CONF.path_to_priv_key_file)
        self.session = self.trans.open_channel("session")

    def _init_sftp(self):
        self.sftp = paramiko.SFTPClient.from_transport(self.trans)
        #task?

    def execute(self):
        pass


class CollectCommand(SSHCommand):

    def __init__(self, targetHost, RemoteCommandArgs, remotePath='/tmp'):
        super(CollectCommand, self).__init__(targetHost)
        self.RemoteCommandArgs = RemoteCommandArgs
        self.remotePath = remotePath
        self.deploy_file = os.path.join(os.getcwd(), CONF.deploy_file)
        self._init_sftp()

    def execute(self):
        self.sftp.put(self.deploy_file, self.remotePath)
        self.sftp.close()
        self.session.exec_command('python %s/%s %s' % (self.remotePath,
                                                       CONF.deploy_file,
                                                       self.RemoteCommandArgs))
        exit_status = self.session.recv_exit_status()


class DownloadCommand(SSHCommand):

    def __init__(self, targetHost, remotePath):
        super(DownloadCommand, self).__init__(targetHost)
        self.remotePath = remotePath
        self._init_sftp()

    def execute(self):
        self.sftp.get(self.remotePath, self.local_store_path)
        self.sftp.close()


class RemoteExecutor(_threading.Thread):

    def __init__(self, exec_queue):
        super(RemoteExecutor, self).__init__()
        self.alive = _threading.Event()
        self.alive.set()

    def run(self):
        while self.alive.isSet():
            if len(self.exec_queue) > 0:
                commandObj = self.exec_queue.get(True, 0.1)
                multiprocessing.Process(target=commandObj.execute)

    def join(self, timeout=None):
        self.alive.clear()
        _threading.Thread.join(self, timeout)
