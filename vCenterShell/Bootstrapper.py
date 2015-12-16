from pyVim.connect import SmartConnect, Disconnect
from vCenterShell.pycommon.pyVmomiService import pyVmomiService
from commands.CommandExecuterService import CommandExecuterService
from commands.NetworkAdaptersRetrieverCommand import NetworkAdaptersRetrieverCommand
from pycommon.CloudshellDataRetrieverService import CloudshellDataRetrieverService
from pycommon.ResourceConnectionDetailsRetriever import ResourceConnectionDetailsRetriever


class Bootstrapper(object):
    def __init__(self):
        py_vmomi_service = pyVmomiService(SmartConnect, Disconnect)
        cloudshell_data_retriever_service = CloudshellDataRetrieverService()
        resource_connection_details_retriever = ResourceConnectionDetailsRetriever(cloudshell_data_retriever_service)
        network_adapter_retriever_command = NetworkAdaptersRetrieverCommand(py_vmomi_service,
                                                                            cloudshell_data_retriever_service,
                                                                            resource_connection_details_retriever)
        self.commandExecuterService = CommandExecuterService(py_vmomi_service, network_adapter_retriever_command)

    def get_command_executer_service(self):
        return self.commandExecuterService
