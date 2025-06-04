# Actividad  19:

### **Fase 0: Preparación e introducción**

#### Parte 1

En este proyecto, se trabajara con una infraestructura local simulada, donde los componentes tradicionales de TI se representarán mediante:

* **Directorios y archivos** que simulan entornos o servidores
* **Archivos de configuracion** que reemplazan configuraciones de servidores reales
* **Scripts** que emulan servicios y automatización
  
#### Comparacion:

| Componente           | Infraestructura Física      | Infraestructura Cloud            | Nuestro Proyecto (IaC Local)         |
|----------------------|-----------------------------|----------------------------------|--------------------------------------|
| Servidores           | Máquinas físicas            | Instancias EC2/VMs               | Directorios (`app1/`, `app2/`)       |
| Red                  | Switches/Cables             | VPCs/Security Groups             | Jerarquía de directorios             |
| Configuración        | Archivos en /etc/           | Parameter Store/Secrets Manager  | `config.json` en cada "app"          |
| Despliegue           | Scripts manuales            | Pipelines CI/CD                  | Scripts Bash/Python gestionado       |
| Estado Documentado   | Documentación obsoleta      | Consolas de administración       | Estado en `.tfstate` (Terraform)     |

#### Parte 2

#### Configuración manual de infraestructura

Simulando la configuracion manual de un entorno, asi que primeramente creamos un entorno para la aplicacción `app1` de la siguiente manera

```bash
mkdir generated_enviroment/app1
touch generated_enviroment/app1/config.json
touch generated_enviroment/app1/run.sh
```

Configuramos manualmente el archivo `config.json` como:

```json
{
    "app_name": "app1",
    "version": "1.0.0",
    "port": 8080,
    "debug_mode": true
}
```

De la misma manera configuramos manualmente el archivo `run.sh`:

```bash
#!/bin/bash
echo "Iniciando app1..."
python3 app.py
```

### ¿Que problemas puede ocurrir en la configuracion manual?

1. Propensión a Errores Humanos:
  
   - Al configurar el archivo JSON, uno de los desarrolladores puede configurar su entorno con `port 8000` y `debug_mode: false`, ocacionando que su aplicacion no pueda ejecutarse por otro desarrollador que tiene un entorno distinto (ya que lo configuro bien) y que este error no pueda detectarse hasta que sea muy tarde (ej: en integración continua)
  
2. Falta de repoducibilidad:
  
   - Dado que es un proceso manual, esta propenso a errores humanos y a la configuracion del sistema, ocacionando problemas en replicar el entorno exactamente en otro entorno como en desarrollo/pruebas/produccion("funcionaba en mi maquina")

3. Dificultad para escalar:
   
   - Dado que cada microservicio lo estamos separando por directorios, archivos de configuracion y scripts, tendriamos que crear muchos directorios, archivos y scripts para diferentes microservicios que podria necesitar para el funcionamiento de un proyecto ocacionando trabajo repetitivo y alto riesgo de inconsistencias.

#### Infraestructura como código

Se define infraestructura en archivos `.tf` que son caracteristicos de Terraform, una hrrramienta que nos permite describir infraestructura (física, cloud o local) en archivos de configuración legibles. En este caso usaremos Terraform para gestionar archivos y directorios locales como si fuera servidores o servicios.

**¿Como funciona?**

Para definir recursos se utiliza la siguiente sintaxis (ej: local_file, random_id)

```hcl
resource "tipo_recurso" "nombre_logico" {
    argumento1 = valor1
    argumento2 = valor2
}
```

Para configurar el proveedor que se utilizara, se emplea la siguiente sintaxis

```hcl
resource "nombre_proveedor"{
    argumento1 = valor1
    argumento2 = valor2
}
```

Como ejemplo práctico, se creara un directorio, llamado `mi_entorno_local` por medio de archivos terraform:

```hcl
#Ejemplo_practico/versions.tf
terraform {
    required_provider {
        local = {
            source = "hashicorp/local"
            version = "~> 2.5"
        }
    }
}

#Ejemplo_practico/main.tf
resource "local_file" "directorio_ejemplo" {
  filename = "${path.cwd}/mi_entorno_local/README.md"
  content  = "Este directorio fue creado por Terraform"
}
```

Para iniciar la infraestructura (que solamente consiste en crear un directar) seria:

```
terraform init
terraform plan
terraform apply
```

### Ejercicio 1

Añade un nuevo "servicio" llamado `database_connector` al `local.common_app_config` en `main.tf`. Este servicio requiere un parámetro adicional en su configuración JSON llamado `connection_string`.

En este ejercicio aplicamos el principio de **envolvabilidad**, añadiendo un servicio extra y evolucionando nuestra infraestructura. Asi que primeramente añadimos un servicio nuevo dentro de `local.common_app_config` que se encuentra en el `main.tf`. 

```hcl
locals {
  common_app_config = {
    app1 = { version = "1.0.2", port = 8081 }
    app2 = { version = "0.5.0", port = 8082 }
    database = { version = "1.0.0", port = 5432, connection_string_tpl = "" }
  }
}
```

En el mismo archivo, observamos que se instancian los servicios que estan en `local.common_app_config`, asi que actualizamos el campo del servicio que se agrego para que funcione el servicio de `database` (es decir la *app_connection_string*).

```hcl
module "simulated_apps" {
  for_each = local.common_app_config

  source                   = "./modules/application_service"
  app_name                 = each.key
  app_version              = each.value.version
  app_port                 = each.value.port
  app_connection_string    = try(each.value.connection_string_tpl,null)
  base_install_path        = "${path.cwd}/generated_environment/services"
  global_message_from_root = var.mensaje_global
  python_exe               = local.python_executable_full 
}
```

Observamos que este cambio tambien debe propagarse al modulo involucrado, es decir, debemos modificar `./modules/application_service/main.tf` con el nuevo cambio del servicio, asi que creamos una variable y lo agregamos en la siguiente seccion, el cual esta encargado de modificar una plantilla existente `config.json.tpl`:

```hcl
variable "app_connection_string"    { type = string }

data "template_file" "app_config" {
  template = file("${path.module}/templates/config.json.tpl")
  vars = {
    app_name_tpl    = var.app_name
    app_version_tpl = var.app_version
    port_tpl        = var.app_port
    connection_string_tpl = var.app_connection_string
    deployed_at_tpl = timestamp()
    message_tpl     = var.global_message_from_root
  }
}
```

Observamos que se utiliza una plantilla llamada `config.json.tpl`, asi que actualizamos la plantilla con la variable extra que utiliza nuestro servicio que agregamos, se pone una condicional para evitar que la clave apareza en caso *connection_string_tpl* sea vacia.

```json
{
    "applicationName": "${app_name_tpl}",
    "version": "${app_version_tpl}",
    "listenPort": ${port_tpl},
    "deploymentTime": "${deployed_at_tpl}",
    %{ if connection_string_tpl != "" }
    "connectionString": "${connection_string_tpl}",
    %{ endif }
    "notes": "Este es un archivo de configuración autogenerado. ${message_tpl}",
    "settings": {
        "featureA": true,
        "featureB": false,
        "maxConnections": 100,
        "logLevel": "INFO"
        ...
    }
}
```

### Ejercicio 2

Actualmente, el `generate_app_metadata.py` se llama para cada servicio. Imagina que parte de los metadatos es común a todos los servicios en un "despliegue" (ej. un `deployment_id` global).

Primeramente creamos el script de python `generate_global_metadata.py` que genera un id para el despliegue que compartira en todos los servicios.

```python
# scripts/python/generate_global_metadata.py
import json
import uuid

def main():
    deployment_id = str(uuid.uuid4())
    print(json.dumps({"deployment_id": deployment_id}))

if __name__ == "__main__":
    main()
```

Asi que para obtener una id de despligue solamente una vez, modificamos en el `main.tf` de la raiz. En donde ejecutaremos el script y agregaremos un campo extra que sera para la id del despliegue.

```hcl
data "external" "global_metadata" {
  program = [local.python_executable_full, "${path.cwd}/scripts/python/generate_global_metadata.py"]
}

module "simulated_apps" {
  for_each = local.common_app_config

  source                   = "./modules/application_service"
  app_name                 = each.key
  app_version              = each.value.version
  app_port                 = each.value.port
  app_connection_string    = try(each.value.connection_string_tpl,null)
  base_install_path        = "${path.cwd}/generated_environment/services"
  global_message_from_root = var.mensaje_global
  deployment_id            = data.external.global_metadata.result.deployment_id
  python_exe               = local.python_executable_full 
}
```

Como observamos, al agregar un nuevo campo, tambien se modificaria `./modules/application_service/main.tf`, asi que agregamos una nueva variable y asignamos un nuevo campo que seria el id del despliegue que se modificaria en la plantilla cuando se cree los servicios.

```hcl
variable "deployment_id"            { type = string }

data "template_file" "app_config" {
  template = file("${path.module}/templates/config.json.tpl")
  vars = {
    app_name_tpl    = var.app_name
    app_version_tpl = var.app_version
    port_tpl        = var.app_port
    deployment_id_tpl = var.deployment_id
    connection_string_tpl = var.app_connection_string
    deployed_at_tpl = timestamp()
    message_tpl     = var.global_message_from_root
  }
}
```

Como observamos, se asigna un nuevo campo, asi que modificaremos la plantilla para que reciba este nuevo campo y se refleje el id del despliegue en cada servicio.

```json
{
    "applicationName": "${app_name_tpl}",
    "version": "${app_version_tpl}",
    "listenPort": ${port_tpl},
    ...
    "deploymentId": "${deployment_id_tpl}",
    ...
}
```

Ademas para generar los metadatos, se tiene que ejecutar el script `generate_app_metadata.py` por medio del archivo `./modules/application_service/main.tf` y para que genere el id del despliegue le tenemos que pasar al script, asi que modificamos el siguiente bloque con el campo *deployment_id*: 

```hcl
data "external" "app_metadata_py" {
  program = [var.python_exe, "${path.root}/scripts/python/generate_app_metadata.py"]

  query = merge(
    {
      app_name      = var.app_name
      version       = var.app_version
      deployment_id = var.deployment_id
    },
    {
      q1  = "v1",  q2  = "v2",  q3  = "v3",  q4  = "v4",  q5  = "v5",
      q6  = "v6",  q7  = "v7",  q8  = "v8",  q9  = "v9",  q10 = "v10",
      q11 = "v11", q12 = "v12", q13 = "v13", q14 = "v14", q15 = "v15",
      q16 = "v16", q17 = "v17", q18 = "v18", q19 = "v19", q20 = "v20"
    }
  )
}
```

Y ademas modificamos el Script `generate_app_metadata.py` para que el id del despligue se escriba en el JSON como se muestra: 

```python
...
app_name = input_json.get("app_name", "unknown_app")
app_version = input_json.get("version", "0.0.0")
deployment_id = input_json.get("deployment_id", "unknown_deployment")

metadata = {
    "appName": app_name,
    "deploymentId": deployment_id,
    ...
}
```

De esta manera, cuando aplicamos la infraestructura tenemos que en el archivo JSON generado `metadata_generated.json` y `config.json` de cada servicio que aplicamos tendria el mismo id del despliegue `deploymentID` como para el servicio **app1_v1.0.2**:

```json
//generated_enviroment/services/app1_v1.0.2/config.json
{
    "applicationName": "app1",
    "version": "1.0.2",
    "listenPort": 8081,
    "deploymentId": "1b0e1874-3518-450b-bc57-471876ee795f",
    ...
}
```

Para el servicio **app2_v0.5.0**

```json
//generated_enviroment/services/app2_v0.5.0/config.json
{
    "applicationName": "app2",
    "version": "0.5.0",
    "listenPort": 8082,
    "deploymentId": "1b0e1874-3518-450b-bc57-471876ee795f",
    ...
}
```

Para el servicio **database_v1.0.0**

```json
//generated_enviroment/services/database_v1.0.0/config.json
{
    "applicationName": "database",
    "version": "1.0.0",
    "listenPort": 5432,
    "deploymentId": "1b0e1874-3518-450b-bc57-471876ee795f",
    ...
}
```











