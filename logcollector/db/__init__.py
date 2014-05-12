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
from logcollector.openstack.common import importutils

CONF = cfg.CONF
CONF.import_opt()


def get_api():
    return importutils.import_module(CONF.data_api)


def unwrap(db_api):
    return db_api


class Hosts(object):

    def __init__(self, context, db_api):
        self.context = context
        self.db_api = db_api


class Tasks(object):

    def __init__(self, context, db_api, image):
        self.context = context
        self.db_api = db_api
        self.image = image

