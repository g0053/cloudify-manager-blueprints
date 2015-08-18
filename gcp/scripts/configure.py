########
# Copyright (c) 2015 GigaSpaces Technologies Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
#    * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    * See the License for the specific language governing permissions and
#    * limitations under the License.
import fabric.api
import os

from cloudify import ctx
from gcp.compute import constants


def configure_manager(manager_config_path=None, gcp_config=None):
    user = ctx.node.properties['cloudify']['cloudify_agent']['user']
    manager_config_path = manager_config_path or get_remote_config_path(user)
    auth = gcp_config.get(constants.AUTH)
    if auth and os.path.isfile(auth):
        fabric.api.put(auth, manager_config_path)
    resources = _construct_resources(gcp_config)
    provider = {'resources': resources}
    ctx.instance.runtime_properties['provider_context'] = provider


def _construct_resources(gcp_config):
    node_instances = ctx._endpoint.storage.get_node_instances()
    resources = {}
    for node_instance in node_instances:
        if node_instance.node_id in constants.SECURITY_GROUPS:
            run_props = node_instance.runtime_properties
            resources[node_instance.node_id] = {
                'id': run_props[constants.NAME],
                constants.TARGET_TAGS: run_props[constants.TARGET_TAGS],
                constants.SOURCE_TAGS: run_props[constants.SOURCE_TAGS]
            }

    resources[constants.GCP_CONFIG] = {
        constants.AUTH: constants.GCP_DEFAULT_CONFIG_PATH,
        constants.PROJECT: gcp_config[constants.PROJECT],
        constants.ZONE: gcp_config[constants.ZONE],
        constants.NETWORK: gcp_config[constants.NETWORK],
    }

    return resources


def get_remote_config_path(user):
    return os.path.join(os.sep, 'home', user, 'gcp_config.json')
