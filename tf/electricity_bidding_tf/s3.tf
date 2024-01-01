resource "aws_s3_bucket" "private" {
  bucket = "${var.private_s3_bucket_name}"
 
  # Prevent accidental deletion of this S3 bucket 
  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_s3_bucket_versioning" "disabled" {
  bucket = aws_s3_bucket.private.id
  versioning_configuration {
    status = "Disabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "default" {
  bucket = aws_s3_bucket.private.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "public_access" {
  bucket                  = aws_s3_bucket.private.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Bucket for lambdas
resource "aws_s3_bucket" "lambda_bucket" {
  bucket = "${var.lambda_s3_bucket_name}-${var.env}"
  force_destroy = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "default" {
  bucket = aws_s3_bucket.lambda_bucket.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "public_access" {
  bucket                  = aws_s3_bucket.melostats_lambda_bucket.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

locals {
  lambda_s3_bucket_id = aws_s3_bucket.lambda_bucket.id
}