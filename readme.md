# Azure Resource Management Scripts

I've taken some of the cool stuff I've built (or played with) for managing Microsoft Azure with Python, cleaned them up, and now I’m throwing them out into the wild for all of you.🎉🎉🎉

## Features

- Authentication using Azure CLI credentials.
- Listing available Azure subscriptions.
- Selection of Azure subscriptions for operations.
- Creation and deletion of Azure resource groups with specified names and locations.
- Verifies the non-existence of resource groups before creation to avoid conflicts.
- YOLO mode for bypassing confirmation steps in resource management operations.
- Configurable through a JSON file for automated setups.

## Prerequisites

Before you begin, ensure you have met the following requirements:

- Python 3.12
- Azure CLI installed and configured with `az login`.
- Installation of required Python libraries: `azure-identity`, `azure-mgmt-resource`, and `rich`.

You can install the necessary Python libraries using pip:

```bash
pip install azure-identity azure-mgmt-resource rich

```

## Usage
Clone the repository or download the script to your local machine.
Ensure you have configured the config.json file as per your requirements.
Run the script using Python:
```bash
python ResourceGroup.py
```
## ResourceGroup.py Command Line Arguments

### --setup
This command is used to set up resources. When this argument is passed, the script will initiate the process of setting up resources.

### --takedown
This command is used to take down resources. When this argument is passed, the script will initiate the process of taking down resources.

### --setup-takedown
This command is used to manage resources. When this argument is passed, the script will check the status of the resource. If the resource is not up, it will set it up. If the resource is up, it will take it down.

### --yolo
This command is used to run the script in YOLO mode. When this argument is passed, the script will skip user input and execute the scripts.

### --no-config
This command is used to run the script without using the config file. When this argument is passed, the script will not use the config file for its operations.

Follow the on-screen prompts to authenticate, select subscriptions, and manage resource groups.
