resource "aws_s3_bucket" "mlops_tf_artifacts_bucket" {
  bucket = var.bucket_name
  acl    = "private"
}

output "name" {
  value = aws_s3_bucket.mlops_tf_artifacts_bucket.bucket
}
