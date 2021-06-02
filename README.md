# Accessing a message broker using Skupper

Use [Skupper](https://skupper.io/) to consume from a job queue in a
private datacenter and process jobs in the public cloud

* [Overview](#overview)
* [Prerequisites](#prerequisites)
* [Step 1: Configure separate console sessions](#step-1-configure-separate-console-sessions)
* [Step 2: Log in to your clusters](#step-2-log-in-to-your-clusters)
* [Step 3: Set the current namespaces](#step-3-set-the-current-namespaces)
* [Step 4: Install Skupper in your namespaces](#step-4-install-skupper-in-your-namespaces)
* [Step 5: Link your namespaces](#step-5-link-your-namespaces)
* [Step 6: Deploy your services](#step-6-deploy-your-services)
* [Step 7: Expose your services](#step-7-expose-your-services)
* [Step 8: Test your application](#step-8-test-your-application)

## Overview

This example is a multi-service messaging application that can
be deployed across multiple Kubernetes clusters using Skupper.

It contains three services:

* A message broker running in a private data center.  The broker has
  a queue named "jobs" and a topic named "notifications".

* A job requestor running in the private data center.  It serves a
  REST API for submitting jobs to the job queue and getting results
  from the notifications topic.

* A job processor running in the public cloud.  It consumes from the
  job queue, does some work, and publishes the result to the
  notifications topic.

## Prerequisites

* The `kubectl` command-line tool, version 1.15 or later
  ([installation guide][install-kubectl])

* The `skupper` command-line tool, the latest version ([installation
  guide][install-skupper])

* Access to two Kubernetes namespaces, from any providers you
  choose, on any clusters you choose

[install-kubectl]: https://kubernetes.io/docs/tasks/tools/install-kubectl/
[install-skupper]: https://skupper.io/start/index.html#step-1-install-the-skupper-command-line-tool-in-your-environment

## Step 1: Configure separate console sessions

Skupper is designed for use with multiple namespaces, typically on
different clusters.  The `skupper` command uses your
[kubeconfig][kubeconfig] and current context to select the namespace
where it operates.

[kubeconfig]: https://kubernetes.io/docs/concepts/configuration/organize-cluster-access-kubeconfig/

Your kubeconfig is stored in a file in your home directory.  The
`skupper` and `kubectl` commands use the `KUBECONFIG` environment
variable to locate it.

A single kubeconfig supports only one active context per user.
Since you will be using multiple contexts at once in this
exercise, you need to create distinct kubeconfigs.

Start a console session for each of your namespaces.  Set the
`KUBECONFIG` environment variable to a different path in each
session.

Console for cloud:

~~~ shell
export KUBECONFIG=~/.kube/config-cloud
~~~

Console for datacenter:

~~~ shell
export KUBECONFIG=~/.kube/config-datacenter
~~~

## Step 2: Log in to your clusters

The methods for logging in vary by Kubernetes provider.  Find
the instructions for your chosen providers and use them to
authenticate and establish access for each console session.  See
the following links for more information:

* [Minikube](https://skupper.io/start/minikube.html#logging-in)
* [Amazon Elastic Kubernetes Service (EKS)](https://docs.aws.amazon.com/eks/latest/userguide/create-kubeconfig.html)
* [Azure Kubernetes Service (AKS)](https://docs.microsoft.com/en-us/azure/aks/kubernetes-walkthrough#connect-to-the-cluster)
* [Google Kubernetes Engine (GKE)](https://skupper.io/start/gke.html#logging-in)
* [IBM Kubernetes Service](https://skupper.io/start/ibmks.html#logging-in)
* [OpenShift](https://skupper.io/start/openshift.html#logging-in)

## Step 3: Set the current namespaces

Use `kubectl create namespace` to create the namespaces you wish
to use (or use existing namespaces).  Use `kubectl config
set-context` to set the current namespace for each session.

Console for cloud:

~~~ shell
kubectl create namespace cloud
kubectl config set-context --current --namespace cloud
~~~

Console for datacenter:

~~~ shell
kubectl create namespace datacenter
kubectl config set-context --current --namespace datacenter
~~~

## Step 4: Install Skupper in your namespaces

The `skupper init` command installs the Skupper router and
service controller in the current namespace.  Run the `skupper
init` command in each namespace.

[minikube-tunnel]: https://skupper.io/start/minikube.html#running-minikube-tunnel

**Note:** If you are using Minikube, [you need to start
`minikube tunnel`][minikube-tunnel] before you install Skupper.

Console for cloud:

~~~ shell
skupper init
~~~

Console for datacenter:

~~~ shell
skupper init --ingress none
~~~

## Step 5: Link your namespaces

Creating a link requires use of two `skupper` commands in
conjunction, `skupper token create` and
`skupper link create`.

The `skupper token create` command generates a secret token that
signifies permission to create a link.  The token also carries
the link details.  The `skupper link create` command then uses
the link token to create a link to the namespace that generated
it.

**Note:** The link token is truly a *secret*.  Anyone who has
the token can link to your namespace.  Make sure that only those
you trust have access to it.

Console for cloud:

~~~ shell
skupper token create ~/cloud.token
~~~

Console for datacenter:

~~~ shell
skupper link create ~/cloud.token
skupper link status --wait 30
~~~

## Step 6: Deploy your services

Console for cloud:

~~~ shell
kubectl create deployment job-processor --image quay.io/skupper/job-processor
~~~

Console for datacenter:

~~~ shell
kubectl apply -f message-broker.yaml
kubectl create deployment job-requestor --image quay.io/skupper/job-requestor
~~~

## Step 7: Expose your services

Console for datacenter:

~~~ shell
skupper expose deployment/message-broker --port 5672
kubectl expose deployment/job-requestor --port 8080 --type LoadBalancer
~~~

## Step 8: Test your application

Console for datacenter:

~~~ shell
curl -X POST $(kubectl get service/job-requestor -o jsonpath='http://{.status.loadBalancer.ingress[0].ip}:8080/send-request')
~~~