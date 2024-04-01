from config import ConfigManager as cm
from azure.core.exceptions import ResourceNotFoundError
from azure.identity import AzureCliCredential
from azure.mgmt.resource import ResourceManagementClient, SubscriptionClient
from rich.console import Console
from rich.progress import BarColumn, Progress, TextColumn
from rich.table import Table
from .AzureCredentialProvider import ICredentialProvider, AzureCliCredentialProvider
import time

class ContainerManager:
    def __init__(self, icreds: ICredentialProvider = AzureCliCredentialProvider(), console: Console = None):
        self.console = console if console else Console()
        self.credential_provider = icreds
        self.credential = None
        self.subscriptions = None
        self.container_name = None
        self.container_service = None
        self.subscription_id = None
        self.resource_group_name = None
        self.resource_group_location = None
        self.subscription_client = None
        self.resource_client = None


    def __defaults(self):
        try:
            defualtConfig = cm("defaults.config.json")
        except Exception as e:
            Console().print("Failed to read defaults.config.json", style="bold red")
            Console().print(e, style="red")
        try:
            resourceConfig = cm("resourceGroup.config.json")
        except Exception as e:
            Console().print("Failed to read resourceGroup.config.json, please run ResourceGroup or make the config.", style="bold red")
            Console().print(e, style="red")
        try:
            self.resource_group_name = defualtConfig.read_config()["default_resource_group_name"]
            self.resource_group_location = defualtConfig.read_config()["default_location"]
            self.container_name = defualtConfig.read_config()["default_container_name"]
            self.container_service = defualtConfig.read_config()["default_container_service"]
            self.subscription_id = resourceConfig.read_config()["subscription_id"]
            self.resource_group_name = resourceConfig.read_config()["resource_group_name"]
            self.resource_group_location = resourceConfig.read_config()["resource_group_location"]

        except Exception as e:
            Console().print("Failed to read configs.", style="bold red")
            Console().print(e, style="red")
            
    def authenticate(self):
        self.__defaults()
        try:
            self.credential = self.credential_provider.get_credential()
            self.subscription_client = SubscriptionClient(self.credential)
            self.console.print("Authenticated", style="bold green")
        except Exception as e:
            self.console.print("Failed to authenticate", style="bold red")
            self.console.print(e, style="red")

        try:
            self.