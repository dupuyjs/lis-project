FROM ubuntu:18.04

ARG BUILD_TERRAFORM_VERSION="1.0.3"
ARG BUILD_TERRAFORM_OS_ARCH=linux_amd64

ENV TERRAFORM_VERSION=${BUILD_TERRAFORM_VERSION}
ENV TERRAFORM_OS_ARCH=${BUILD_TERRAFORM_OS_ARCH}

# Update & Install tool
RUN apt-get update && \ 
    apt-get upgrade -y && \
    apt-get install -y unzip curl git wget

# Install Terraform
RUN curl -Os https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/terraform_${TERRAFORM_VERSION}_${TERRAFORM_OS_ARCH}.zip && \
    unzip -o terraform_${TERRAFORM_VERSION}_${TERRAFORM_OS_ARCH}.zip -d /usr/local/bin

# Install Azure CLI
RUN curl -sL https://aka.ms/InstallAzureCLIDeb | bash

# Install Go language version 1.16.6
RUN cd /usr/local 
RUN wget https://golang.org/dl/go1.16.6.linux-amd64.tar.gz
RUN tar -C /usr/local -xzf go1.16.6.linux-amd64.tar.gz
ENV PATH "$PATH:/usr/local/go/bin"
ENV CGO_ENABLED 0

# Install terraform-docs
RUN GO111MODULE="on" go get github.com/terraform-docs/terraform-docs@v0.14.1
RUN chmod +x /root/go/bin/terraform-docs
ENV PATH "$PATH:/root/go/bin"

# Install Helm
RUN curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3
RUN chmod 700 get_helm.sh
RUN ./get_helm.sh

# Cleanup
RUN rm terraform_${TERRAFORM_VERSION}_${TERRAFORM_OS_ARCH}.zip
RUN rm -rf /ci
RUN rm get_helm.sh

CMD [ "sleep", "infinity" ]