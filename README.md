# ECS MLOps

## Introduction

This is a sample solution to build a completed MLOps pipeline in production for a typical ML system. This example could be useful for any engineer or organization looking to operationalize ML with native AWS development tools such as CodePipeline, CodeBuild, and ECS.

The main use-case of this sample solution is:

- Your team wants to deploy an infrastructure for an ML endpoint of an ML system. Let's call this endpoint "A".
- After that, your team wants to deploy another ML endpoint of the same ML system into the existing infrastructure for your own purpose like testing. Let's call this endpoint "B".

## Architecture

In the following diagram, you can view the continuous delivery stages of the system.

1. Developers push code to trigger the CodePipeline
1. The CodePipeline runs CodeBuild job to run the CloudFormation templates to create resources (first time running) or update resources (second time running)

![architecture][architecture]

### Component Details

- CodePipeline: has various stages that define which step through which actions must be taken in which order to go from source code to creation of the production resources.
- CodeBuild: builds the source code from GitHub and runs CloudFormation templates.
- CloudFormation (CF): creates resources using YAML template.
- Elastic Container Registry (ECR): stores docker images.
- Elastic Container Service (ECS): groups container instances on which we can run task requests.
- Elastic File System (EFS): stores user request's data and model's weights.
- Application Load Balancer (ALB): distributes incoming application traffic across multiple target groups in ECS across Availability Zones. It monitors the health of its registered targets, and routes traffic only to the healthy targets.
- Route 53: connects user requests to infrastructure running in AWS, in our case, the ALB. In this project, we will use another domain provider to route the traffic at domain level.
- AWS Certificate Manager (ACM): provisions, manages, and deploys public and private Secure Sockets Layer/Transport Layer Security (SSL/TLS) certificates for use with AWS services.
- Virtual Private Cloud (VPC): controls our virtual networking environment, including resource placement, connectivity, and security.
- CloudWatch: collects monitoring and operational data in the form of logs, metrics, and events.
- Simple Notification Service (SNS): manages messaging service for both application-to-application (A2A) and application-to-person (A2P) communication. In this project, we don't configure SNS.

## Deployment Step 1: Create Endpoint A

Creating the infrastructure for the endpoint A has several steps:

1. Create the CloudFormation stack
1. Create CodePipeline and CodeBuild projects
1. Validate resources' permission and states
1. Upload model's weights

This infrastructure is reusable for the other endpoint.

### 1.1. Create CloudFormation Stack

The CloudFormation stack creates the ECR repository. The CodePipeline and CodeBuild that we will create in the later steps depend on this ECR repository.

1. Set parameter "DesiredCount" in "cf_templates/create-ep-a.json" to 0 to avoid the error "docker image is not ready" when the CloudFormation stack is created, because at the time the stack is created, the ECR repository doesn't exist. Set other parameters as well.
1. Run
   ```bash
   aws cloudformation create-stack --stack-name=<stack-name> --template-body file://cf_templates/create-ep-a.yaml --parameters file://cf_templates/create-ep-a.json --capabilities CAPABILITY_NAMED_IAM
   ```

### 1.2. Create CodePipeline and CodeBuild projects

This step creates manually CodePipeline and CodeBuild projects. In the next version of this tutorial, this step should be defined in a CloudFormation template.

1. Update "buildspec/ep-a.yaml" file and push the code
1. Go to AWS Console > CodePipeline > Create new pipeline
1. Choose pipeline settings

   - Pipeline name: "ep-a"
   - Select "New service role"

1. Add source stage

   - Connect to GitHub, select repository and branch name
   - Enable "Start the pipeline on source code change"
   - Output artifact format: "Full clone"

1. Add build stage

   - Build provider: "AWS CodeBuild"
   - Select your region
   - Create a CodeBuild project with the following settings:
   - Project name: "ep-a"
   - Environment:
     - System: "Ubuntu"
     - Runtime: "Standard"
     - Image: "standard:4.0"
     - Environment type: "Linux"
     - Privileged: Enabled
     - Create a new service role
     - Buildspec: use a buildspec file
     - Buildspec name: "./buildspec/ep-a.yaml"
   - Build type: "Single build"

1. Skip deploy stage
1. Review and create CodePipeline

### 1.3. Validate resources

#### 1.3.1. Add GitClone permission to CodeBuild project

Follow the section "Add CodeBuild GitClone permissions for connections to Bitbuket, GitHub, or GitHub Enterprise Server" at [this link](https://docs.aws.amazon.com/codepipeline/latest/userguide/troubleshooting.html#codebuild-role-connections).

#### 1.3.2. Validate API Health Check path

Make sure the health check path parameter in "cf_templates/create-ep-a.json" is correct.

#### 1.3.3. Validate ECS's instances permission to access EFS

Manually add the ECS task's security group of the endpoint A to Inbound rules of the security group created for EFS shared volumes. Without this, the ECS's instances cannot access EFS shared volumes. Check [this article](https://forums.aws.amazon.com/thread.jspa?threadID=321135) for more detail.

This step can be automated by creating a AWS Lambda function to run the validation task.

### 1.4. Update CloudFormation stack

1. Set parameter "DesiredCount" in "cf_templates/create-ep-a.json" to the expected value.
1. Set parameter "APITag" to the latest git commit hash in "master" branch.
1. Update stack

   ```bash
   aws cloudformation update-stack --stack-name=<stack-name> --template-body file://cf_templates/create-ep-a.yaml --parameters file://cf_templates/create-ep-a.json --capabilities CAPABILITY_NAMED_IAM
   ```

1. Validate resources
   - ECS: check services, tasks, instances, instances' logs
   - CloudFormation: check created resources, stack status

### 1.5. Upload model's weights

1. Create an S3 folder like `s3://<bucket-name>/<folder-name>`
1. Upload model's weights to this folder
1. Mount the EFS shared weights folder to an EC2 bastion instance (check section `Miscellaneous` below for the instruction of creating this EC2 instance). Check CloudFormation stack's resources for the EFS shared volume's ID
1. Run s3 sync
   ```bash
   sudo aws s3 sync s3://<bucket-name>/<folder-name> /mnt/<MOUNTED_FOLDER> --delete
   ```
1. Add the sync command above as the cronjob of sudo user
   ```bash
   sudo crontab -e
   # Add this line to perform synchronization every 3rd minute of hour
   */3 * * * * aws s3 sync s3://<bucket-name>/<folder-name> /mnt/<MOUNTED_FOLDER> --delete
   ```

### 1.6. Test endpoint

1. Go to the domain service provider (or Route 53), add the expected record (eg. `HostHeaderApi` parameter in `cf_templates/create-ep-a.json`) to point to the DNS name of the ALB created by the CloudFormation stack
1. Test the API by sending a request to the expected URL
1. Mount the shared assets EFS folder to the EC2 bastion instance to validate if the data is stored correctly

## Deployment Step 2: Add Endpoint B

## Miscellaneous

<!-- MARKDOWN LINKS & IMAGES -->

[architecture]: /assets/images/architecture.png
