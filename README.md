# VLE 6 Jenkins Maven Continuous Integration

This repository contains the Java 17 Maven application used for Virtual Lab Experiment 6. The deployed Jenkins Freestyle job checks the `main` branch every minute through SCM polling, checks out this repository, runs `mvn --batch-mode clean package`, publishes the JUnit result, and archives the resulting JAR file. Jenkins runs on Java 21 on an Ubuntu EC2 host. Maven compiles the application for Java 17.

The verified AWS-only deployment uses the `vle6-terraform-cloud-deploy` CodeBuild project in account `071292884790`, region `us-east-1`. The project reads a private S3 source archive, runs Terraform `init`, `validate`, `plan`, and `apply` against the versioned S3 state backend, then calls `cloud-runner/configure_jenkins_via_ssm.py`. That script sends the existing Jenkins bootstrap through AWS Systems Manager to the EC2 host and verifies that Jenkins is active, Maven is installed, and the latest Freestyle build succeeded with a JAR artifact. CodeBuild uses its IAM role rather than local AWS credentials.

The latest successful build ID is `vle6-terraform-cloud-deploy:2e7f0b6d-556a-4462-be46-4f73ecd47b6e` (29 Sep 2026). Google Chrome screenshots of AWS CloudShell build status and SSM verification are in `evidence/09-cloudshell-vle6-codebuild.png` and `evidence/10-cloudshell-jenkins-ssm.png`. To rerun:

```bash
aws codebuild start-build --project-name vle6-terraform-cloud-deploy --profile vishal-test --region us-east-1
```

The S3 source archive is `s3://vle6-terraform-state-071292884790-us-east-1/artifacts/vle6-cloud-redo.zip`; update it before rerunning if source files change. Jenkins listens on loopback; use an SSM port-forward to local port 8080 to access it. The Jenkinsfile is an alternative Pipeline definition; the deployed job is Freestyle, as requested by the experiment.

An earlier GitHub push triggered the verified Jenkins SCM rebuild. The AWS-only Terraform and SSM deployment described here does not require a new GitHub push.

## Local verification

```bash
mvn clean test package
java -cp target/vle6-jenkins-maven-ci-1.0.0.jar com.devops.HelloWorld
```

Expected output:

```text
Hello from Jenkins and Maven CI
```
