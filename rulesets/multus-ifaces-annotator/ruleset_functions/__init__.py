
from krules_core.base_functions import *
from krules_core.providers import subject_factory


class SetMultusInterfaces(RuleFunctionBase):

    def execute(self):
        '''
        take the list of networks interfaces name set by multus in "k8s.v1.cni.cncf.io/networks"
        annotation and for each name add into the subject the pair name-status, which status is
        the status set by multus in "k8s.v1.cni.cncf.io/networks-status" annotation.
        (status mainly contain the ip of the network interface)
        '''

        interfaces = self.payload["metadata"]["annotations"]["k8s.v1.cni.cncf.io/networks"]
        statuses = self.payload["metadata"]["annotations"]["k8s.v1.cni.cncf.io/networks-status"]
        statuses = json.loads(statuses)
        interfaces = interfaces.split(', ')

        subject = subject_factory(
            f"service:{self.payload['metadata']['name']}"
        )
        if "multus-app" in self.payload["metadata"]["labels"]:
            subject.set_ext("multusapp", self.payload["metadata"]["labels"]["multus-app"])

        for interface in interfaces:
            for status in statuses:
                if status.get("name") == interface:
                    subject.set(status.get("name"), status, use_cache=False)
                    break
