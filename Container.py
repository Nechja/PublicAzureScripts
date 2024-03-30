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
        