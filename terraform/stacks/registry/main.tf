
# This can be improved by using a for_each loop if the number of repositories increases
# CAMBIAR POR LOS REPOSITORIOS

# made a for loop to generate the repositories for: users, scores, offers, routes. 

variable "apps" {
  type    = list(string)
  default = ["users", "scores", "offers", "routes", "posts", "rf003", "rf004", "rf005"]
}

module "apps_repositories" {
  source = "../../modules/repository"

  for_each = toset([for app in var.apps : "${app}-repository"])

  keep_tags_number = var.keep_tags_number
  repository_name  = each.value
}
