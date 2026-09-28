# VLE 6 Jenkins Maven Continuous Integration

This repository contains the Java 17 Maven application used for Virtual Lab Experiment 6. The deployed Jenkins Freestyle job checks the `main` branch every minute through SCM polling, checks out this repository, runs `mvn --batch-mode clean package`, publishes the JUnit result, and archives the resulting JAR file. Jenkins runs on Java 21 on an Ubuntu EC2 host. Maven compiles the application for Java 17.

The verified deployment uses `ansible/bootstrap_ssm.py` through AWS Systems Manager. Jenkins listens on loopback; use an SSM port-forward to local port 8080 to access it. The Jenkinsfile is an alternative Pipeline definition; the deployed job is Freestyle, as requested by the experiment.

This update also serves as the GitHub push used to verify automatic SCM-triggered rebuilding.

## Local verification

```bash
mvn clean test package
java -cp target/vle6-jenkins-maven-ci-1.0.0.jar com.devops.HelloWorld
```

Expected output:

```text
Hello from Jenkins and Maven CI
```
