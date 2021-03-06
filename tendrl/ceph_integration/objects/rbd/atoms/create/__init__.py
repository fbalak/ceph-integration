from tendrl.ceph_integration.manager.crud import Crud
from tendrl.commons import objects
from tendrl.ceph_integration.objects.rbd import Rbd
from tendrl.commons.event import Event
from tendrl.commons.message import Message


class Create(objects.BaseAtom):
    obj = Rbd
    def __init__(self, *args, **kwargs):
        super(Create, self).__init__(*args, **kwargs)

    def run(self):
        attrs = dict(name=self.parameters['Rbd.name'],
                     size=str(self.parameters['Rbd.size']),
                     pool_id=self.parameters.get('Rbd.pool_id')
                     )
        Event(
            Message(
                priority="info",
                publisher=NS.publisher_id,
                payload={
                    "message": "Creating rbd %s on pool %s" %
                    (self.parameters['Rbd.name'],
                     self.parameters['Rbd.pool_id'])
                },
                job_id=self.parameters['job_id'],
                flow_id=self.parameters['flow_id'],
                cluster_id=NS.tendrl_context.integration_id,
            )
        )

        crud = Crud()
        ret_val = crud.create("rbd", attrs)
        if ret_val['response'] is not None and \
            ret_val['response']['error'] is True:
            Event(
                Message(
                    priority="info",
                    publisher=NS.publisher_id,
                    payload={
                        "message": "Failed to create rbd %s."
                        " Error: %s" % (self.parameters['Rbd.name'],
                                        ret_val['error_status'])
                    },
                    job_id=self.parameters['job_id'],
                    flow_id=self.parameters['flow_id'],
                    cluster_id=NS.tendrl_context.integration_id,
                )
            )
            return False

        Event(
            Message(
                priority="info",
                publisher=NS.publisher_id,
                payload={
                    "message": "Successfully created rbd %s on pool %s" %
                    (self.parameters['Rbd.name'],
                     self.parameters['Rbd.pool_id'])
                },
                job_id=self.parameters['job_id'],
                flow_id=self.parameters['flow_id'],
                cluster_id=NS.tendrl_context.integration_id,
            )
        )

        pool_name = NS.etcd_orm.client.read(
            "clusters/%s/Pools/%s/pool_name" %
            (NS.tendrl_context.integration_id,
             self.parameters['Rbd.pool_id'])
        ).value
        rbd_details = NS.state_sync_thread._get_rbds(pool_name)
        for k, v in rbd_details.iteritems():
            NS.ceph.objects.Rbd(
                name=k,
                size=v['size'],
                pool_id=self.parameters['Rbd.pool_id'],
                flags=v['flags'],
                provisioned=NS.state_sync_thread._to_bytes(
                    v['provisioned']),
                used=NS.state_sync_thread._to_bytes(v['used'])
            ).save()

        return True
