resource "aws_s3_bucket" "bronze_tier" {
   bucket = "bronze-tier"
   force_destroy = true
}

resource "aws_s3_bucket" "silver_tirr" {
    bucket = "silver-tier"
    force_destroy = true
}
