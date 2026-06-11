from prometheus_client import Gauge, Counter

USERS_CREATED=Counter("users_created", "No. of users created")
EMAILS_SENT=Counter("emails_sent", "Total emails sent")
USERS_LOGIN=Gauge("users_login", "No. of users logged in")
TOTAL_USERS= Gauge("total_users", "total number of users")
TOTAL_REFRESH_TOKENS= Gauge("total_refresh", "total refresh tokens")
