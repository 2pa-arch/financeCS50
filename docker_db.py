import docker
import os 




# Define the container parameters
def start_db():
    client = docker.from_env()
    password_mq = "my-secret-pw"
    container_name = 'mysql-financedb'
    port_mapping = {'3306/tcp': 3306}
    environment = {'MYSQL_ROOT_PASSWORD': f'{password_mq}'}
    volumes = {
        os.path.join(os.getcwd(), 'financeDB'): {
            'bind': '/var/lib/mysql',
            'mode': 'rw'
        }
    }

    # Pull the MySQL Docker image
    client.images.pull('mysql')

    # Create the container
    container = client.containers.run(
        'mysql',
        name=container_name,
        ports=port_mapping,
        environment=environment,
        volumes=volumes,
        detach=True
    )


    print(f'Container {container.name} started successfully.')
    return container.id

def stop_db():
    client = docker.from_env()

    container = client.containers.get("mysql-financedb")

    container.stop()
    print(f'Container {container.name} stoped successfully.')
    container = client.containers.get("mysql-financedb")
    print(f'Container {container.name} removed successfully.')
    container.remove()

# if __name__ == "__main__":
#     start_db()