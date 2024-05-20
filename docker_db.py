import docker
import os 
import sys
import time
import docker.models
import docker.models.containers 
from conn_db import check_create_db



# Define the container parameters
def start_db():
    print("AAAAAABBBB")
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
    try:
        container = client.containers.run(
            'mysql',
            name=container_name,
            ports=port_mapping,
            environment=environment,
            volumes=volumes,
            detach=True
        )
    except Exception as ex:
        print('OOps, mb db alredy start')
        print(ex)
        return



    print(f'Container {container.name} started successfully.')
    try:
        check_create_db()
    except:
        time.sleep(10)
        check_create_db()
    return container.id

def stop_db(container_id):
    client = docker.from_env()

    container = client.containers.get(container_id)
    try:
        container.stop()
    except:
        print('OOps, mb db alredy stop')
    print(f'Container {container.name} stoped successfully.')
    container = client.containers.get(container_id)
    print(f'Container {container.name} removed successfully.')
    try:
        container.remove()
    except:
        print('OOps, mb db alredy remove')



if __name__ == "__main__":
    
    arg = sys.argv[1].strip()
    
    if arg == "stop":
        
        client = docker.from_env()
        for con in client.containers.list(all=True):
            if con.name == "mysql-financedb":
                stop_db(container_id=con.id)
                break
    elif arg == "start":
        start_db()
    else:
        print("-_-")
