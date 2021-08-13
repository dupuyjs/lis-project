# Workflow

Once the infrastructure deployed, you can run github workflow [model-deployment.yml](../.github/workflows/model-deployment.yml). It automates the following deployment steps:

- Get secrets from key vault
- Build the Dockerfile image
- Push the image on the container registry
- Substitute image name on deployment file.
- Apply deployment and service files on Kubernetes

## Prerequisites

However, you need some prerequisites steps before to run this workflow:

### Service Principal for Github

Use the [az ad sp create-for-rbac](https://docs.microsoft.com/cli/azure/ad/sp?view=azure-cli-latest#az_ad_sp_create_for_rbac) command to create a service principal.

``` bash
az ad sp create-for-rbac --name "{sp-name}" --sdk-auth
```
This service principal will be used by github to login on your subscription. The previous command creates a service principal and assign a contributor role on your subscription. If you prefer, you can restrict the scope to target only the resource group you created with terraform.

``` bash
az ad sp create-for-rbac --name "{sp-name}" --sdk-auth --role contributor --scopes /subscriptions/{subscription-id}/resourceGroups/{resource-group}
```
When complete, the `az ad sp create-for-rbac` command displays JSON output in the following form (which is specified by the --sdk-auth argument):

```json
{
  "clientId": "<GUID>",
  "clientSecret": "<GUID>",
  "subscriptionId": "<GUID>",
  "tenantId": "<GUID>",
  (...)
}
```

In your repository, use Add secret to create a new secret named `AZURE_CREDENTIALS`. Paste the entire JSON object produced by the az ad sp create-for-rbac command as the secret value and save the secret.

*Note from the documentation:*

While adding secret AZURE_CREDENTIALS make sure to add like this

     {"clientId": "<GUID>",
      "clientSecret": "<GUID>",
      "subscriptionId": "<GUID>",
      "tenantId": "<GUID>",
      (...)}

instead of

    {
        "clientId": "<GUID>",
        "clientSecret": "<GUID>",
        "subscriptionId": "<GUID>",
        "tenantId": "<GUID>",
        (...)
    }
to prevent unnecessary masking of { } in your logs which are in dictionary form.

### Key Vault

In your repository, use Add secret to create a new secret named `KEYVAULT_NAME`. 

Copy the name of your key vault instance (this information is returned bu terraform outputs).

In addition, add the service principal created before in the key vault policies to access `secrets` with `get` and `list` permissions.

And now, you are fine to run the workflow.
