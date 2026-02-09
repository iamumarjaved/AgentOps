variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
}

variable "vpc_id" {
  description = "ID of the VPC"
  type        = string
}

variable "private_subnet_ids" {
  description = "List of private subnet IDs for ECS tasks"
  type        = list(string)
}

variable "execution_role_arn" {
  description = "ARN of the ECS execution role"
  type        = string
}

variable "task_role_arn" {
  description = "ARN of the ECS task role"
  type        = string
}

variable "ecr_repository_urls" {
  description = "Map of ECR repository URLs"
  type        = map(string)
}

variable "database_url" {
  description = "Database connection URL"
  type        = string
  sensitive   = true
}

variable "redis_url" {
  description = "Redis connection URL"
  type        = string
}

variable "mlflow_tracking_uri" {
  description = "MLflow tracking server URI"
  type        = string
}

variable "api_target_group_arn" {
  description = "ARN of the API target group"
  type        = string
}

variable "frontend_target_group_arn" {
  description = "ARN of the frontend target group"
  type        = string
}

variable "mlflow_target_group_arn" {
  description = "ARN of the MLflow target group"
  type        = string
}

variable "grafana_target_group_arn" {
  description = "ARN of the Grafana target group"
  type        = string
}

variable "api_cpu" {
  description = "CPU units for API task"
  type        = string
  default     = "512"
}

variable "api_memory" {
  description = "Memory for API task in MB"
  type        = string
  default     = "1024"
}

variable "api_desired_count" {
  description = "Desired number of API tasks"
  type        = number
  default     = 1
}

variable "alb_security_group_id" {
  description = "Security group ID of the ALB"
  type        = string
}
