# Dynamic VNF Management in Kubernetes

This repo is a practical example of solution found by me during my thesis work and explained in [this Medium article](https://medium.com/@francesco.valente95/dynamic-vnf-management-in-kubernetes-892f66fbd2e).
Check out the article to get more information about the work.

This project is a consequence of my thesis work made in collaboration with the R&D division of TIM (Italian telco company) 
which is trying to exploit Kubernetes to manage VNF by following a dynamic and declarative approach.
The aim of this project is to demonstrate how the Knative and Krules frameworks can be exploited to automatically
adapt and change the behaviour of a network of VNF, as a result of different events, in a declarative manner, 
instead of the traditional imperative approach.

The network used for this project is the one described in the article. Note that the images used for this project are not an 
implementation of real VNF, but are simple linux images. The LB is implemented by means of Multipath Routing on linux, 
changing the routing table (this is not a load balancer but it's just an example, and the project could be extended to 
manage a real load balancer only with replacement of one function). Instead, the FW is implemented using the UFW configuration tool
for Ubuntu. 

The VNF are connected to each other through the use of the CNI Multus, but any CNI could be used.

## Requirements

- An up and running **Kubernetes cluster**. I used a local minikube installation. My advice is to install Kubernetes 
  using the following command, in order to use the same version I used and simplify the installation of Multus.
  ```
  minikube start --kubernetes-version=1.17.1 --cpus=2 --memory=4096 --cni flannel
  ```
- **Multus** installed on the Kubernetes cluster. If we have installed Kubernetes using the previous command multus 
  can be easly installed using the following command:
  ```
  kubectl create -f https://raw.githubusercontent.com/intel/multus-cni/master/images/multus-daemonset.yml
  ```
- A **Knative** updated version working installation (including serving and eventing). You can 
follow [the official Knative installation guide](https://knative.dev/v0.19-docs/install/any-kubernetes-cluster/) 
or opt for a simpler installation using [Mink](https://github.com/mattmoor/mink). In case you choose the official installation,
  as I did too, remember to install Istio as networking layer.  
- In order to configure a subjects storage provider, you need at least a **Redis** or a **MongoDB** database;
- A working **Docker** installation and a registry accessible from the cluster to push your images to. 
This is needed in order to build and publish your rulesets.

## Deploy the VNFs on Kubernetes

In the {PROJECT_DIR}/base/k8s/use-case directory you will find the NetworkAttachmentDefinitions used by Multus
to setup the network attachments and the Deployments of the VNF (client, LB, FW and Server).

Firstly create the three NetworkAttachmentDefinitions that represent the three networks configuration between the four VNF: 
`cl-lb-multus-def.yaml`, `lb-fw-multus-def.yaml`, `fw-sv-multus-def.yaml`.

Secondly create the four VNF: `client.yaml`, `firewall-ufw.yaml`, `multipath-outgoing.yaml`, `server.yaml`.

Note that the VNF at this moment cannot communicate, because they are in different networks and cannot reach each
other until you will configure the routing table in a correct way.

## Install KRules base system

Once all previously mentioned requirements are satisfied you can proceed with the installation of KRules base 
system running:

```
$ kubectl apply -f https://github.com/airspot-dev/krules-controllers/releases/download/v0.8.1/release.yaml
```

:warning: **WARNING**: Ensure that all pods are in a `Running` status and all container are `READY` before run the previous command. If you have installed
Knative in a standard way you can check pods status in **knative-eventing** and **knative-serving** namespaces. While if you had chose to use Mink 
check **mink-system** namespace.

This command will install various kinds of stuff in the `krules-system`  namespace.
Most of them are Knative services able to scale to zero, so if you want to check the installation status run the 
following command:

```
$ kubectl -n krules-system get ksvc
```

Wait until all the service show a status `READY` equal to `True`.
