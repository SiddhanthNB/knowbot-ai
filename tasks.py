from invoke.collection import Collection
from lib.tasks.one_time import one_time_collection

ns = Collection()
ns.add_collection(one_time_collection)
ns.configure({'run': {'echo': True}})
