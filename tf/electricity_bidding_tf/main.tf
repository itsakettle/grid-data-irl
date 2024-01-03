provider "aws" {
  region = var.aws_region
  shared_credentials_files = ["~/.aws/credentials"]
}

module "tf_backend" {
  source = "../electricity_bidding_tf_backend"
  bucket_name = "electricity-bidding-tf-state"
}

module "extract_semo" {
  source = "./extract_semo"
  env = var.env
  aws_region = var.aws_region
  lambda_s3_bucket = locals.lambda_s3_bucket
}



