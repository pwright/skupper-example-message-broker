# Skupper Hello World

A minimal HTTP application deployed across Kubernetes clusters using [Skupper](https://skupper.io/)

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

<div class='console-label'>Console for west</div>

```shell
export KUBECONFIG=~/.kube/config-west
```

<div class='console-label'>Console for east</div>

```shell
export KUBECONFIG=~/.kube/config-east
```

## Step 2: Log in to your clusters

*Specific to your cloud provider*

## Step 3: Create your namespaces

<div class='console-label'>Console for west</div>

```shell
kubectl create namespace west
kubectl config set-context --current --namespace west
```

<div class='console-label'>Console for east</div>

```shell
kubectl create namespace east
kubectl config set-context --current --namespace east
```

## Step 4: Install Skupper in your namespaces

<div class='console-label'>Console for west</div>

```shell
skupper init
```

<div class='console-label'>Console for east</div>

```shell
skupper init --ingress none
```

## Step 5: Link your namespaces

<div class='console-label'>Console for west</div>

```shell
skupper token create ~/west.token
```

<div class='console-label'>Console for east</div>

```shell
skupper link create ~/west.token
skupper link status --wait 30
```

## Step 6: Deploy your services

<div class='console-label'>Console for west</div>

```shell
kubectl create deployment hello-world-frontend --image quay.io/skupper/hello-world-frontend
```

<div class='console-label'>Console for east</div>

```shell
kubectl create deployment hello-world-backend --image quay.io/skupper/hello-world-backend
```

## Step 7: Expose your services

<div class='console-label'>Console for west</div>

```shell
kubectl expose deployment/hello-world-frontend --port 8080 --type LoadBalancer
```

<div class='console-label'>Console for east</div>

```shell
skupper expose deployment/hello-world-backend --port 8080
```

## Step 8: Test your application

<div class='console-label'>Console for west</div>

```shell
curl $(kubectl get service hello-world-frontend -o jsonpath='http://{.status.loadBalancer.ingress[0].ip}:8080/')
```

    <style>
      div.console-label {
        margin-bottom: 0;
        font-size: 0.7em;
        text-transform: uppercase;
        padding: 0.2em 0.6em 0 0.6em;
        border-bottom: 0.1em solid gray;
      }
    </style>
    