##work in progress

import json
import time
import argparse
from managers import AzureResourceManager
from config import ConfigManager as cm
from azure.identity import AzureCliCredential
from azure.mgmt.resource import SubscriptionClient, ResourceManagementClient
from azure.core.exceptions import ResourceNotFoundError
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, BarColumn, TextColumn
from rich.text import Text
from rich.panel import Panel
from rich import print


class AzureContainerCLI:
    def __init__(self):
        self.azure_manager = AzureResourceManager()
        self.commands = ContainerCommands()
        self.parser = argparse.ArgumentParser(description='Manage Azure resources.')
        self.parser.add_argument('--setup', action='store_true', help='Set up resources.')

    def run(self):
        args = self.parser.parse_args()
        if args.setup:
            self.commands.setup()
        else:
            self.commands.setup()
     
class ContainerCommands:
    def __init__(self):
        self.azure_manager = AzureResourceManager()
        self.config_manager = cm("resourceGroup.config.json")
        self.console = Console()

    def setup(self):
        self.console.print("Setting up resources...")
        self.azure_manager.setup_from_config(self.config_manager.read_config(),True)
        if self.azure_manager.check_resource_group_does_not_exist():
            self.azure_manager.create_resource_group()
        self.azure_manager.launch_container()
        self.azure_manager.stop_container()


if __name__ == "__main__":

    azure_container_cli = AzureContainerCLI()
    azure_container_cli.run()
