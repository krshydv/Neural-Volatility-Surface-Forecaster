# Kubernetes manifests — unverified

These manifests were written to match `docker-compose.yml` service-for-service
(postgres, redis, api, worker, web, plus an nginx ingress) but have **never been
applied to a real cluster** — this and every prior development sandbox had no
Kubernetes control plane available.

Before relying on these:

- Build and push `hermes-forecast/api:latest` and `hermes-forecast/web:latest`
  to a registry the cluster can pull from, and update the `image:` fields
  accordingly (these placeholder names assume a local/dev registry).
- Replace the plaintext secrets in `api.yaml` / `postgres.yaml` with a real
  secrets manager (Sealed Secrets, External Secrets, Vault, etc.) before any
  non-local use.
- `RATE_LIMIT_BACKEND=redis` is set here since the API runs with 2+ replicas —
  this is the multi-replica case the in-memory limiter explicitly does not
  handle correctly.
- Autoscaling (`autoscaling.yaml`: HPA for `api` and `worker` on CPU, PDBs for
  `api` and `web`) and default-deny `NetworkPolicy` rules (`network-policy.yaml`)
  are included now — still unverified against a real cluster, and the
  `NetworkPolicy` resources only take effect if the cluster's CNI actually
  enforces them (not all do by default; e.g. plain kind/minikube may not).
- Apply order: `namespace.yaml`, then `postgres.yaml` and `redis.yaml`, then
  `api.yaml` and `web.yaml`, then `ingress.yaml` (requires an ingress-nginx
  controller already installed in the cluster), then `autoscaling.yaml` and
  `network-policy.yaml` last (the network policies assume the `app` labels
  from the manifests above already exist, and assume an `ingress-nginx`
  namespace with pods labeled `app: ingress-nginx` — adjust the selector to
  match whatever ingress controller is actually installed).
