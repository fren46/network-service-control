
from krules_core.base_functions import *
from krules_core import RuleConst as Const

from krules_core.providers import proc_events_rx_factory
from krules_env import publish_proc_events_errors, publish_proc_events_all  #, publish_proc_events_filtered

import json

try:
    from ruleset_functions import *
except ImportError:
    # for local development
    from .ruleset_functions import *


rulename = Const.RULENAME
subscribe_to = Const.SUBSCRIBE_TO
ruledata = Const.RULEDATA
filters = Const.FILTERS
processing = Const.PROCESSING


# proc_events_rx_factory().subscribe(
#   on_next=publish_proc_events_all,
# )
proc_events_rx_factory().subscribe(
 on_next=publish_proc_events_errors,
)


class PPrint(RuleFunctionBase):

    def execute(self, something):
        from pprint import pprint
        pprint(something)


rulesdata = [
    """
    filter resources with multus network annotations
    set annotations properties with interfaces name and IPs 
    set extended property of resources
    """,
    {
        rulename: "set-subject-multus-interface",
        subscribe_to: [
            "dev.knative.apiserver.resource.add",
            "dev.knative.apiserver.resource.update",
        ],
        ruledata: {
            filters: [
                Filter(
                    lambda payload:
                        "k8s.v1.cni.cncf.io/networks" in payload.get("metadata").get("annotations", {}) and
                        "k8s.v1.cni.cncf.io/networks-status" in payload.get("metadata").get("annotations", {})
                ),
            ],
            processing: [
                SetMultusInterfaces(),
            ]
        }
    },

    """
    filter deletion of resources with multus network annotations
    generate an event with type "fw-delete"
    """,
    {
        rulename: "delete-subject-multus-interface",
        subscribe_to: [
            "dev.knative.apiserver.resource.delete",
        ],
        ruledata: {
            filters: [
                Filter(
                    lambda payload:
                    "k8s.v1.cni.cncf.io/networks" in payload.get("metadata").get("annotations", {}) and
                    "k8s.v1.cni.cncf.io/networks-status" in payload.get("metadata").get("annotations", {})
                ),
            ],
            processing: [
                Route("fw-delete", lambda payload: f"service:{payload['metadata']['name']}", {}),
            ]
        }
    },
]

