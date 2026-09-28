pipeline {
  agent any

  stages {
    stage('Checkout') {
      steps {
        checkout scm
      }
    }
    stage('Build and Test') {
      steps {
        sh 'mvn --batch-mode clean test package'
      }
    }
    stage('Verify Artifact') {
      steps {
        sh 'test -f target/vle6-jenkins-maven-ci-1.0.0.jar'
      }
    }
  }

  post {
    always {
      junit allowEmptyResults: false, testResults: 'target/surefire-reports/*.xml'
      archiveArtifacts artifacts: 'target/*.jar', fingerprint: true
    }
  }
}
