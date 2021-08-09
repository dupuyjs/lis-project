# LIS Project

## Installation Steps
### Prerequisites

Azure cloud resources are deployed using [terraform >= 1.0.3](https://www.terraform.io/) and [Azure CLI >= 2.26.1](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli). 

We recommend to use the .devcontainer included within this solution when running Visual Studio Code, it contains all the tools needed to deploy this infrastucture. At least, you can use the installation steps in the [Dockerfile](./.devcontainer/Dockerfile) to install manually prerequisite tools.

If you never used a dev container, please check the reference [Developing inside a Container](https://code.visualstudio.com/docs/remote/containers).

### Architecture
Terraform will deploy the following cloud infrastructure: 

- An Azure Container Registry (ACR) to store docker images.
- An Azure Kubernetes Service (AKS) to host containers and expose API.
- An Azure Key Vault to store secrets.

In addition:
- We assign AKS kubelet_identity with `acrpull` role to pull images from registry.
- Secrets get, set, list permissions are assigned for current user when creating the key vault.

### Steps
Login with Azure CLI.
``` bash
root@1c54ba24e25c:/workspaces/lis-project# az login
```
Ensure your default account is the correct one.
``` bash
root@1c54ba24e25c:/workspaces/lis-project# az account show
```
Initialize terraform.
``` bash
root@1c54ba24e25c:/workspaces/lis-project# cd infra
root@1c54ba24e25c:/workspaces/lis-project/infra# terraform init

Initializing the backend...

Initializing provider plugins...
- Reusing previous version of hashicorp/azurerm from the dependency lock file
- Reusing previous version of hashicorp/random from the dependency lock file
- Using previously-installed hashicorp/azurerm v2.69.0
- Using previously-installed hashicorp/random v3.1.0

Terraform has been successfully initialized!
```
Apply changes to deploy resources. Just type 'yes'.
``` bash
root@1c54ba24e25c:/workspaces/lis-project/infra# terraform apply

(...)
Plan: 9 to add, 0 to change, 0 to destroy.

Changes to Outputs:
  + acr_login_server = (known after apply)
  + key_vault_name   = (known after apply)

Do you want to perform these actions?
  Terraform will perform the actions described above.
  Only 'yes' will be accepted to approve.

  Enter a value: yes
```
``` bash
Apply complete! Resources: 9 added, 0 changed, 0 destroyed.

Outputs:

acr_login_server = "lis<prefix>acr.azurecr.io"
aks_name = "lis<prefix>aks"
key_vault_name = "lis<prefix>kv"
resource_group_name = "lis<prefix>-dev-rg"
```

### GPU Support
Install kubectl.
``` bash
root@1c54ba24e25c:/workspaces/lis-project/infra# az aks install-cli
```
Get the access credentials for AKS and merge them into the kubeconfig file. Change resource-group and name using information returned by terraform.
``` bash
root@1c54ba24e25c:/workspaces/lis-project/infra# az aks get-credentials --resource-group lis<prefix>-dev-rg --name lis<prefix>aks
Merged "lis791anaks" as current context in /root/.kube/config
```
Check you have 1 node.
``` bash
root@1c54ba24e25c:/workspaces/lis-project/infra# kubectl get nodes
NAME                              STATUS   ROLES   AGE     VERSION
aks-default-31759975-vmss000000   Ready    agent   3h23m   v1.20.7
```
Describe the node to access capacity information. 6 CPUs are available but no GPU. Provide the name for your own node.
``` bash
root@1c54ba24e25c:/workspaces/lis-project/infra# kubectl describe node aks-default-31759975-vmss000000
(...)
Capacity:
  attachable-volumes-azure-disk:  24
  cpu:                            6
  ephemeral-storage:              129900528Ki
  hugepages-1Gi:                  0
  hugepages-2Mi:                  0
  memory:                         57584828Ki
  pods:                           110
(...)
```

Add k8s-device-plugin to helm repo.
``` bash
root@1c54ba24e25c:/workspaces/lis-project/infra# helm repo add nvdp https://nvidia.github.io/k8s-device-plugin
"nvdp" has been added to your repositories
```
Update helm repo.
``` bash
root@1c54ba24e25c:/workspaces/lis-project/infra# helm repo update
Hang tight while we grab the latest from your chart repositories...
...Successfully got an update from the "nvdp" chart repository
Update Complete. ⎈Happy Helming!⎈
```
Install nvidia-device-plugin.
``` bash
root@1c54ba24e25c:/workspaces/lis-project/infra# helm install nvdp/nvidia-device-plugin --version=0.9.0 --generate-name --set migStrategy=mixed
NAME: nvidia-device-plugin-1628514017
LAST DEPLOYED: Mon Aug  9 13:00:20 2021
NAMESPACE: default
STATUS: deployed
REVISION: 1
TEST SUITE: None
```
Describe the node again. nvidia.com/gpu should be listed.
``` bash
root@1c54ba24e25c:/workspaces/lis-project/infra# kubectl describe node aks-default-31759975-vmss000000
(...)
Capacity:
  attachable-volumes-azure-disk:  24
  cpu:                            6
  ephemeral-storage:              129900528Ki
  hugepages-1Gi:                  0
  hugepages-2Mi:                  0
  memory:                         57584828Ki
  nvidia.com/gpu:                 1
  pods:                           110
(...)
```

For additional information, you can check the following resources: 
- [NVIDIA device plugin for Kubernetes](https://github.com/NVIDIA/k8s-device-plugin)
- [Use GPUs for compute-intensive workloads on Azure Kubernetes Service (AKS)](https://docs.microsoft.com/en-us/azure/aks/gpu-cluster)

(Optional) Run a GPU-enabled workload

Use the `kubectl apply` command to run the job. 

``` bash
root@1c54ba24e25c:/workspaces/lis-project/infra# cd test 
root@1c54ba24e25c:/workspaces/lis-project/infra/test# kubectl apply -f samples-tf-mnist-demo.yaml
job.batch/samples-tf-mnist-demo created
```

To look at the output of the GPU-enabled workload, first get the name of the pod with the kubectl get pods command:
``` bash
root@1c54ba24e25c:/workspaces/lis-project/infra/test# kubectl get pods --selector app=samples-tf-mnist-demo
NAME                          READY   STATUS      RESTARTS   AGE
samples-tf-mnist-demo-gvxkt   0/1     Completed   0          3m34s
```

Now use the `kubectl logs` command to view the pod logs. Tesla K80 has been correctly discovered.
``` bash
root@1c54ba24e25c:/workspaces/lis-project/infra/test# kubectl logs samples-tf-mnist-demo-gvxkt

(...)
2021-08-09 14:18:44.715494: I tensorflow/core/common_runtime/gpu/gpu_device.cc:1030] Found device 0 with properties: 
name: Tesla K80 major: 3 minor: 7 memoryClockRate(GHz): 0.8235
pciBusID: 0001:00:00.0
totalMemory: 11.17GiB freeMemory: 11.11GiB
(...)
```