
variable "aws_region" {
  type    = string
  description = "AWS region to deploy resources in"
  default = "eu-north-1"
}

variable "instance_type" {
  type    = string
  description = "EC2 instance type"
  default = "t3.small"
}

variable "ami_id" {
  type    = string
  description = "AMI ID for the EC2 instance"
  default = "ami-0a0823e4ea064404d"
}

variable "aws_access_key" {
  type    = string
  description = "AWS Access Key"
}

variable "aws_secret_key" {
  type    = string
  description = "AWS Secret Key"
}

variable "key_name" {
  type = string
  description = "key name"
}

variable "ssh_user" {
  type = string
  description = "SSH username for EC2 instance"
  default = "ubuntu"
}

variable "ssh_private_key" {
  type = string
  description = "SSH private key for EC2 instance"
  sensitive = true
}

variable "port_ssh" {
  type = number
  description = "SSH port"
  default = 22
}

variable "port_http" {
  type = number
  description = "HTTP port"
  default = 80
}

variable "port_grafana" {
  type = number
  description = "Grafana port"
  default = 3000
}

variable "port_prometheus" {
  type = number
  description = "Prometheus port"
  default = 9090
}

variable "port_api_from" {
  type = number
  description = "API from port"
  default = 8000
}

variable "port_api_to" {
  type = number
  description = "API to port"
  default = 8005
}

variable "port_api_gateway" {
  type = number
  description = "API Gateway port"
  default = 8080
}