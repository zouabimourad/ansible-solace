#!/usr/bin/env python

# Copyright (c) 2019, Mark Street <mkst@protonmail.com>
# MIT License

"""Ansible-Solace Module for configuring Clients"""
import ansible.module_utils.network.solace.solace_utils as su
from ansible.module_utils.basic import AnsibleModule


class SolaceClientTask(su.SolaceTask):

    def __init__(self, module):
        su.SolaceTask.__init__(self, module)

    def lookup_item(self):
        return self.module.params["name"]

    def get_args(self):
        return [self.module.params["msg_vpn"]]

    def get_func(self, solace_config, vpn):
        """Pull configuration for all Clients associated with a given VPN"""
        path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.CLIENT_USERNAMES]
        return su.get_configuration(solace_config, path_array, "clientUsername")

    def create_func(self, solace_config, vpn, client, settings=None):
        """Create a Client"""
        defaults = {
            "enabled": True
        }
        mandatory = {
            "clientUsername": client,
        }
        data = su.merge_dicts(defaults, mandatory, settings)
        path = "/".join([su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.CLIENT_USERNAMES])

        return su.make_post_request(solace_config, path, data)

    def update_func(self, solace_config, vpn, client, settings=None):
        """Update an existing Client"""
        path = "/".join([su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.CLIENT_USERNAMES, client])
        return su.make_patch_request(solace_config, path, settings)

    def delete_func(self, solace_config, vpn, client):
        """Delete a Client"""
        path = "/".join([su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.CLIENT_USERNAMES, client])
        return su.make_delete_request(solace_config, path, None)


def run_module():
    """Entrypoint to module"""
    module_args = dict(
        name=dict(type='str', required=True),
        msg_vpn=dict(type='str', required=True),
        host=dict(type='str', default='localhost'),
        port=dict(type='int', default=8080),
        secure_connection=dict(type='bool', default=False),
        username=dict(type='str', default='admin'),
        password=dict(type='str', default='admin', no_log=True),
        settings=dict(type='dict', require=False),
        state=dict(default="present", choices=["absent", "present"]),
        timeout=dict(default=1, require=False)
    )
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    solace_client_task = SolaceClientTask(module)
    result = solace_client_task.do_task()

    module.exit_json(**result)


def main():
    """Standard boilerplate"""
    run_module()


if __name__ == '__main__':
    main()
