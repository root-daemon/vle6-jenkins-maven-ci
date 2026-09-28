variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "admin_cidr" {
  description = "Single operator IPv4 address allowed to create an SSH tunnel"
  type        = string
}

variable "public_key_path" {
  description = "Public SSH key path relative to the terraform directory"
  type        = string
}

variable "key_name" {
  type    = string
  default = "vle6-jenkins-20260928"
}

variable "instance_type" {
  type    = string
  default = "t3.medium"
}
