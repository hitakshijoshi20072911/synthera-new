# synthera-new
# NOTE: 
This project is currently being revamped. Changes:
1. Migration to individual worker services from a single langGraph worker.
2. Migration to Kubernetes based infra
3. Aggressive caching for cost optimization

# Revamped Architecture
![System Architecture](./docs/arc.png)
   
# Old architecture
<img width="1030" height="320" alt="image" src="https://github.com/user-attachments/assets/aeedde05-9adf-4065-ab82-d95b30981a0e" />

 # Interactive diagram (Eraser):
[https://app.eraser.io/workspace/cwYBuzNqWJcuLDUH4jne?origin=share](https://app.eraser.io/workspace/cwYBuzNqWJcuLDUH4jne?origin=share)

# Tech stack
1. Frontend : NextJS
2. Backend Services : FastAPI
3. Common Database: postgreSQL
4. Queue system : Kafka 
5. Caching : Redis Cloud
6. Authentication : Custom fine grained auth
8. Containerization : Docker
9. Deployments : Kubernetes (to be deployed on GKE)
10. File storage : Amazon S3
11. Email Service : Amazon SES
12. Task runner: Celery

#  Key Architectural Benefits

* Scalable – Event-driven architecture supports horizontal scaling.
* Secure – Token-based authentication and Cloudflare protection.
* Modular – Agents can be added or replaced independently.
* Efficient – Caching minimizes latency and cost.
* Production-Ready – Uses battle-tested cloud services.
* Multi cloud architecture to reduce dependance on one single cloud provider

# Project Overview

This project implements an **agent-driven backend system** with a secure frontend, asynchronous processing, and automated report generation. The architecture is designed for scalability, clear separation of concerns, and reliable communication between services.

The system follows a **request → process → report → notify** workflow, orchestrated by a central master agent and supported by worker agents.

## High-Level Architecture

<img width="647" height="596" alt="image" src="https://github.com/user-attachments/assets/858e605c-e43c-4eb8-9fe9-2f3a09eeb0e4" />


The application is composed of four major layers:

1. **User & Frontend Layer**
2. **Authentication & Messaging Layer**
3. **Backend API & Agentic System**
4. **Reporting & Notification Layer**

Each layer communicates through well-defined interfaces to ensure security, fault tolerance, and extensibility.

## System Highlights

* Secure authentication and authorization
* Scalable agent-based processing
* Asynchronous and event-driven design
* Efficient caching to reduce recomputation
* Secure report access using pre-signed URLs
* Clean separation between orchestration, execution, and presentation layers


## Conclusion

This architecture enables a robust, scalable, and intelligent system for automated report generation and delivery. By leveraging an agentic approach with FastAPI and cloud-native services, the project ensures performance, reliability, and maintainability suitable for production environments.







