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

from oslo.config import cfg
from oslo.db import concurrency
from logcollector.openstack.common import importutils

CONF = cfg.CONF

_BACKEND_MAPPING = {'sqlalchemy': 'logcollector.db.sqlalchemy.api'}

IMPL = concurrency.TpoolDbapiWrapper(CONF, backend_mapping=_BACKEND_MAPPING)


def create_task(hostList):
    return IMPL.create_task(hostList)


def get_host(hostID, session=None):
    return IMPL.get_host(hostID, session)


def get_all_tasks():
    return IMPL.get_all_tasks()


def get_hosts_with_task(taskUUID):
    return IMPL.get_hosts_with_task(taskUUID)


def update_host(hostID, values):
    return IMPL.update_host(hostID, values)


def get_all_busy_hosts():
    return IMPL.get_all_busy_hosts()


def delete_task(task_obj):
    return IMPL.delete_task(task_obj)


class Hosts(object):

    def __init__(self, context, db_api):
        self.context = context
        self.db_api = db_api


class Tasks(object):

    def __init__(self, context, db_api, image):
        self.context = context
        self.db_api = db_api
        self.image = image
