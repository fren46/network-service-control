
from krules_core.base_functions import *
from krules_core import RuleConst as Const

from krules_core.providers import proc_events_rx_factory, subject_factory
from krules_env import publish_proc_events_errors, publish_proc_events_all  #, publish_proc_events_filtered
from k8s_functions import K8sObjectsQuery
from app_functions.k8s import exec_command

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


CL_LB_NETWORK = "default/cl-lb-macvlan-conf"
LB_FW_NETWORK = "default/lb-fw-macvlan-conf"
FW_SV_NETWORK = "default/fw-sv-macvlan-conf"


def set_running_fws_in_payload(obj, payload):
    """
    Set ip address of the LB_FW_NETWORK interface of the FW passed as first parameter
    in the payload passed as second parameter.
    """
    subject = subject_factory(f"service:{obj['metadata']['name']}")
    try:
        if subject.get_ext("multusapp"):
            payload["fw_ips"] = payload.get("fw_ips", [])
            payload["fw_ips"].append(subject.get(LB_FW_NETWORK)["ips"][0])
    except AttributeError as ex:
        print(str(ex))


def add_fw_to_lb(ob, dest_net_subnet, fw_ips):
    """
    Modify the routing table of the pod passed as first parameter using the
    destination network "dest_net_subnet" and the IPs of the FW "fw_ips".
    :param ob: multipath-router get by K8sObjectQuery
    :param dest_net_subnet: ip with subnetmask of the destination network
    :param fw_ips: list of the approved FW
    :return: None
    """
    command = [
        '/bin/sh',
        '-c',
        'ip route del '+dest_net_subnet]
    exec_command(ob, command=command, container="multipath", preload_content=False)
    if len(fw_ips):
        separator = ' via '
        if len(fw_ips) > 1:
            separator = ' nexthop via '
        command = [
            '/bin/sh',
            '-c',
            'ip route add '+dest_net_subnet+separator+separator.join(fw_ips)]
        exec_command(ob, command=command, container="multipath", preload_content=False)


rulesdata = [
    """
    change the LoadBalancer configuration when a Firewall is created or deleted
    """,
    {
        rulename: "on-firewall-creation",
        subscribe_to: ["subject-property-changed", "fw-delete"],
        ruledata: {
            processing: [
                # set the network ip in payload if the NetworkAttachmentDefinition name is "fw-sv-macvlan-conf"
                K8sObjectsQuery(
                    apiversion="k8s.cni.cncf.io/v1",
                    kind="NetworkAttachmentDefinition",
                    foreach=lambda payload: lambda obj:
                        obj.obj["metadata"]["name"] == "fw-sv-macvlan-conf" and
                        payload.setdefault("subnet", json.loads(obj.obj["spec"]["config"])["ipam"]["subnet"])
                ),
                # set firewall name in payload
                K8sObjectsQuery(
                    apiversion="v1",
                    kind="Pod",
                    foreach=lambda payload: lambda obj:
                        set_running_fws_in_payload(obj.obj, payload),
                    selector={
                        "multus-app": "firewall",
                    },
                ),
                # configure multipath route
                K8sObjectsQuery(
                    apiversion="v1",
                    kind="Pod",
                    selector= {
                            "multus-app": "multipath",
                        },
                    foreach=lambda payload: lambda obj: (
                            add_fw_to_lb(obj,
                                     payload["subnet"],
                                     payload["fw_ips"])
                    )
                )
            ]
        }
    },
    """
    Delete the subject
    """,
    {
        rulename: "on-firewall-deletion",
        subscribe_to: ["fw-delete"],
        ruledata: {
            processing: [
                FlushSubject()
            ]
        }
    }
]

