##work in progress

import json
import time
import argparse
from azure.identity import AzureCliCredential
from azure.mgmt.resource import SubscriptionClient, ResourceManagementClient
from azure.core.exceptions import ResourceNotFoundError
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, BarColumn, TextColumn
from rich.text import Text
from rich.panel import Panel
from rich import print

class AzureManager:
    def __init__(self):
        self.console = Console()
        self.credential = AzureCliCredential()
        self.subscription_client = SubscriptionClient(self.credential)

class AzureContainerCLI:
    def __init__(self):
        self.azure_manager = AzureManager()
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
        self.azure_manager = AzureManager()
        self.console = Console()

    def setup(self):
        self.console.print("Setting up resources...")

class ConfigManager:
    @staticmethod
    def read_config():
        with open('containterConfig.json') as json_file:
            return json.load(json_file)
    @staticmethod
    def write_config(config):
        with open('containerConfig.json', 'w') as json_file:
            json.dump(config, json_file, indent=4)


if __name__ == "__main__":

    azure_container_cli = AzureContainerCLI()
    azure_container_cli.run()
