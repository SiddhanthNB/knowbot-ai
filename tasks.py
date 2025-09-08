from invoke.collection import Collection
from utils.tasks.one_time_tasks import one_time_collection

ns = Collection()
ns.add_collection(one_time_collection)
ns.configure({'run': {'echo': True}})
