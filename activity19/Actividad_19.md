# Actividad  19:

### Fase 0:

En este proyecto, se trabajara con una infraestructura local simulada, donde los componentes tradicionales de TI se representan mediante:

* Directorios que simulan entornos o servidores
* Archivos de configuracion que reemplazan configuraciones de servidores reales
* Scripts que emulan servicios y automatización
  
### Comparacion:

| Componente           | Infraestructura Física      | Infraestructura Cloud            | Nuestro Proyecto (IaC Local)         |
|----------------------|-----------------------------|----------------------------------|--------------------------------------|
| Servidores           | Máquinas físicas            | Instancias EC2/VMs               | Directorios (`app1/`, `app2/`)       |
| Red                  | Switches/Cables             | VPCs/Security Groups             | Jerarquía de directorios             |
| Configuración        | Archivos en /etc/           | Parameter Store/Secrets Manager  | `config.json` en cada "app"          |
| Despliegue           | Scripts manuales            | Pipelines CI/CD                  | Scripts Bash/Python gestionado       |
| Estado Documentado   | Documentación obsoleta      | Consolas de administración       | Estado en `.tfstate` (Terraform)     |
