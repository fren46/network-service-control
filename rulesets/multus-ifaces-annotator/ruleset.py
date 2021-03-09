
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
                # PPrint(
                #     lambda payload: subject_factory(f"service:{payload['metadata']['name']}").get
                # ),
            ]
        }
    },

]

