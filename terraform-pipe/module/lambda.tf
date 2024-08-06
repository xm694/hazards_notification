resource "aws_lambda_function" "data_extract" {
    filename = "./main/data_extract.zip" #need to add zip to same path
    function_name = "data_extract"
    role = aws_iam_role.iam_for_dataextrac.arn
    handler = "extract.handler"

    runtime = "python3.12"

}

resource "aws_lambda_function" "data_process" {
    filename = "./main/data_process.zip" #need to add zip to same path
    function_name = "data_process"
    role = aws_iam_role.iam_for_dataprocess.arn
    handler = "dataprocess.handler"

    runtime = "python3.12"

}

# IAM role for Lambda
data "aws_iam_policy_document" "lambda_role_policy" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "iam_for_dataextrac" {
    name = "policy_for_dataextrac"
    assume_role_policy = jsonencode({
      Version = "2012-10-17"
      Statement = [
        {
          Action = "sts:AssumeRole"
          Effect = "Allow"
          Principal = {
            Service = "lambda.amazonaws.com"
          }
        }
      ]
    })
    
    inline_policy {
      name = "inline_policy_dataextract"

      policy = jsonencode({
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "Statement1",
                    "Effect": "Allow",
                    "Action": [
                        "s3:put*",
                        "s3:ListBucket",
                        "s3:GetObject"
                    ],
                    "Resource": [
                        "arn:aws:s3:::hazards-nsw",
                        "arn:aws:s3:::hazards-nsw/*"
                    ]
                }
            ]
        })
    } 
}

resource "aws_iam_role" "iam_for_dataprocess" {
    name = "policy_for_dataprocess"
    assume_role_policy = data.aws_iam_policy_document.lambda_role_policy.json
    
    inline_policy {
    name = "inline_policy_dataprocess"

    policy = jsonencode({
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "Statement1",
                "Effect": "Allow",
                "Action": [
                    "s3:list*",
                    "s3:get*",
                    "s3:put*"
                ],
                "Resource": [
                    "arn:aws:s3:::hazards-nsw",
                    "arn:aws:s3:::hazards-nsw/*",
                    "arn:aws:s3:::silver-hazard-nsw",
                    "arn:aws:s3:::silver-hazard-nsw/*"
                ]
            },
            {
                "Sid": "Statement2",
                "Effect": "Allow",
                "Action": [
                    "ec2:CreateNetworkInterface",
                    "ec2:DescribeNetworkInterfaces",
                    "ec2:DeleteNetworkInterface"
                ],
                "Resource": [
                    "*"
                ]
            },
            {
                "Sid": "PublishSNSMessage",
                "Effect": "Allow",
                "Action": [
                    "sns:Publish"
                ],
                "Resource": [
                    "arn:aws:sns:ap-southeast-2:654654465889:hazards-nsw"
                ]
            }
        ]
      })
    }
}

# locals {
#   permission_json_file = file("data_extract_role.json")
#   permission_json = jsondecode(local.permission_json_file)
# }

# resource "aws_iam_policy" "access_s3" {
#     name = "want-to-acess-s3"
#     policy = local.permission_json_file
# }

# resource "aws_iam_policy_attachment" "attach_S3_policy" {
#     name = aws_iam_role.iam_for_dataextrac.name
#     policy_arn = aws_iam_policy.access_s3.arn
# }