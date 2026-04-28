
provider "aws" {
  region = var.aws_region
  access_key = var.aws_access_key
  secret_key = var.aws_secret_key
}

resource "aws_instance" "assignment_instance" {
  ami           = var.ami_id
  instance_type = var.instance_type
  key_name = var.key_name
  vpc_security_group_ids = [
    aws_security_group.main_sg.id,
    aws_security_group.api_sg.id
    ]

  provisioner "file" {
    source      = "docker-deploy.sh"
    destination = "/tmp/docker-deploy.sh"
    
    connection {
      type        = "ssh"
      user        = var.ssh_user
      private_key = file(var.ssh_private_key)
      host        = self.public_ip
    }
  }

  provisioner "remote-exec" {
    inline = [
      "chmod +x /tmp/docker-deploy.sh",
      "sudo /tmp/docker-deploy.sh",
    ]

    connection {
      type        = "ssh"
      user        = var.ssh_user
      private_key = file(var.ssh_private_key)
      host        = self.public_ip
    }
  }

  tags = {
    Name = "AssignmentInstance"
  }
}

resource "aws_security_group" "main_sg" {
  name        = "main_security_group"
  description = "Allow SSH and HTTP access"

  # SSH
  ingress {
    from_port   = var.port_ssh
    to_port     = var.port_ssh
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # HTTP
  ingress {
    from_port   = var.port_http
    to_port     = var.port_http
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Grafana
  ingress {
    from_port   = var.port_grafana
    to_port     = var.port_grafana
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Prometheus
  ingress {
    from_port   = var.port_prometheus
    to_port     = var.port_prometheus
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "api_sg" {
  # APIs
  ingress {
    from_port   = var.port_api_from
    to_port     = var.port_api_to
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] 
  }

  # API Gateway
  ingress {
    from_port   = var.port_api_gateway
    to_port     = var.port_api_gateway
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] 
  }
}
