variable "env" {
  description = "E.g. dev or prod."
  type = string
}

variable "aws_region" {
  description = "AWS region to build in."
  type = string
}

variable "lambda_function_name" {
  description = "lambda function name"
  type = string
  default = "electricity-bidding-extract-semo-lambda"
}

variable "lambda_s3_bucket_info" {
  description = "lambda s3 bucket info"
  type = object({id=string, arn=string})
}