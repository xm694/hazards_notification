terraform {
      required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  } 
}

# Configure the AWS Provider
provider "aws" {
  region = "ap-southeast-2"
}

module "hazards_pipeline" {
    source = "./module"

    #input variables
    db_name = "hazards_nsw"
    db_user = "root"
    db_pass = "hazards_root"
  
}