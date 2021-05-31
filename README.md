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

* Two Kubernetes namespaces, from any providers you choose, on any
  clusters you choose

[install-kubectl]: https://kubernetes.io/docs/tasks/tools/install-kubectl/
[install-skupper]: https://skupper.io/start/index.html#step-1-install-the-skupper-command-line-tool-in-your-environment

## Step 1: Set up your namespaces

## Step 2: Link your namespaces

## Step 3: Deploy your services

## Step 4: Expose your services

## Step 5: Test your application