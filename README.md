# synthera-new
Perfect — below is a **proper, detailed, production-grade README “System Architecture” section** that you can **directly paste** into your README.md.
It is written in **clear technical language**, suitable for **evaluators, recruiters, open-source users, or investors**.

# System Architecture
<img width="1030" height="320" alt="image" src="https://github.com/user-attachments/assets/aeedde05-9adf-4065-ab82-d95b30981a0e" />

This system is designed as a **secure, scalable, and agent-driven architecture** for authenticated data processing, intelligent task orchestration, report generation, and user notifications. The architecture follows a **loosely coupled, event-driven design** to ensure reliability and extensibility.


 # High-Level Architecture Diagram

 # Interactive diagram (Eraser):
[https://app.eraser.io/workspace/cwYBuzNqWJcuLDUH4jne?origin=share](https://app.eraser.io/workspace/cwYBuzNqWJcuLDUH4jne?origin=share)


# Authentication & Access Control

* Amazon Cognito

  * Handles user authentication and authorization.
  * Issues secure JWT tokens after successful login.

* Token Verification Layer

  * All incoming client requests are validated using tokens.
  * Prevents unauthorized access to backend services.

* Cloudflare

  * Acts as a security and performance layer.
  * Provides caching, rate limiting, and protection against malicious traffic.
  * Optimizes external API calls and dataset access.


# Backend & Agent Orchestration

* FastAPI (Core Backend)

  * Serves as the primary API gateway.
  * Handles request routing, validation, and orchestration.
  * Communicates with internal services and agents.

* Master Agent

  * Coordinates multi-step tasks.
  * Breaks down requests into subtasks.
  * Publishes jobs to the message broker for asynchronous processing.

* GCP Pub/Sub

  * Used as the **task broker**.
  * Enables event-driven communication between agents.
  * Ensures scalability and fault tolerance.


# Data Ingestion & Storage

* AWS Lambda

  * Handles dataset ingestion workflows.
  * Fetches data from external APIs or uploads.

* Amazon S3

  * Stores datasets, intermediate results, and final outputs.
  * Acts as the central object storage system.

* External APIs

  * Integrated for fetching real-time or third-party data.
  * Cached wherever possible to reduce latency and cost.


# Caching & Performance Optimization

* Redis

  * Temporarily stores intermediate agent results.
  * Reduces recomputation and improves response times.

* Cloudflare Cache

  * Caches frequently requested external API data.
  * Minimizes redundant network calls.


# Persistence & History

* NeonDB (PostgreSQL)

  * Stores chat history and user interaction logs.
  * Ensures consistency and durability of conversational data.



#  Report Generation & Delivery

* Report Generator Agent

  * Compiles processed results into structured PDF reports.
  * Fetches required assets from S3.

* Amazon SES

  * Sends generated reports to users via email.
  * Ensures reliable and scalable email delivery.


## End-to-End Request Flow

1. User sends a request from the client.
2. Request is authenticated via Amazon Cognito.
3. Token is verified before processing.
4. FastAPI receives and routes the request.
5. Master Agent publishes tasks to GCP Pub/Sub.
6. Agents process data asynchronously.
7. Intermediate results cached in Redis.
8. Final outputs stored in S3.
9. Report Generator creates a PDF.
10. Amazon SES emails the report to the user.



#  Key Architectural Benefits

* Scalable – Event-driven architecture supports horizontal scaling.
* Secure – Token-based authentication and Cloudflare protection.
* Modular – Agents can be added or replaced independently.
* Efficient – Caching minimizes latency and cost.
* Production-Ready – Uses battle-tested cloud services.






