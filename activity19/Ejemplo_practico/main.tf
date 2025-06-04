resource "local_file" "directorio_ejemplo" {
  filename = "${path.cwd}/mi_entorno_local/README.md"
  content  = "Este directorio fue creado por Terraform"
}