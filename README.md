# Accessing a message broker using Skupper

Use [Skupper](https://skupper.io/) to consume from a job queue in a private datacenter

* [Overview](#overview)
* [Prerequisites](#prerequisites)
* [Step 1: Configure separate kubeconfigs](#step-1-configure-separate-kubeconfigs)
* [Step 2: Log in to your clusters](#step-2-log-in-to-your-clusters)
* [Step 3: Create your namespaces](#step-3-create-your-namespaces)
* [Step 4: Install Skupper in your namespaces](#step-4-install-skupper-in-your-namespaces)
* [Step 5: Link your namespaces](#step-5-link-your-namespaces)
* [Step 6: Deploy your services](#step-6-deploy-your-services)
* [Step 7: Expose your services](#step-7-expose-your-services)
* [Step 8: Test your application](#step-8-test-your-application)

## Overview

This example is a multi-service messaging application that can
be deployed across multiple Kubernetes clusters using Skupper.

It contains three services:

* A message broker running in a private data center

* A job processor running in the public cloud

* A job requstor, running in the private data center, that serves a
  REST API for submitting jobs

## Prerequisites

* The `kubectl` command-line tool, version 1.15 or later
  ([installation guide][install-kubectl])

* The `skupper` command-line tool, the latest version ([installation
  guide][install-skupper])

* Access to two Kubernetes namespaces, from any providers you
  choose, on any clusters you choose

[install-kubectl]: https://kubernetes.io/docs/tasks/tools/install-kubectl/
[install-skupper]: https://skupper.io/start/index.html#step-1-install-the-skupper-command-line-tool-in-your-environment

## Step 1: Configure separate kubeconfigs

Since we are dealing with two namespaces, we need to set up
isolated `kubectl` configurations, one for each namespace.  In
this example, we will use distinct kubeconfigs on separate
consoles.

Console for cloud:

~~~ shell
export KUBECONFIG=~/.kube/config-cloud
~~~

Console for datacenter:

~~~ shell
export KUBECONFIG=~/.kube/config-datacenter
~~~

## Step 2: Log in to your clusters

*Specific to your cloud provider*

## Step 3: Create your namespaces

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

Console for cloud:

~~~ shell
skupper init
~~~

Console for datacenter:

~~~ shell
skupper init --ingress none
~~~

## Step 5: Link your namespaces

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