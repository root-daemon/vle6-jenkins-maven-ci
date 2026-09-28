import base64
import json
import subprocess

script = r"""set -eu
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y -qq openjdk-21-jdk maven git fontconfig curl
install -d /etc/apt/keyrings /etc/systemd/system/jenkins.service.d
curl -fsSL https://pkg.jenkins.io/debian-stable/jenkins.io-2026.key -o /etc/apt/keyrings/jenkins-keyring.asc
printf '%s\n' 'deb [signed-by=/etc/apt/keyrings/jenkins-keyring.asc] https://pkg.jenkins.io/debian-stable binary/' > /etc/apt/sources.list.d/jenkins.list
printf '%s\n' '[Service]' 'Environment="JAVA_OPTS=-Djenkins.install.runSetupWizard=false"' 'Environment="JENKINS_LISTEN_ADDRESS=127.0.0.1"' > /etc/systemd/system/jenkins.service.d/lab.conf
apt-get update -qq
apt-get install -y -qq jenkins
systemctl stop jenkins
curl -fsSL https://github.com/jenkinsci/plugin-installation-manager-tool/releases/download/2.15.0/jenkins-plugin-manager-2.15.0.jar -o /opt/jenkins-plugin-manager.jar
java -jar /opt/jenkins-plugin-manager.jar --war /usr/share/java/jenkins.war --plugin-download-directory /var/lib/jenkins/plugins --plugins git junit
install -d -o jenkins -g jenkins /var/lib/jenkins/jobs/vle6-maven-ci
python3 - <<'PY'
from pathlib import Path
Path('/var/lib/jenkins/jobs/vle6-maven-ci/config.xml').write_text('''<?xml version="1.0" encoding="UTF-8"?>
<project>
 <description>VLE 6 Maven continuous integration from the personal GitHub repository</description>
 <keepDependencies>false</keepDependencies><properties/>
 <scm class="hudson.plugins.git.GitSCM" plugin="git">
  <configVersion>2</configVersion><userRemoteConfigs><hudson.plugins.git.UserRemoteConfig>
  <url>https://github.com/root-daemon/vle6-jenkins-maven-ci.git</url>
  </hudson.plugins.git.UserRemoteConfig></userRemoteConfigs>
  <branches><hudson.plugins.git.BranchSpec><name>*/main</name></hudson.plugins.git.BranchSpec></branches>
  <doGenerateSubmoduleConfigurations>false</doGenerateSubmoduleConfigurations><submoduleCfg class="empty-list"/><extensions/>
 </scm>
 <canRoam>true</canRoam><disabled>false</disabled><blockBuildWhenDownstreamBuilding>false</blockBuildWhenDownstreamBuilding><blockBuildWhenUpstreamBuilding>false</blockBuildWhenUpstreamBuilding>
 <triggers><hudson.triggers.SCMTrigger><spec>* * * * *</spec><ignorePostCommitHooks>false</ignorePostCommitHooks></hudson.triggers.SCMTrigger></triggers><concurrentBuild>false</concurrentBuild>
 <builders><hudson.tasks.Shell><command>mvn --batch-mode clean package
java -cp target/vle6-jenkins-maven-ci-1.0.0.jar com.devops.HelloWorld</command></hudson.tasks.Shell></builders>
 <publishers><hudson.tasks.ArtifactArchiver><artifacts>target/*.jar</artifacts><allowEmptyArchive>false</allowEmptyArchive><fingerprint>true</fingerprint></hudson.tasks.ArtifactArchiver><hudson.tasks.junit.JUnitResultArchiver plugin="junit"><testResults>target/surefire-reports/*.xml</testResults></hudson.tasks.junit.JUnitResultArchiver></publishers><buildWrappers/>
</project>''')
Path('/var/lib/jenkins/init.groovy.d').mkdir(exist_ok=True)
Path('/var/lib/jenkins/init.groovy.d/lab.groovy').write_text('''import jenkins.model.Jenkins
import hudson.model.Cause
def j = Jenkins.get()
j.setNumExecutors(1)
j.save()
def job = j.getItem("vle6-maven-ci")
if (job != null && job.getLastBuild() == null) { job.scheduleBuild2(5, new Cause.UserIdCause()) }
''')
PY
chown -R jenkins:jenkins /var/lib/jenkins/jobs /var/lib/jenkins/plugins /var/lib/jenkins/init.groovy.d
systemctl daemon-reload
systemctl restart jenkins
systemctl is-active jenkins
java -version
mvn -version
"""

payload = {"commands": ["echo " + base64.b64encode(script.encode()).decode() + " | base64 -d | bash"], "executionTimeout": ["1800"]}
result = subprocess.run(['aws', '--profile', 'vishal-test', 'ssm', 'send-command', '--instance-ids', 'i-03bee19bc9c0ebf3f', '--document-name', 'AWS-RunShellScript', '--parameters', json.dumps(payload), '--comment', 'Install VLE6 Jenkins Maven and Freestyle Git CI job', '--query', 'Command.CommandId', '--output', 'text'], check=True, capture_output=True, text=True)
print(result.stdout.strip())
