class ConnectionResult(object):
    def __init__(self, mac_address, vm_uuid, network_name, network_key):
        self.mac_address = mac_address
        self.vm_uuid = vm_uuid
        self.network_name = network_name
        self.network_key = network_key
