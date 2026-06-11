from prometheus_client import Counter, Gauge
FILE_UPLOADED=Counter("files_uploaded", "Files uploaded")
TOTAL_FILES=Gauge("total_files", "Total files uploaded")
