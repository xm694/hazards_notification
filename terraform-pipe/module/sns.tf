resource "aws_sns_topic" "new_hazards_notification" {
    name = "new_hazards_notification"
}

resource "aws_sns_topic_subscription" "new_hazards_subs" {
  topic_arn = aws_sns_topic.new_hazards_notification.arn
  protocol = "email"
  for_each = toset(var.email_subscription)
  endpoint = each.value
}