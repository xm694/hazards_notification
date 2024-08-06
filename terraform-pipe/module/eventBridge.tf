resource "aws_cloudwatch_event_rule" "s3_object_created" {
  name        = "s3_object_created"
  description = "Invoke Data Process when a s3 object is created"

  event_pattern = jsonencode({
    source = ["aws.s3"]
    detail-type = ["Object Created"]
    detail = {
        bucket = {
          name = [aws_s3_bucket.bronze_tier.id]
        }
    }
  })
}

resource "aws_cloudwatch_event_target" "Lambda_data_process" {
  rule      = aws_cloudwatch_event_rule.s3_object_created.name
  target_id = "SendToLambda"
  arn       = aws_lambda_function.data_process.arn
}

resource "aws_lambda_permission" "allow_eventbridge1" {
    principal = "events.amazonaws.com"
    statement_id = "AllowExecutionFromEventBridge"
    action = "lambda:InvokeFunction"
    function_name = aws_lambda_function.data_process.function_name
    source_arn = aws_cloudwatch_event_rule.s3_object_created.arn
}

resource "aws_cloudwatch_event_rule" "every_day" {
    name = "every_day_rule"
    description = "trigger lambda every day at 6am"

    schedule_expression = "cron(0 16 * * ? *)"
}

resource "aws_cloudwatch_event_target" "Lambda_target" {
    rule = aws_cloudwatch_event_rule.every_day.name
    target_id = "SendToLambda"
    arn = aws_lambda_function.data_extract.arn
}

resource "aws_lambda_permission" "allow_eventbridge2" {
    principal = "events.amazonaws.com"
    statement_id = "AllowExecutionFromEventBridge"
    action = "lambda:InvokeFunction"
    function_name = aws_lambda_function.data_extract.function_name
    source_arn = aws_cloudwatch_event_rule.every_day.arn
}