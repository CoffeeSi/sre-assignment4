
variable "aws_region" {
  type    = string
  description = "AWS region to deploy resources in"
  default = "eu-north-1"
}

variable "instance_type" {
  type    = string
  description = "EC2 instance type"
  default = "t3.micro"
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