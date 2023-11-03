from spaceone.core.pygrpc.server import GRPCServer
from .cost import Cost
from .data_source import DataSource
from .job import Job

_all_ = ['app']

app = GRPCServer()
app.add_service(Cost)
app.add_service(DataSource)
app.add_service(Job)