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

# This is a placeholder for Kilo backports.
# Do not use this number for new Liberty work.  New work starts after
# all the placeholders.
#
# See this for more information:
# http://lists.openstack.org/pipermail/openstack-dev/2013-March/006827.html


from oslo_config import cfg
from oslo_log import log as logging
from sqlalchemy import MetaData, Table
from cinder.i18n import _LE, _LI
from oslo_utils import timeutils
# Get default value via config.  The defaults will either
# come from the default value set in the quota option
# configuration or via cinder.conf if the user has configured
# default value for per volume quota there.

CONF = cfg.CONF
CONF.import_opt('per_volume_quota', 'cinder.quota')
LOG = logging.getLogger(__name__)
CLASS_NAME = 'default'
CREATED_AT = timeutils.utcnow()


def upgrade(migrate_engine):
    """Add default per volume quota row data into DB."""
    meta = MetaData()
    meta.bind = migrate_engine
    quota_classes = Table('quota_classes', meta, autoload=True)
    row = quota_classes.count().\
        where(quota_classes.c.resource == 'per_volume_gigabytes').\
        execute().scalar()

    # Do not add entry if there is already 'default' entry.  We don't
    # want to write over something the user added.
    if row:
        LOG.info(_LI("Found existing 'default' entry for "
                     "per_volume_gigabytes in the quota_classes "
                     "table.  Skipping insertion of default value."))
        return

    try:
        # Set default quota for per volume size
        qci = quota_classes.insert()
        qci.execute({'created_at': CREATED_AT,
                     'class_name': CLASS_NAME,
                     'resource': 'per_volume_gigabytes',
                     'hard_limit': 1000,
                     'deleted': False, })
        LOG.info(_LI("Added default quota class data into the DB."))
    except Exception:
        LOG.error(_LE("Default quota class data not inserted into the DB."))
        raise


def downgrade(migrate_engine):
    """Don't delete the 'default' entries at downgrade time.
    We don't know if the user had default entries when we started.
    If they did, we wouldn't want to remove them.  So, the safest
    thing to do is just leave the 'default' entries at downgrade time.
    """
    pass
