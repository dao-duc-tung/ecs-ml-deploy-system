# ECS MLOps

## Introduction

This is a sample solution to build a completed MLOps pipeline in production for a typical ML system. This example could be useful for any engineer or organization looking to operationalize ML with native AWS development tools such as CodePipeline, CodeBuild, and ECS.

## Architecture

In the following diagram, you can view the continuous delivery stages of the system.

1. Developers push code to trigger the CodePipeline
1. The CodePipeline runs CodeBuild job to run the CloudFormation templates to create resources (first time running) or update resources (second time running)

![architecture][architecture]

### Component Details

- CodePipeline: has various stages that define which step through which actions must be taken in which order to go from source code to creation of the production resources.
- CodeBuild: builds the source code from GitHub and runs CloudFormation templates.
- CloudFormation: creates resources using YAML template.
- Elastic Container Registry (ECR): stores docker images.
- Elastic Container Service (ECS): groups container instances on which we can run task requests.
- Elastic File System (EFS): stores user request's data and model's weights.
- Application Load Balancer (ALB): distributes incoming application traffic across multiple target groups in ECS across Availability Zones. It monitors the health of its registered targets, and routes traffic only to the healthy targets.
- Route 53: connects user requests to infrastructure running in AWS, in our case, the ALB. In this project, we will use another domain provider to route the traffic at domain level.
- AWS Certificate Manager (ACM): provisions, manages, and deploys public and private Secure Sockets Layer/Transport Layer Security (SSL/TLS) certificates for use with AWS services. In this project, we don't use ACM.
- Virtual Private Cloud (VPC): controls our virtual networking environment, including resource placement, connectivity, and security.
- CloudWatch: collects monitoring and operational data in the form of logs, metrics, and events.
- Simple Notification Service (SNS): manages messaging service for both application-to-application (A2A) and application-to-person (A2P) communication. In this project, we don't configure SNS.

## Deployment Steps


<!-- MARKDOWN LINKS & IMAGES -->

[architecture]: /assets/images/architecture.png
