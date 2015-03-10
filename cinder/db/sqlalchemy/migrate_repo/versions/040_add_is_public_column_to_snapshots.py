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

from sqlalchemy import Column
from sqlalchemy import MetaData, Table, Boolean
from cinder.i18n import _
from cinder.openstack.common import log as logging

LOG = logging.getLogger(__name__)


def upgrade(migrate_engine):
    """Add is_public column to snapshots."""
    meta = MetaData()
    meta.bind = migrate_engine
    snapshots = Table('snapshots', meta, autoload=True)
    is_public = Column('is_public', Boolean)
    try:
        snapshots.create_column(is_public)
        snapshots.update().values(is_public=False).execute()
    except Exception:
        LOG.error(_("Column |%s| not created!"), repr(is_public))
        raise


def downgrade(migrate_engine):
    """Remove is_public column from snapshots."""
    meta = MetaData()
    meta.bind = migrate_engine
    snapshots = Table('snapshots', meta, autoload=True,
                      autoload_with=migrate_engine)
    is_public = snapshots.columns.is_public

    ''' Remove the CHECK constraint before delete Boolean Column '''
    for constraint in snapshots.constraints:
        if is_public.name in unicode(getattr(constraint, 'sqltext', '')):
            snapshots.constraints.remove(constraint)
            break

    try:
        snapshots.drop_column(is_public)
    except Exception:
        LOG.error(_("is_public Column not dropped from snapshots table"))
        raise
