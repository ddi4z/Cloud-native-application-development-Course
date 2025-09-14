
# This can be improved by using a for_each loop if the number of repositories increases
# CAMBIAR POR LOS REPOSITORIOS

module "add_repository" {
  source = "../../modules/repository"

  keep_tags_number = var.keep_tags_number
  repository_name  = var.add_repository_name
}

module "multiply_repository" {
  source           = "../../modules/repository"
  keep_tags_number = var.keep_tags_number
  repository_name  = var.multiply_repository_name
}
