resource "aws_db_instance" "db_instance" {
    instance_class = "db.t4g.micro"
    allocated_storage = 20
    storage_type = "standard"
    engine = "postgres"
    engine_version = "15"
    db_name = var.db_name
    username = var.db_user
    password = var.db_pass
}