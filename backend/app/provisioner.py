from pydantic import BaseModel

class InstanceDetails(BaseModel):
    status: str
    host: str
    port: int

class Provisioner:
    def __init__(self):
        pass

    def provision_instance(self, instance):
        print("Provisioning MongoDB instance...")