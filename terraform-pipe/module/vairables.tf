#general variables
variable "region" {
  description = "default region"
  type = string
  default = "ap-southeast-2"
}

# RDS Variables
variable "db_name" {
  description = "DB name"
  type = string
}

variable "db_user" {
  description = "Username for DB"
  type = string
}

variable "db_pass" {
  description = "Password for DB"
  type = string
  sensitive = true
}

#sns email subscription
variable "email_subscription" {
  default = ["shaymok11@gmail.com", "chapagain.aaditya@gmail.com"]
}