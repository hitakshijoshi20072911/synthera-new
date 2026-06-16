from prometheus_client import Counter, Gauge, Histogram, Summary

TOTAL_SUMMARIZERS=Counter("total_summarizers", "total number of summarized docs")
TOTAL_ASKS=Counter("total_asks", "total number of aqna fired")
