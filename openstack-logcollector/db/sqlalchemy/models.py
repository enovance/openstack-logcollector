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

import uuid

from sqlalchemy import BigInteger
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import ForeignKey
from sqlalchemy import Index
from sqlalchemy import Integer
from sqlalchemy.orm import backref, relationship
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.types import TypeDecorator
from sqlalchemy import UniqueConstraint

from sqlalchemy import Column, Integer, String, BigInteger
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import ForeignKey, DateTime, Boolean, Text
from sqlalchemy.orm import relationship, backref, object_mapper
from sqlalchemy.types import TypeDecorator
from sqlalchemy import Index, UniqueConstraint
from logcollector.openstack.common.db.sqlalchemy import models

from logcollector.openstack.common import timeutils
from logcollector.openstack.common import uuidutils

BASE = declarative_base()


class BaseModel(models.SoftDeleteMixin,
               models.TimestampMixin,
               models.ModelBase):
    metadata = None


class Host(BASE, BaseModel):
    __tablename__ = 'hosts'

    id = Column(String(36), primary_key=True,
                default=lambda: str(uuid.uuid4()))
    task = Column(String(36))
    ip = Column(String(20))


class Task(BASE, BaseModel):
    __tablename__ = 'tasks'
    __protected_attributes__ = set(['created_at', 'last_update'])

    id = Column(String(36), primary_key=True,
                default=lambda: str(uuid.uuid4()))
    path = Column(String(255))
    status = Column(String(30))
    created_at = Column(DateTime, default=timeutils.utcnow,
                        nullable=False)
    last_update = Column(DateTime, default=timeutils.utcnow,
                         nullable=False)
