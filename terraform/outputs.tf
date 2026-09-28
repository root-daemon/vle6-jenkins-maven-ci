output "instance_id" {
  value = aws_instance.jenkins.id
}

output "public_ip" {
  value = aws_instance.jenkins.public_ip
}

output "public_dns" {
  value = aws_instance.jenkins.public_dns
}

output "security_group_id" {
  value = aws_security_group.jenkins.id
}

output "ssm_instance_profile" {
  value = aws_iam_instance_profile.jenkins_ssm.name
}

output "ssh_tunnel_command" {
  value = "ssh -i ../keys/vle6_jenkins_ed25519 -L 8080:localhost:8080 ubuntu@${aws_instance.jenkins.public_ip}"
}
