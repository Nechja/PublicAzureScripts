from azure.identity import AzureCliCredential

class ICredentialProvider:
    def get_credential(self):
        pass

class AzureCliCredentialProvider(ICredentialProvider):
    def get_credential(self):
        return AzureCliCredential()