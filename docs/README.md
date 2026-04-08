# API Gateway Documentation

## Overview

The API Gateway serves as the single entry point for all client requests to the platform's microservices. It handles routing, rate limiting, authentication, and request transformation.

## Architecture

```
Client → API Gateway → Service Mesh → Microservices
```

## Features

- **Request Routing**: Dynamic routing to backend services based on path, headers, and query parameters.
- **Rate Limiting**: Configurable per-client and per-endpoint rate limiting to protect backend services.
- **Authentication & Authorization**: JWT validation, API key verification, and OAuth2 token introspection.
- **Request/Response Transformation**: Header manipulation, payload transformation, and protocol translation.
- **Circuit Breaking**: Automatic circuit breaking to prevent cascading failures.
- **Logging & Metrics**: Structured request logging with latency tracking and error rate monitoring.
- **Caching**: Response caching with configurable TTL for GET endpoints.

## Configuration

The gateway is configured via environment variables and a YAML configuration file. See [`config/`](./config/) for examples.

### Key Environment Variables

| Variable | Description | Default |
|---|---|---|
| `GATEWAY_PORT` | Listening port | `8080` |
| `LOG_LEVEL` | Logging verbosity (`debug`, `info`, `warn`, `error`) | `info` |
| `RATE_LIMIT_RPM` | Default rate limit (requests per minute) | `1000` |
| `UPSTREAM_TIMEOUT_MS` | Upstream request timeout in milliseconds | `5000` |
| `ENABLE_CACHING` | Enable response caching (`true`/`false`) | `false` |

## Health Check

- **Liveness**: `GET /healthz` — Returns `200 OK` when the gateway process is running.
- **Readiness**: `GET /readyz` — Returns `200 OK` when the gateway can accept traffic (dependencies reachable).

## Deployment

The API Gateway is deployed as a Kubernetes Deployment behind a LoadBalancer Service. See the `k8s/` directory for manifests.

### Rolling Update Strategy

- Max unavailable: `25%`
- Max surge: `25%`
- Readiness gate on `/readyz`

## Monitoring & Alerts

- Dashboards are available in Grafana under the **API Gateway** folder.
- Alerts are configured for:
  - High error rate (>1% 5xx responses over 5 minutes)
  - Elevated latency (p99 > 2s over 5 minutes)
  - Upstream connection failures

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines on submitting changes.

## Contacts

- **Platform Team**: #platform-engineering on Slack
- **On-Call**: See PagerDuty schedule `api-gateway-oncall`
