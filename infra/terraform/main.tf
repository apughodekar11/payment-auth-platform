terraform {
  required_version = ">= 1.5"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.region
}

# Look up the AZs available in this region so the VPC isn't hardcoded to specific ones.
data "aws_availability_zones" "available" {
  state = "available"
}

# --- Networking -------------------------------------------------------------
# Official VPC module. I configure it; I don't maintain its internals.
# Two AZs, public + private subnets. The pods live in private subnets and reach
# the internet (ECR pulls) through a single NAT gateway - "single" to save cost,
# at the price of it being one AZ's single point of failure (a real prod cluster
# would use one NAT per AZ).
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name = "${var.project}-vpc"
  cidr = "10.0.0.0/16"

  azs             = slice(data.aws_availability_zones.available.names, 0, 2)
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24"]

  enable_nat_gateway = true
  single_nat_gateway = true

  # These tags are how AWS load balancers know which subnets to use. EKS needs them.
  private_subnet_tags = { "kubernetes.io/role/internal-elb" = 1 }
  public_subnet_tags  = { "kubernetes.io/role/elb" = 1 }
}

# --- EKS cluster ------------------------------------------------------------
# Official EKS module. One managed node group of t3.medium. Desired 1 / max 2 to
# keep cost down for a demo.
module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 20.0"

  cluster_name    = "${var.project}-eks"
  cluster_version = var.cluster_version

  # Public endpoint so I can run kubectl from my laptop. In prod this would be
  # private-only with access through a bastion or VPN.
  cluster_endpoint_public_access = true

  # Grants the IAM identity running `terraform apply` admin on the cluster, so I
  # can immediately use kubectl without manually editing the aws-auth config.
  enable_cluster_creator_admin_permissions = true

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  eks_managed_node_groups = {
    default = {
      instance_types = ["t3.medium"]
      min_size       = 1
      max_size       = 2
      desired_size   = 1
    }
  }
}

# --- Container registry -----------------------------------------------------
# Holds the app image. Terraform owns it so the whole stack is one `apply`.
resource "aws_ecr_repository" "app" {
  name                 = var.project
  image_tag_mutability = "MUTABLE"   # lets me re-push :latest during a demo
  force_delete         = true        # so `terraform destroy` can clean it up even with images in it
}