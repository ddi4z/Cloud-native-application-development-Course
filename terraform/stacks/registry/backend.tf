terraform {
  backend "s3" {
    bucket = "grupo19-jorgepaternina2-tfstate" 
    key    = "registry/terraform.tfstate"  
    region = "us-east-1"
  }
}