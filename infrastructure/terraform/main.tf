terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

# Example VPC and ECS placeholders for PRISM
resource "aws_vpc" "prism_vpc" {
  cidr_block = "10.0.0.0/16"
}
