from tendrl.ceph_integration import flows
from tendrl.commons.event import Event
from tendrl.commons.message import Message


class CreateECProfile(flows.CephIntegrationBaseFlow):
    def run(self):
        Event(
            Message(
                priority="info",
                publisher=tendrl_ns.publisher_id,
                payload={
                    "message": "Starting creation flow for ec-profile %s" %
                    self.parameters['ECProfile.name']
                },
                request_id=self.request_id,
                flow_id=self.uuid,
                cluster_id=tendrl_ns.tendrl_context.integration_id,
            )
        )

        super(CreateECProfile, self).run()
