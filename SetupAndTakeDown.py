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
        self.credential = None
        self.subscription_client = None
        self.subscriptions = None
        self.subscription = None 
        self.resource_group_name = "TestingResourceGroup"
        self.resource_group_location = "westus"
        self.yolo = False


    def to_dict(self):
        return {
            "subscription.id": self.subscription.id,
            "resource_group_name": self.resource_group_name,
            "resource_group_location": self.resource_group_location,
            "yolo": self.yolo
        }


    def setup(self):
        self.authenticate()
        self.print_subscriptions()
        self.subscription = self.get_subscription()
        self.print_subscription()
    
    def setup_from_config(self, config, yolo=None):
        self.authenticate()
        self.subscription_client = SubscriptionClient(self.credential)
        self.subscriptions = list(self.subscription_client.subscriptions.list())
        self.subscription = self.get_subscription(config["subscription.id"])
        self.resource_group_name = config["resource_group_name"]
        if yolo is not None:
            self.yolo = yolo
        else:
            self.yolo = config["yolo"]

    def authenticate(self):
        try:
            self.credential = AzureCliCredential()
            self.console.print("[green]Authenticated[/] using [cyan]Azure CLI[/] credentials")
        except Exception as e:
            self.console.print("Failed to authenticate using Azure CLI credentials", style="bold red")
            self.console.print("You may need to type az login to make this work :(", style="yellow")
            self.console.print(e, style="red")

    def print_subscriptions(self):
        self.subscription_client = SubscriptionClient(self.credential)
        self.subscriptions = list(self.subscription_client.subscriptions.list())
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("No.", style="dim")
        table.add_column("Name")
        table.add_column("ID")

        for i, sub in enumerate(self.subscriptions):
            table.add_row(str(i), sub.display_name, sub.id)

        self.console.print(table)

    def get_subscription(self,subscription_id_input=None):
        if subscription_id_input is None:
            
            subscription_id_input = int(input("Enter the subscription id: "))

            try:
                self.subscription = self.subscriptions[subscription_id_input]
            except Exception as e:
                self.console.print("Invalid subscription ID", style="bold red")
                return self.get_subscription()
        else:
            self.subscription = self.subscription_client.subscriptions.get(subscription_id_input)
            Console().print(f"Subscription with ID [bold green]{self.subscription.display_name}[/] selected")
        return self.subscription

    
    def print_subscription(self):
        self.console.print(f"Selected subscription: [bold magenta]{self.subscription.display_name}[/]", style="blue")

    def check_resource_group_does_not_exist(self):
        try:
            self.subscription.id = self.subscription.id.replace('/subscriptions/', '')
            resource_client = ResourceManagementClient(self.credential, subscription_id=self.subscription.id)
            Console().print("Resource Management Client created", style="green")

            check_group = resource_client.resource_groups.get(self.resource_group_name)
            if check_group is not None:
                Console().print(f"Resource Group with name [bold]{self.resource_group_name}[/] already exists", style="red")
                return False
            else:
                Console().print(f"Resource Group with name [bold]{self.resource_group_name}[/] does not exist", style="green")
                return True
        except Exception as e:
            return True
    
    from azure.core.exceptions import ResourceNotFoundError

    def check_azure_resource(self):
        try:
            self.subscription.id = self.subscription.id.replace('/subscriptions/', '')
            resource_client = ResourceManagementClient(self.credential, subscription_id=self.subscription.id)
            check_group = resource_client.resource_groups.get(self.resource_group_name)
            while check_group is not None:
                time.sleep(3)
                check_group = resource_client.resource_groups.get(self.resource_group_name)

            return True
        except ResourceNotFoundError:
            # The resource does not exist, return True
            return True
        except Exception as e:
            Console().print("Failed to check [cyan]Azure[/] resource", style="bold red")
            return False

    def create_resource_group(self):
        try:
            resource_group_params = {'location': self.resource_group_location}
            resource_client = ResourceManagementClient(self.credential, subscription_id=self.subscription.id)
            resource_group = resource_client.resource_groups.create_or_update(
                self.resource_group_name, 
                resource_group_params
            )
            Console().print(f"Resource Group created with name [bold magenta]{resource_group.name}[/]", style="green")
        except Exception as e:
            Console().print("Failed to create Resource Group", style="bold red")
            Console().print(e, style="red")

    def remove_resource_group(self):
        try:
            resource_client = ResourceManagementClient(self.credential, subscription_id=self.subscription.id)
            resource_client.resource_groups.begin_delete(self.resource_group_name)
            Console().print(f"Resource Group with name [bold]{self.resource_group_name}[/] deleting", style="green")
        except Exception as e:
            Console().print("Failed to delete Resource Group", style="bold red")
            Console().print(e, style="red")
        try:
            progress = Progress(
                    TextColumn("[bold cyan]{task.description}", justify="right"),
                    BarColumn(bar_width=None, style="cyan", complete_style="bold bright_green"),  # Fills the space dynamically
                    TextColumn("cHeCkInG!", justify="right"),
                    expand=True
                )
            with progress:
                task = progress.add_task("[cyan]Checking Azure resource...[/]", total=None)
                result = self.check_azure_resource()
                progress.update(task, completed=100, description="[bold green]Resource Removed!")
        except Exception as e:
            Console().print("Something failed while checking, the resource could be deleted but who knows?", style="bold red")
            Console().print(e, style="red")

class AzureManagerCLI:
    def __init__(self):
        self.azure_manager = AzureManager()
        self.parser = argparse.ArgumentParser(description='Manage Azure resources.')
        self.parser.add_argument('--setup', action='store_true', help='Set up resources.')
        self.parser.add_argument('--takedown', action='store_true', help='Take down resources.')
        self.parser.add_argument('--setup-takedown', action='store_true', help='Set up resource if its not up, take down resource group if it is.')
        self.parser.add_argument('--yolo', action='store_true', help='YOLO mode, skips user input and yeets your scripts into the void.')
        self.parser.add_argument('--no-config', action='store_true', help='Do not use the config file.')

    def run(self):
        commands = Commands()
        args = self.parser.parse_args()
        if args.yolo:
            commands.yolo = True
        if args.no_config:
            commands.useconfig = False


            

        if args.setup:
            commands.setup()
        elif args.takedown:
            commands.takedown()
        elif args.setup_takedown:
            commands.set_up_and_take_down()
        else:
            commands.set_up_and_take_down()

class Commands:
    def __init__(self):
        self.azure_manager = AzureManager()
        self.yolo = False
        self.useconfig = True

    def set_yolo(self, yolo):
        self.azure_manager.yolo = yolo
        self.yolo = yolo

    def set_config(self):
        try:
            config = ConfigManager.read_config()
        except Exception as e:
            config = None
        if config and self.useconfig:
            self.azure_manager.setup_from_config(config, self.yolo)
        else:
            self.azure_manager.setup()

    def set_up_and_take_down(self):
        self.set_config()
    
        if self.azure_manager.check_resource_group_does_not_exist():
            self.azure_manager.create_resource_group()
        elif self.azure_manager.yolo:

            text = Text("YOLO mode is enabled, skipping user input and deleting the existing resource group")

            text.stylize("bright_red", 0, 4)  # YOLO
            text.stylize("bright_green", 5, 9)  # mode
            text.stylize("bright_blue", 10, 17)  # is enabled
            text.stylize("bright_magenta", 18, 26)  # skipping
            text.stylize("bright_cyan", 27, 37)  # user input
            text.stylize("bright_yellow", 38, 42)  # and
            text.stylize("bright_red", 43, 50)  # deleting
            text.stylize("bright_green", 51, 54)  # the
            text.stylize("bright_blue", 55, 63)  # existing
            text.stylize("bright_magenta", 64, 69)  # resource
            text.stylize("bright_cyan", 70, 75)  # group
            panel = Panel(text, title="YOLO Mode", expand=False)
            
            print(panel)
            self.azure_manager.remove_resource_group()
        else:
            responce = input("Do you want to delete the existing resource group? (y/n): ")
            if responce.lower() == 'y':
                Console().print("Deleting the existing resource group")
                self.azure_manager.remove_resource_group()    
            else:
                Console().print("Exiting the program")
        self.write_config()

    def setup(self):
        self.set_config()
    
        if self.azure_manager.check_resource_group_does_not_exist():
            self.azure_manager.create_resource_group()
        self.write_config()

    def takedown(self):
        self.set_config()
        if self.azure_manager.check_resource_group_does_not_exist():
            Console().print("Resource Group does not exist, please run the setup command first", style="magenta")
            return
        elif self.azure_manager.yolo:

            text = Text("YOLO mode is enabled, skipping user input and deleting the existing resource group")

            text.stylize("bright_red", 0, 4)  # YOLO
            text.stylize("bright_green", 5, 9)  # mode
            text.stylize("bright_blue", 10, 17)  # is enabled
            text.stylize("bright_magenta", 18, 26)  # skipping
            text.stylize("bright_cyan", 27, 37)  # user input
            text.stylize("bright_yellow", 38, 42)  # and
            text.stylize("bright_red", 43, 50)  # deleting
            text.stylize("bright_green", 51, 54)  # the
            text.stylize("bright_blue", 55, 63)  # existing
            text.stylize("bright_magenta", 64, 69)  # resource
            text.stylize("bright_cyan", 70, 75)  # group
            panel = Panel(text, title="YOLO Mode", expand=False)
            
            print(panel)
            self.azure_manager.remove_resource_group()
        else:
            responce = input("Do you want to delete the existing resource group? (y/n): ")
            if responce.lower() == 'y':
                Console().print("Deleting the existing resource group")
                self.azure_manager.remove_resource_group()
        self.write_config()


    def write_config(self):
        config = self.azure_manager.to_dict()
        ConfigManager.write_config(config)




class ConfigManager:
    @staticmethod
    def read_config():
        with open('config.json') as json_file:
            return json.load(json_file)
    @staticmethod
    def write_config(config):
        with open('config.json', 'w') as json_file:
            json.dump(config, json_file, indent=4)

if __name__ == "__main__":

    cli = AzureManagerCLI()
    cli.run()
    
   
    



