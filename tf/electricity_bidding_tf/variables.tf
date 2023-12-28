variable "aws_region" {
  description = "AWS region to build in."
  type = string
  default="eu-west-1"
}

variable "private_s3_bucket_name" {
  description = "Name of private s3 bucket."
  type = string
  default="itsakettle-electricity-bidding-private"
}
