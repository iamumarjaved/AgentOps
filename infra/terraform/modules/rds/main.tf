# RDS PostgreSQL Instance

# DB Subnet Group for private subnets
resource "aws_db_subnet_group" "main" {
  name       = "${var.project_name}-${var.environment}-db-subnet-group"
  subnet_ids = var.private_subnet_ids

  tags = {
    Name        = "${var.project_name}-${var.environment}-db-subnet-group"
    Environment = var.environment
    Project     = var.project_name
  }
}

# Security Group for RDS
resource "aws_security_group" "rds" {
  name        = "${var.project_name}-${var.environment}-rds-sg"
  description = "Security group for RDS PostgreSQL"
  vpc_id      = var.vpc_id

  # Allow PostgreSQL traffic from ECS security group
  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [var.ecs_security_group_id]
    description     = "PostgreSQL from ECS"
  }

  # Allow all outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "All outbound traffic"
  }

  tags = {
    Name        = "${var.project_name}-${var.environment}-rds-sg"
    Environment = var.environment
    Project     = var.project_name
  }
}

# RDS PostgreSQL Instance
resource "aws_db_instance" "main" {
  identifier     = "${var.project_name}-${var.environment}-postgres"
  engine         = "postgres"
  engine_version = "16"

  # Instance configuration
  instance_class       = var.db_instance_class
  allocated_storage    = 20
  storage_encrypted    = true
  storage_type         = "gp3"

  # Database configuration
  db_name  = var.db_name
  username = var.db_username
  password = var.db_password

  # Networking
  db_subnet_group_name            = aws_db_subnet_group.main.name
  vpc_security_group_ids          = [aws_security_group.rds.id]
  publicly_accessible             = false
  skip_final_snapshot             = var.environment == "dev" ? true : false
  final_snapshot_identifier_prefix = "${var.project_name}-${var.environment}-final-snapshot"

  # High availability
  multi_az = var.environment == "dev" ? false : true

  # Backup configuration
  backup_retention_period = var.environment == "dev" ? 7 : 30
  backup_window           = "03:00-04:00"
  maintenance_window      = "mon:04:00-mon:05:00"

  # Parameter group
  parameter_group_name = aws_db_parameter_group.main.name

  # Performance and monitoring
  performance_insights_enabled = var.environment == "dev" ? false : true
  enabled_cloudwatch_logs_exports = [
    "postgresql"
  ]

  depends_on = [aws_security_group.rds, aws_db_subnet_group.main]

  tags = {
    Name        = "${var.project_name}-${var.environment}-postgres"
    Environment = var.environment
    Project     = var.project_name
  }
}

# RDS Parameter Group
resource "aws_db_parameter_group" "main" {
  family      = "postgres16"
  name        = "${var.project_name}-${var.environment}-postgres-params"
  description = "Parameter group for PostgreSQL 16"

  # PostgreSQL specific parameters can be added here
  parameter {
    name  = "log_statement"
    value = "all"
    apply_method = "immediate"
  }

  tags = {
    Name        = "${var.project_name}-${var.environment}-postgres-params"
    Environment = var.environment
    Project     = var.project_name
  }
}
