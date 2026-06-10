# Service Level Objectives — Payment Authorization Platform

## SLIs (what we measure)
- **Latency:** time to serve POST /authorize, measured at the service.
- **Availability:** proportion of /authorize requests that return non-5xx.

## SLOs (the targets)
| SLO | Target | Window |
|-----|--------|--------|
| Latency | 99% of /authorize requests complete in < 150ms | rolling 30 days |
| Availability | 99.9% of /authorize requests return non-5xx | rolling 30 days |

## Error budgets
- **Latency:** 1% of requests may exceed 150ms. Over 30 days at ~1M requests,
  that's ~10,000 slow requests before the budget is spent.
- **Availability:** 0.1% may fail. That's ~43 minutes of total downtime over 30 days.

The error budget is the whole point: it's the amount of failure we've agreed is
acceptable. We don't chase 100% - we spend the budget on shipping speed, and only
slow down when we're burning it too fast.