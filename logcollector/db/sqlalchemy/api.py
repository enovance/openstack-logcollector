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
import sqlalchemy
import sqlalchemy.orm as sa_orm
import sqlalchemy.sql as sa_sql
from logcollector.db.sqlalchemy import models
from logcollector.openstack.common.db.sqlalchemy import session as db_session
from logcollector.openstack.common import timeutils
#from logcollector import exceptions
import uuid


BASE = models.BASE
CONF = cfg.CONF


get_engine = db_session.get_engine
get_session = db_session.get_session


def create_task(hostList):
    task_ref = models.Task()
    task_ref.id = str(uuid.uuid4())
    task_ref.created_at = timeutils.utcnow()
    task_ref.save()
    return task_ref.id


def get_host(hostID, session=None):
    session = session or get_session()
    query = session.query(models.Host).filter_by(id=hostID)
    result = query.first()
    if not result:
        raise Exception('Host Not Found: %s' % hostID)
        #exceptions.HostNotFound(host_id=hostID)
    return result


def get_all_tasks():
    session = get_session()
    return session.query(models.Task).all()


def get_hosts_with_task(taskUUID):
    session = get_session()
    return session.query(models.Host).filter_by(task=taskUUID).all()


def update_host(hostID, values):
    session = get_session()
    with session.begin():
        host_obj = get_host(hostID, session=session)
        host_obj.update(values)
    return host_obj


def get_all_busy_hosts():
    session = get_session()
    return session.query(models.Host).filter(models.Host.task != None).all()


def delete_task(task_obj):
    session = get_session()
    with session.begin():
        session.delete(task_obj)
