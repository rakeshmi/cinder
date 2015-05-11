# Copyright (C) 2012 - 2014 EMC Corporation.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from migrate import ForeignKeyConstraint
from sqlalchemy import Boolean, Column, DateTime
from sqlalchemy import ForeignKey, MetaData, String, Table
import migrate.changeset.constraint as constraint
from cinder.i18n import _
from cinder.openstack.common import log as logging

LOG = logging.getLogger(__name__)


def upgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine

    # New table
    sharedsnapshots = Table(
        'sharedsnapshots', meta,
	Column('created_at', DateTime(timezone=False)),
        Column('updated_at', DateTime(timezone=False)),
        Column('deleted_at', DateTime(timezone=False)),
        Column('deleted', Boolean(create_constraint=True, name=None)),
        Column('snapshot_id', String(length=255),nullable=False),
        Column('project_id', String(length=255)),
        constraint.PrimaryKeyConstraint('snapshot_id','project_id'),
        mysql_engine='InnoDB',mysql_charset='utf8')

    try:
        sharedsnapshots.create()
    except Exception:
        LOG.error(_("Table |%s| not created!"), repr(sharedsnapshots))
        raise


       


def downgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine

    # Drop table
    sharedsnapshots = Table('sharedsnapshots', meta, autoload=True)
    try:
        sharedsnapshots.drop()
    except Exception:
        LOG.error(_("sharedsnapshots table not dropped"))
        raise

