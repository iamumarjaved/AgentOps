output "cluster_name" {
  description = "Name of the ECS cluster"
  value       = aws_ecs_cluster.main.name
}

output "ecs_security_group_id" {
  description = "ID of the ECS tasks security group"
  value       = aws_security_group.ecs_tasks.id
}

output "service_names" {
  description = "Names of the ECS services"
  value = {
    api      = aws_ecs_service.api.name
    worker   = aws_ecs_service.worker.name
    frontend = aws_ecs_service.frontend.name
    mlflow   = aws_ecs_service.mlflow.name
  }
}
