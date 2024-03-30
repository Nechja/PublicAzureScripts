import json
import argparse
from managers import ResourceGroupManager
from config import ConfigManager as cm
from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich import print



class AzureManagerCLI:
    def __init__(self):
        self.azure_manager = ResourceGroupManager()
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
        self.azure_manager = ResourceGroupManager()
        self.config_manager = cm("resourceGroup.config.json")
        self.yolo = False
        self.useconfig = True

    def set_yolo(self, yolo):
        self.azure_manager.yolo = yolo
        self.yolo = yolo

    def set_config(self):
        try:
            config = self.config_manager.read_config()
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
        self.config_manager.write_config(config)





if __name__ == "__main__":

    cli = AzureManagerCLI()
    cli.run()
    
   
    



