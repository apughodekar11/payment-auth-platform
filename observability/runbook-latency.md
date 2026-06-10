# Runbook: /authorize p99 latency alert

Triggered when the latency error budget is burning fast (see burn-rate alert).

## 1. Confirm
- Dynatrace > Services > payment-auth: is p99 actually elevated, or a single spike?
- Check the time it started - does it line up with a recent deploy?

## 2. Triage (most likely first)
- **Recent deploy?** `kubectl rollout history deployment/payment-auth`.
  If latency rose right after a deploy, that's the suspect.
- **Redis slow/unreachable?** Velocity check is on the hot path. Check the redis
  pod, and the readiness probe status of app pods.
- **Postgres slow?** Every decision writes a row. Check DB pod / connection pool.
- **Pods CPU-throttled?** `kubectl top pods`. If at CPU limit, the HPA should be
  scaling - check `kubectl get hpa`. If it's not scaling, that's the problem.

## 3. Mitigate
- Deploy-related: `kubectl rollout undo deployment/payment-auth`.
- Capacity-related: bump HPA max or pod CPU limits.
- Dependency down: failover / restart the dependency.

## 4. Verify
- Watch p99 in Dynatrace return under 150ms. Confirm decline rate normal.

## 5. Close
- Note root cause. If it'll recur, file a follow-up (e.g. add caching, sliding-window
  velocity, connection pool tuning).