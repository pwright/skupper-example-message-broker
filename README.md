# Skupper Hello World

A minimal HTTP application deployed across Kubernetes clusters using [Skupper](https://skupper.io/)

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

This example is a very simple multi-service HTTP application that can
be deployed across multiple Kubernetes clusters using Skupper.

It contains two services:

* A backend service that exposes an `/api/hello` endpoint.  It
  returns greetings of the form `Hello from <pod-name>
  (<request-count>)`.

* A frontend service that accepts HTTP requests, calls the backend
  to fetch new greetings, and serves them to the user.

With Skupper, you can place the backend in one cluster and the
frontend in another and maintain connectivity between the two
services without exposing the backend to the public internet.

<img src="images/entities.svg" width="640"/>

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

Console for west:

~~~ shell
export KUBECONFIG=~/.kube/config-west
~~~

Console for east:

~~~ shell
export KUBECONFIG=~/.kube/config-east
~~~

## Step 2: Log in to your clusters

*Specific to your cloud provider*

## Step 3: Create your namespaces

Console for west:

~~~ shell
kubectl create namespace west
kubectl config set-context --current --namespace west
~~~

Console for east:

~~~ shell
kubectl create namespace east
kubectl config set-context --current --namespace east
~~~

## Step 4: Install Skupper in your namespaces

Console for west:

~~~ shell
skupper init
~~~

Console for east:

~~~ shell
skupper init --ingress none
~~~

## Step 5: Link your namespaces

Console for west:

~~~ shell
skupper token create ~/west.token
~~~

Console for east:

~~~ shell
skupper link create ~/west.token
skupper link status --wait 30
~~~

## Step 6: Deploy your services

Console for west:

~~~ shell
kubectl create deployment hello-world-frontend --image quay.io/skupper/hello-world-frontend
~~~

Console for east:

~~~ shell
kubectl create deployment hello-world-backend --image quay.io/skupper/hello-world-backend
~~~

## Step 7: Expose your services

Console for west:

~~~ shell
kubectl expose deployment/hello-world-frontend --port 8080 --type LoadBalancer
~~~

Console for east:

~~~ shell
skupper expose deployment/hello-world-backend --port 8080
~~~

## Step 8: Test your application

Console for west:

~~~ shell
curl $(kubectl get service hello-world-frontend -o jsonpath='http://{.status.loadBalancer.ingress[0].ip}:8080/')
~~~