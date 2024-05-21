import docker
import os 
import sys
import time
import docker.models
import docker.models.containers 
from conn_db import check_create_db


# Визначення параметрів контейнера
# Define the container parameters 
def start_db():
    print("******Start******")
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
    } # Відображення томів для збереження даних

    # Завантаження образу Docker для MySQL
    # Pull the MySQL Docker image
    client.images.pull('mysql')

    # Створення контейнера
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
        check_create_db() # Перевірка і створення бази даних
    except:
        time.sleep(20) # Затримка перед повторною перевіркою
        check_create_db()
    return container.id # Повернення ідентифікатора контейнера


# Зупинка контейнера
# Stop the container
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


# Основна функція
# Main function
if __name__ == "__main__":
    
    arg = sys.argv[1].strip()
    
    if arg == "stop":
        # Зупинка контейнера, якщо аргумент дорівнює "stop"
        # Stop the container if the argument is "stop"
        client = docker.from_env()
        for con in client.containers.list(all=True):
            if con.name == "mysql-financedb":
                stop_db(container_id=con.id)
                break
    elif arg == "start":
        # Запуск контейнера, якщо аргумент дорівнює "start"
        # Start the container if the argument is "start"
        start_db()
    else:
        print("-_-")
