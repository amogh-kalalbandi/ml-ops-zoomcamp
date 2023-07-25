terraform {
  required_version = ">= 1.0"
  backend "s3" {
    bucket  = "mlflow-artifacts-remote-amogh"
    key     = "mlops-zoomcamp.tfstate"
    region  = "us-east-2"
    encrypt = true
  }
}

provider "aws" {
  region  = var.aws_region
  profile = "default"
}


data "aws_caller_identity" "current_identity" {}

locals {
  account_id = data.aws_caller_identity.current_identity.account_id
}

# ride events
module "source_kinesis_stream" {
  source           = "./modules/kinesis"
  stream_name      = "${var.source_stream_name}-${var.project_id}"
  retention_period = 48
  shard_count      = 2
  tags             = var.project_id
}


# ride_predictions
module "output_kinesis_stream" {
  source           = "./modules/kinesis"
  stream_name      = "${var.output_stream_name}-${var.project_id}"
  retention_period = 48
  shard_count      = 2
  tags             = var.project_id
}


# model artifacts bucket
module "artifacts_s3_bucket" {
  source      = "./modules/s3"
  bucket_name = "${var.model_bucket_name}-${var.project_id}"
}

# image registry
module "ecr_image" {
  source                     = "./modules/ecr"
  ecr_repo_name              = "${var.ecr_repo_name}_${var.project_id}"
  account_id                 = local.account_id
  lambda_function_local_path = var.lambda_function_local_path
  docker_image_local_path    = var.docker_image_local_path
}
