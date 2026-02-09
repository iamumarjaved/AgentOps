output "repository_urls" {
  description = "Map of service names to ECR repository URLs"
  value = {
    for service, repo in aws_ecr_repository.services :
    service => repo.repository_url
  }
}

output "repository_arns" {
  description = "List of ECR repository ARNs"
  value = [
    for repo in aws_ecr_repository.services :
    repo.arn
  ]
}

output "repositories" {
  description = "Map of all ECR repositories with their details"
  value = {
    for service, repo in aws_ecr_repository.services :
    service => {
      url              = repo.repository_url
      arn              = repo.arn
      name             = repo.name
      registry_id      = repo.registry_id
    }
  }
}
