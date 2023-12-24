provider "aws" {
  region = var.aws_region
  shared_credentials_files = ["~/.aws/credentials"]
}

 module "tf_backend" {
  source = "../electricity_bidding_tf_backend"
  bucket_name = "electricity-bidding-tf-state"
}