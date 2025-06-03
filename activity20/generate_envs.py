import os, json
from shutil import copyfile

ENVS = []
for i in range(1, 11):
    name = f"app{i}"
    port = 8000 + i
    
    if i == 3:
        network = "net2-peered"  # cuando es app3
    else:
        network = f"net{i}"
        
    ENVS.append({
        "name": name,
        "network": network,
        "port": port
    })

'''
ENVS = [
    {"name": f"app{i}", "network": f"net{i}", "port": 8000 + i} for i in range(1, 11)
]
'''
MODULE_DIR = "modules/simulated_app"
OUT_DIR    = "environments"

def render_and_write(env):
    env_dir = os.path.join(OUT_DIR, env["name"])
    os.makedirs(env_dir, exist_ok=True)

    # 1) Copia la definición de variables (network.tf.json)
    copyfile(
        os.path.join(MODULE_DIR, "network.tf.json"),
        os.path.join(env_dir, "network.tf.json")
    )

    # 2) Genera main.tf.json SÓLO con recursos
    config = {
        "resource": [
            {
                "null_resource": [
                    {
                        f"local_server_{env['name']}": [
                            {
                                "triggers": {
                                    "name":    env["name"],
                                    "network": env["network"],
                                    "port":    env["port"]
                                },
                                "provisioner": [
                                    {
                                        "local-exec": {
                                            "command": (
                                                f"echo 'Arrancando servidor '"
                                                f"{env['name']} en red {env['network']} con puerto {env['port']}"
                                            )
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
    # Limpia entornos viejos (si quieres)
    #if os.path.isdir(OUT_DIR):
    #    import shutil
    #    shutil.rmtree(OUT_DIR)

    for env in ENVS:
        render_and_write(env)
    print(f"Generados {len(ENVS)} entornos en '{OUT_DIR}/'")
