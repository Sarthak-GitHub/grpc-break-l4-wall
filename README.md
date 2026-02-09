# gRPC Smart Discovery: Breaking the L4 Wall

This repository demonstrates how to implement **Client-Side Load Balancing** and **gRPC Health Checking** in Python. It solves the "Sticky Connection" problem common in Kubernetes and high-scale distributed systems.

## The Problem

By default, gRPC uses persistent HTTP/2 connections. Traditional Layer 4 load balancers (like Kubernetes ClusterIP) only balance the *connection*, not the individual *requests*. This leads to "Connection Pinning," where one backend pod handles 100% of the traffic while others sit idle.

## The Solution

This project implements a **"Thick Client"** pattern using:

1. **Headless Service Discovery:** Using the `dns:///` resolver to find all backend endpoints.
2. **Round-Robin Balancing:** Distributing RPC calls across all discovered subchannels.
3. **Active Health Checks:** Using the gRPC Health Checking Protocol to automatically prune unhealthy pods from the client's rotation.

---

## Project Structure

```text
.
├── protos/             # Protobuf definitions
├── server/             # Python gRPC Server with Health Servicer
├── client/             # Python gRPC Client with Load Balancing Config
└── docker-compose.yml  # Local orchestration mimicking K8s behavior

```

## Getting Started

### 1. Prerequisites

* Docker and Docker Compose
* Python 3.9+ (if running locally)

### 2. Generate Stubs

If you make changes to the `.proto` file, regenerate the Python code:

```bash
# From the root directory
python -m grpc_tools.protoc -I./protos --python_out=./server --grpc_python_out=./server ./protos/service.proto
python -m grpc_tools.protoc -I./protos --python_out=./client --grpc_python_out=./client ./protos/service.proto

```

### 3. Run the Demo

Use Docker Compose to spin up 3 server replicas and 1 client:

```bash
docker-compose up --build --scale server=3

```

## What to Watch For

Observe the client logs. You will see the `server_id` rotating between different pods (e.g., `Pod-A`, `Pod-B`, `Pod-C`) for every single request, proving that the **L4 Wall** has been shattered.

```text
client_1  | Request 1: Handled by Pod-abc123
client_1  | Request 2: Handled by Pod-def456
client_1  | Request 3: Handled by Pod-ghi789

```

---

## Key Configurations

### The Service Config (The "Brain")

Inside `client/main.py`, we inject a JSON service config. This is the secret sauce that enables the internal load balancer:

```python
SERVICE_CONFIG = '''{
    "loadBalancingConfig": [ { "round_robin": {} } ],
    "healthCheckConfig": { "serviceName": "" }
}'''

```

### Graceful Churn

The server is configured with `grpc.max_connection_age_ms`. This ensures that connections are periodically recycled, allowing the client to re-resolve DNS and discover newly deployed pods.

---
