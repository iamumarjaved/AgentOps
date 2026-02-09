resource "aws_ecr_repository" "services" {
  for_each = toset(var.services)

  repository_name = "${var.project_name}-${each.value}"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  force_delete = var.environment == "dev" ? true : false

  tags = {
    Name        = "${var.project_name}-${each.value}"
    Project     = var.project_name
    Service     = each.value
    Environment = var.environment
  }
}

resource "aws_ecr_lifecycle_policy" "services" {
  for_each = aws_ecr_repository.services

  repository = each.value.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Keep last 10 images"
        selection = {
          tagStatus     = "any"
          countType     = "imageCountMoreThan"
          countNumber   = 10
        }
        action = {
          type = "expire"
        }
      }
    ]
  })
}
