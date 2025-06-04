import os
import json
from shutil import copyfile
import click

# configuración global
MODULE_DIR = "modules/simulated_app"
OUT_DIR = "environments"

# configuración CLI
@click.command()
@click.option('--count', default=10, help='Número de entornos a generar', type=int)
@click.option('--prefix', default='app', help='Prefijo para los nombres de los entornos')
@click.option('--base-port', default=8000, help='Puerto base para asignación', type=int)
def generate_envs(count, prefix, base_port):
    # entornos con configuracion personalizada
    
    ENVS = []
    
    # Generar entornos individuales
    for i in range(1, count + 1):
        name = f"{prefix}{i}"
        port = base_port + i
        
        if i == 3:
            network = "net2-peered"  # app3
        else:
            network = f"net{i}"
            
        ENVS.append({
            "name": name,
            "network": network,
            "port": port
        })

    # balanceador
    if count >= 2:
        ENVS.append({
            "name": "lb_environment",
            "network": "main-network",
            "server1_name": f"{prefix}1",
            "server2_name": f"{prefix}2",
            "server1_port": base_port + 1,
            "server2_port": base_port + 2,
            "es_balanceador": True
        })

    os.makedirs(OUT_DIR, exist_ok=True)

    for env in ENVS:
        render_and_write(env)
    
    print(f"Generados {len(ENVS)} entornos en '{OUT_DIR}/'")

def render_and_write(env):
    """Función auxiliar para renderizar y escribir la configuración"""
    env_dir = os.path.join(OUT_DIR, env["name"])
    os.makedirs(env_dir, exist_ok=True)

    # Copiar definición de variables
    copyfile(
        os.path.join(MODULE_DIR, "network.tf.json"),
        os.path.join(env_dir, "network.tf.json")
    )

    if env.get("es_balanceador"):
        # Configuración para balanceador
        config = {
            "resource": [
                # Servidor1
                {
                    "null_resource": [
                        {
                            f"local_server_{env['server1_name']}": [
                                {
                                    "triggers": {
                                        "name": env["server1_name"],
                                        "network": env["network"],
                                        "port": env["server1_port"]
                                    },
                                    "provisioner": [
                                        {
                                            "local-exec": {
                                                "command": f"echo 'Servidor {env['server1_name']} en red {env['network']} puerto {env['server1_port']}'"
                                            }
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                },
                # Servidor2
                {
                    "null_resource": [
                        {
                            f"local_server_{env['server2_name']}": [
                                {
                                    "triggers": {
                                        "name": env["server2_name"],
                                        "network": env["network"],
                                        "port": env["server2_port"]
                                    },
                                    "provisioner": [
                                        {
                                            "local-exec": {
                                                "command": f"echo 'Servidor {env['server2_name']} en red {env['network']} puerto {env['server2_port']}'"
                                            }
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                },
                # Balanceador
                {
                    "null_resource": [
                        {
                            "load_balancer": [
                                {
                                    "triggers": {
                                        "server1_name": env["server1_name"],
                                        "server2_name": env["server2_name"],
                                        "network": env["network"]
                                    },
                                    "depends_on": [
                                        f"null_resource.local_server_{env['server1_name']}",
                                        f"null_resource.local_server_{env['server2_name']}"
                                    ],
                                    "provisioner": [
                                        {
                                            "local-exec": {
                                                "command": f"echo 'Balanceador para {env['server1_name']} y {env['server2_name']} en red {env['network']}'"
                                            }
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    else:
        # Configuración normal para el resto
        config = {
            "resource": [
                {
                    "null_resource": [
                        {
                            f"local_server_{env['name']}": [
                                {
                                    "triggers": {
                                        "name": env["name"],
                                        "network": env["network"],
                                        "port": env["port"]
                                    },
                                    "provisioner": [
                                        {
                                            "local-exec": {
                                                "command": f"echo 'Servidor {env['name']} en red {env['network']} puerto {env['port']}'"
                                            }
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        }

    with open(os.path.join(env_dir, "main.tf.json"), "w") as fp:
        json.dump(config, fp, sort_keys=True, indent=4)

if __name__ == "__main__":
    generate_envs()