# Definition of done

Need to automatically deploy an NLP model coming from [HuggingFace](https://huggingface.co/) and find the best option to expose it as a simple API. Additional challenges:

- Overall performance of the API need to be 'real time' - it means it could be used to analyze sentences in a real conversation flow.
- Model is currently unique for all users. Discussion in progress to have perhaps dedicated model per user. Is there a way to have model loaded for a user session.
- The API should manage BOTH tokenization + model prediction/text generation.
- Check if GPU improves the prediction time or not.

## Investigations

### Hosting

**Web App** has been excluded at the moment, there is no GPU support. However, if we consider GPU don't bring any value for inference, it could be a good choice for hosting the solution (simpler to manage than AKS). In addition, we can reuse existing containers on Web App for Containers without too much work.

**ACI** was a good option for quick deployment but is not really scalable. Anyway, it has been excluded after some tests, due to the following limitations:

- CUDA limitation. It was not possible to install last version of tensorflow with CUDA 11. ACI supports only CUDA 9 at this stage
  - [Deploy container instances that use GPU resources](https://docs.microsoft.com/en-us/azure/container-instances/container-instances-gpu)

> Container instances with GPU resources are pre-provisioned with NVIDIA CUDA drivers and container runtimes, so you can use container images developed for CUDA workloads. We support only CUDA 9.0 at this stage.

- Not possible to use a managed identity to pull images from ACR.
  - [How to use managed identities with Azure Container Instances](https://docs.microsoft.com/en-us/azure/container-instances/container-instances-managed-identity)
  
> You can't use a managed identity to pull an image from Azure Container Registry when creating a container group. The identity is only available within a running container.

**AKS** works fine with GPU support. I was able to run jobs and containers with last versions of tensorflow + huggingface. You just need to install a daemonset provided by nvidia.

### Web Application Framework (WSGI) + Web Server

**Flask with Gunicorn** It works fine BUT a new worker is created for each request. And the model is reloaded in memory each time, unfortunately it takes time. I didn't find a solution yet to avoid this issue.
	
**Tensorflow Serving**. It could be the ideal solution, but it hosts only the model. The tokenization should be done by the client.

**FastAPI with Uvicorn** At the moment, the best option. Code really similar to Flask and performance is awesome. In addition, it creates automatically a swagger file. Perfect solution to host a unique model and preload it when server starts. However, if we need to have a dedicated model per user, session seems complex to use with FastApi, additional investigations needed on this point.








