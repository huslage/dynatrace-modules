#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2018 Aaron Huslage (Red Hat) / Juergen Etzlstorfer (Dynatrace) <ahuslage@redhat.com> <juergen.etzlstorfer@dynatrace.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = '''
---
module: dynatrace_deployment
version_added: "1.2"
author: "Juergen Etzlstorfer (@jetzlstorfer)"
short_description: Notify Dynatrace about app deployments
description:
   - Notify Dynatrace about app deployments (see https://www.dynatrace.com/support/help/dynatrace-api/events/how-do-i-push-events-from-3rd-party-systems/)
options:
  tenant_url:
    description:
      - Tenant URL for the Dynatrace Tenant
    required: true
  api_token:
    description:
      - Dynatrace API Token
    required: true
  entity_id:
    description:
      - Entity Id of the affected entities for this deployment
    required: true
  deploymentVersion:
    description:
      - A deployment version number
    required: false
  remediationAction:
    description:
      - A remediation action in case Dynatrace detects issues related to this deployment
    required: false
  validate_certs:
    description:
      - If C(no), SSL certificates will not be validated. This should only be used
        on personally controlled sites using self-signed certificates.
    required: false
    default: 'yes'
    type: bool
    version_added: 1.5.1

requirements: []
'''

EXAMPLES = '''
- dynatrace_deployment:
    tenant_url: https://mytenant.live.dynatrace.com
    api_token: XXXXXXXX
    entity_id: APPLICATION-XXXXXXXXXX
    deploymentVersion: '2.0'
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import fetch_url
from ansible.module_utils.six.moves.urllib.parse import urlencode

# ===========================================
# Module execution.
#


def main():

    module = AnsibleModule(
        argument_spec=dict(
            tenant_url=dict(required=True),
            api_token=dict(required=True),
            entity_id=dict(required=True),
            deploymentVersion=dict(required=False),
            remediationAction=dict(required=False),
            validate_certs=dict(default='yes', type='bool'),
        ),
        # required_one_of=[['app_name', 'application_id']],
        supports_check_mode=True
    )

    # build list of params
    params = {}
    # if module.params["entity_id"]:
    #     params["entity_id"] = module.params["entity_id"]
    # else:
    #     module.fail_json(msg="entity_id must be set")

    for item in ["deploymentVersion", "remediationAction"]:
        if module.params[item]:
            params[item] = module.params[item]

    params["eventType"] = "CUSTOM_DEPLOYMENT"
    #params["attachRules"] = TODO
    params["deploymentName"] = "Update"
    params["deploymentProject"] = "My Project"
    params["source"] = "Ansible"
    #params["customProperies"] = TODO if needed

    # If we're in check mode, just exit pretending like we succeeded
    if module.check_mode:
        module.exit_json(changed=True)

    # Send the deployment info to Dynatrace
    dt_url = "https://" + module.params["tenant_url"] + "/api/v1/events/?Api-Token=" + module.params["api_token"]
    data = urlencode(params)
    # headers = {
    #     'x-api-key': module.params["token"],
    # }
    response, info = fetch_url(module, dt_url, data=data, headers=headers)
    if info['status'] in (200, 201):
        module.exit_json(changed=True)
    else:
        module.fail_json(msg="unable to send deployment event to Dynatrace: %s" % info['msg'])


if __name__ == '__main__':
    main()