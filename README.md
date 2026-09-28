# VLE 6 Jenkins Maven Continuous Integration

This repository contains the Java 17 Maven application used for Virtual Lab Experiment 6. Jenkins checks the `main` branch through SCM polling, checks out this repository, runs `mvn clean test package`, publishes the JUnit result, and archives the resulting JAR file.

## Local verification

```bash
mvn clean test package
java -cp target/vle6-jenkins-maven-ci-1.0.0.jar com.devops.HelloWorld
```

Expected output:

```text
Hello from Jenkins and Maven CI
```
