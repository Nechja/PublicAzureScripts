import json

class ConfigManager:
    def __init__(self, config_file):
        self.config_directory = 'config/'
        self.config_file = f"{self.config_directory}{config_file}"


    def read_config(self):
        with open(self.config_file) as json_file:
            return json.load(json_file)
    def write_config(self,config):
        with open(self.config_file, 'w') as json_file:
            json.dump(config, json_file, indent=4)