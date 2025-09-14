variable "region" {
  description = "La región de AWS donde se desplegarán los recursos."
  type        = string
  nullable    = false
}

variable "owner" {
  description = "Dueño de los recursos. Para propósito acadmémico."
  type        = string
  nullable    = false
}

variable "keep_tags_number" {
  description = "Number of tags to keep in the registry"
  type        = number
}

# TODO: CAMBIAR POR LOS REPOSITORIOS

variable "add_repository_name" {
  description = "Name of the repository to add"
  type        = string
  nullable    = false
}

variable "multiply_repository_name" {
  description = "Name of the repository to multiply"
  type        = string
  nullable    = false
}
