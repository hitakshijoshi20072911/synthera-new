from prometheus_client import Counter, Histogram
REQUEST_COUNT= Counter("agent_requests_total", "Total requests to /agent-run endpoint", ["status"])
REQUEST_LATENCY = Histogram("agent_request_latency_seconds", "Latency of /agent-run endpoint" , buckets=(0.1, 0.3, 0.5, 1, 2, 4, 6, 8, 10, 15 ))
CACHE_HITS = Counter("agent_cache_hits_total", "Total cache hits")
CACHE_MISSES = Counter("agent_cache_misses_total", "Total cache misses")
ERROR_COUNT = Counter("agent_errors_total", "Total agent errors")
