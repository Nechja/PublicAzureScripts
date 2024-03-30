import unittest
from unittest.mock import Mock, patch
from managers import ResourceGroupManager

class TestResourceGroupManager(unittest.TestCase):
    def setUp(self):

        self.mock_credential_provider = Mock()
        self.mock_console = Mock()
        self.rgm = ResourceGroupManager(icreds=self.mock_credential_provider, console=self.mock_console)

    @patch('managers.AzureResourceGroupManager.ResourceGroupManager')  # Adjust the patch decorator to match your import paths
    def test_authenticate_success(self, mock_azure_cli_credential):
        self.mock_credential_provider.get_credential.return_value = mock_azure_cli_credential
        self.rgm.authenticate()
        self.mock_credential_provider.get_credential.assert_called_once()
        self.mock_console.print.assert_called_with("[green]Authenticated[/] using [cyan]Azure CLI[/] credentials")

    def test_authenticate_failure(self):
        self.mock_credential_provider.get_credential.side_effect = Exception("Authentication failed")
        self.rgm.authenticate()
        self.mock_credential_provider.get_credential.assert_called_once()
        self.mock_console.print.assert_any_call("Failed to authenticate using Azure CLI credentials", style="bold red")

if __name__ == '__main__':
    unittest.main()
