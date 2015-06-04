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

from cinder.openstack.common import log as logging
import datetime
from oslo.config import cfg
from sqlalchemy import MetaData, Table
# Get default value via config.  The defaults will either
# come from the default value set in the quota configuration option
# or via cinder.conf if the user has configured
# default value for "per_volume_size_limit" there.

CONF = cfg.CONF
CONF.import_opt('per_volume_size_limit', 'cinder.quota')
LOG = logging.getLogger(__name__)
CLASS_NAME = 'default'
CREATED_AT = datetime.datetime.now()


def upgrade(migrate_engine):
    """Add default per_volume_gigabytes row into DB."""
    meta = MetaData()
    meta.bind = migrate_engine
    quota_classes = Table('quota_classes', meta, autoload=True)
    row = quota_classes.count().\
        where(quota_classes.c.resource == 'per_volume_gigabytes').\
        execute().scalar()

    # Do not add entry if there is already 'default' entry.  We don't
    # want to write over something the user added.
    if row:
        LOG.info(_("Found existing 'default' entry for "
                   "per_volume_gigabytes in the quota_classes "
                   "table. Skipping insertion of default value."))
        return

    try:
        # Set default quota for per volume size
        qci = quota_classes.insert()
        qci.execute({'created_at': CREATED_AT,
                     'class_name': CLASS_NAME,
                     'resource': 'per_volume_gigabytes',
                     'hard_limit': 1024,
                     'deleted': False, })
        LOG.info(_("Added default per_volume_gigabytes data row"
                   "into the quota_classes."))
    except Exception:
        LOG.error(_("Default per_volume_gigabytes row"
                    "not inserted into the DB."))
        raise


def downgrade(migrate_engine):
    """Don't delete the 'default' entries at downgrade time.
    We don't know if the user had default entries when we started.
    If they did, we wouldn't want to remove them.  So, the safest
    thing to do is just leave the 'default' entries at downgrade time.
    """
    pass
