terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket         = "agentops-terraform-state"
    key            = "terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform-locks"
    encrypt        = true
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "agentops"
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}

# Data source for current AWS account
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

# VPC
module "vpc" {
  source = "./modules/vpc"

  project_name = var.project_name
  environment  = var.environment
  vpc_cidr     = var.vpc_cidr
  azs          = var.azs
}

# ECR repositories
module "ecr" {
  source = "./modules/ecr"

  project_name = var.project_name
  services     = ["api", "worker", "frontend", "mlflow"]
}

# RDS PostgreSQL
module "rds" {
  source = "./modules/rds"

  project_name       = var.project_name
  environment        = var.environment
  vpc_id             = module.vpc.vpc_id
  private_subnet_ids = module.vpc.private_subnet_ids
  db_instance_class  = var.db_instance_class
  db_name            = "agentops"
  db_username        = var.db_username
  db_password        = var.db_password
  ecs_security_group_id = module.ecs.ecs_security_group_id
}

# S3 for artifacts
module "s3" {
  source = "./modules/s3"

  project_name = var.project_name
  environment  = var.environment
}

# IAM roles
module "iam" {
  source = "./modules/iam"

  project_name   = var.project_name
  environment    = var.environment
  s3_bucket_arn  = module.s3.bucket_arn
  ecr_arns       = module.ecr.repository_arns
  account_id     = data.aws_caller_identity.current.account_id
  region         = data.aws_region.current.name
}

# Security groups & WAF
module "security" {
  source = "./modules/security"

  project_name = var.project_name
  environment  = var.environment
  vpc_id       = module.vpc.vpc_id
  alb_arn      = module.alb.alb_arn
}

# ALB
module "alb" {
  source = "./modules/alb"

  project_name      = var.project_name
  environment       = var.environment
  vpc_id            = module.vpc.vpc_id
  public_subnet_ids = module.vpc.public_subnet_ids
  security_group_id = module.security.alb_security_group_id
  certificate_arn   = var.certificate_arn
}

# ElastiCache Redis
module "elasticache" {
  source = "./modules/elasticache"

  project_name       = var.project_name
  environment        = var.environment
  vpc_id             = module.vpc.vpc_id
  private_subnet_ids = module.vpc.private_subnet_ids
  node_type          = var.redis_node_type
  ecs_security_group_id = module.ecs.ecs_security_group_id
}

# ECS Fargate
module "ecs" {
  source = "./modules/ecs"

  project_name       = var.project_name
  environment        = var.environment
  vpc_id             = module.vpc.vpc_id
  private_subnet_ids = module.vpc.private_subnet_ids
  execution_role_arn = module.iam.ecs_execution_role_arn
  task_role_arn      = module.iam.ecs_task_role_arn

  ecr_repository_urls = module.ecr.repository_urls

  database_url       = module.rds.connection_url
  redis_url          = module.elasticache.connection_url
  mlflow_tracking_uri = "http://mlflow.${var.project_name}.local:5000"

  api_target_group_arn      = module.alb.api_target_group_arn
  frontend_target_group_arn = module.alb.frontend_target_group_arn
  mlflow_target_group_arn   = module.alb.mlflow_target_group_arn
  grafana_target_group_arn  = module.alb.grafana_target_group_arn

  alb_security_group_id = module.security.alb_security_group_id

  api_cpu    = var.api_cpu
  api_memory = var.api_memory
  api_desired_count = var.api_desired_count
}

# CloudWatch monitoring
module "monitoring" {
  source = "./modules/monitoring"

  project_name    = var.project_name
  environment     = var.environment
  ecs_cluster_name = module.ecs.cluster_name
  alb_arn_suffix  = module.alb.alb_arn_suffix
  rds_identifier  = module.rds.db_identifier
}
