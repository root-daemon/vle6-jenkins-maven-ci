terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "VLE6-Jenkins-Maven"
      Lab         = "VLE6"
      Environment = "lab"
      ManagedBy   = "Terraform"
      Owner       = "root-daemon"
    }
  }
}

data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

data "aws_subnet" "selected" {
  id = sort(data.aws_subnets.default.ids)[0]
}

data "aws_ssm_parameter" "ubuntu_2404" {
  name = "/aws/service/canonical/ubuntu/server/24.04/stable/current/amd64/hvm/ebs-gp3/ami-id"
}

resource "aws_key_pair" "jenkins" {
  key_name   = var.key_name
  public_key = file(var.public_key_path)
}

resource "aws_iam_role" "jenkins_ssm" {
  name = "vle6-jenkins-ssm-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Service = "ec2.amazonaws.com"
      }
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "jenkins_ssm_core" {
  role       = aws_iam_role.jenkins_ssm.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_instance_profile" "jenkins_ssm" {
  name = "vle6-jenkins-ssm-profile"
  role = aws_iam_role.jenkins_ssm.name
}

resource "aws_security_group" "jenkins" {
  name        = "vle6-jenkins-sg"
  description = "SSH access to the VLE 6 Jenkins lab host"
  vpc_id      = data.aws_vpc.default.id

  tags = {
    Name         = "vle6-jenkins-sg"
    WorkloadType = "jenkins-ci"
  }
}

resource "aws_vpc_security_group_ingress_rule" "ssh_operator" {
  security_group_id = aws_security_group.jenkins.id
  cidr_ipv4         = var.admin_cidr
  from_port         = 22
  ip_protocol       = "tcp"
  to_port           = 22
  description       = "SSH tunnel access from the lab operator"
}

resource "aws_vpc_security_group_egress_rule" "all_outbound" {
  security_group_id = aws_security_group.jenkins.id
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "-1"
  description       = "Ubuntu packages, Jenkins plugins, Maven dependencies, and GitHub access"
}

resource "aws_instance" "jenkins" {
  ami                         = data.aws_ssm_parameter.ubuntu_2404.value
  instance_type               = var.instance_type
  subnet_id                   = data.aws_subnet.selected.id
  vpc_security_group_ids      = [aws_security_group.jenkins.id]
  associate_public_ip_address = true
  iam_instance_profile        = aws_iam_instance_profile.jenkins_ssm.name
  key_name                    = aws_key_pair.jenkins.key_name

  metadata_options {
    http_endpoint               = "enabled"
    http_tokens                 = "required"
    http_put_response_hop_limit = 1
  }

  root_block_device {
    encrypted             = true
    volume_type           = "gp3"
    volume_size           = 20
    delete_on_termination = true
  }

  tags = {
    Name         = "vle6-jenkins-server"
    WorkloadType = "jenkins-ci"
  }
}
