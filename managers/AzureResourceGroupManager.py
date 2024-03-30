from config import ConfigManager as cm
from azure.core.exceptions import ResourceNotFoundError
from azure.identity import AzureCliCredential
from azure.mgmt.resource import ResourceManagementClient, SubscriptionClient
from rich.console import Console
from rich.progress import BarColumn, Progress, TextColumn
from rich.table import Table


import time


class ResourceGroupManager:
    def __init__(self):
        self.console = Console()
        self.credential = None
        self.subscription_client = None
        self.subscriptions = None
        self.subscription = None
        self.resource_group_name = None
        self.resource_group_location = None
        self.yolo = False


    def __defaults(self):
        try:
            config = cm("defaults.config.json")
        except Exception as e:
            Console().print("Failed to read defaults.config.json", style="bold red")
            Console().print(e, style="red")
        try:
            self.resource_group_name = config.read_config()["default_resource_group_name"]
            self.resource_group_location = config.read_config()["default_location"]
        except Exception as e:
            Console().print("Failed to read defaults from defaults.config.json", style="bold red")
            Console().print(e, style="red")

    def to_dict(self):
        return {
            "subscription.id": self.subscription.id,
            "resource_group_name": self.resource_group_name,
            "resource_group_location": self.resource_group_location,
            "yolo": self.yolo
        }


    def setup(self):
        self.__defaults()
        self.authenticate()
        self.print_subscriptions()
        self.subscription = self.get_subscription()
        self.print_subscription()

    def setup_from_config(self, config, yolo=None):
        self.__defaults()
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