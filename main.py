import docker
import os
from pathutils import PathUtils as pu


pu.target_system = "linux"



# Globale Variable für den Docker-Client
client = docker.from_env()

def list_volumes():
    volumes = client.volumes.list()
    for volume in volumes:
        print(volume.name)

def select_volume(name):
    try:
        volume = client.volumes.get(name)
        return volume
    except docker.errors.NotFound:
        print(f"Volume '{name}' not found.")
        return None

def mount_volume(name):
    volume = select_volume(name)
    if volume:
        container = client.containers.run(
            'alpine',  # Beispiel-Image (kann an deine Bedürfnisse angepasst werden)
            detach=True,
            name="Docker_Vol_Explorer",
            volumes={volume.name: {'bind': '/data', 'mode': 'rw'}},
            command='tail -f /dev/null'  # Hält den Container am Laufen
        )
        print(f"Volume '{name}' wurde erfolgreich gemountet.")
        return container

def unmount_volume(name):
    volume = select_volume(name)
    if volume:
        containers = client.containers.list(filters={'name': "Docker_Vol_Explorer"})
        for container in containers:
            container.stop()
            container.remove()
        print(f"Volume '{name}' wurde erfolgreich ungemountet.")


def import_data_recursive(container, source_path, target_path):
    x=os.listdir()
    print(x)
#    exec_command = f"ls -A {source_path}"
#    exec_result = container.exec_run(exec_command)
#    file_list = exec_result.output.decode('utf-8').split()
#
#    for item in file_list:
#        if item == '.' or item == '..':
#            continue
#
#        item_path = os.path.join(source_path, item)
#        item_target_path = os.path.join(target_path, item)
#
#        exec_command = f"ls -A {item_path}"
#        exec_result = container.exec_run(exec_command)
#        sub_file_list = exec_result.output.decode('utf-8').split()
#
#        if sub_file_list:
#            os.makedirs(item_target_path, exist_ok=True)
#            if item != "OCI":  # Ausschließen des OCI-Verzeichnisses
#                export_data_recursive(container, item_path, item_target_path)
#        else:
#            exec_command = f"cat {item_path}"
#            exec_result = container.exec_run(exec_command)
#            file_content = exec_result.output
#
#            with open(item_target_path, 'wb') as f:
#                f.write(file_content)
#
#    container.exec_run(f"ls -A {source_path}")  # Zurück zum ursprünglichen Verzeichnis



def export_data_recursive(container, source_path, target_path):
    exec_command = f"ls -A {source_path}"
    exec_result = container.exec_run(exec_command)
    file_list = exec_result.output.decode('utf-8').split()
    print(file_list)
    for item in file_list:
        print(item)
        if item == '.' or item == '..':
            continue

        item_path = os.path.join(source_path, item)
        print(item_path)
        item_target_path = os.path.join(target_path, item)

        if os.path.isdir(item_path):
            os.makedirs(item_target_path, exist_ok=True)
            if item != "OCI":  # Ausschließen des OCI-Verzeichnisses
                export_data_recursive(container, item_path, item_target_path)
        else:
            normalized_item_path = os.path.normpath(item_path)  # Pfad normalisieren
            exec_command = f"cat {normalized_item_path}"
            exec_result = container.exec_run(exec_command)
            print(exec_result)
            if exec_result.exit_code == 0:  # Überprüfen, ob die Ausführung erfolgreich war
                file_content = exec_result.output

                # Entfernen Sie den Ordnerpfad von item_target_path
                relative_item_target_path = item_target_path[len(target_path) + 1:]
                file_target_path = os.path.join(target_path, relative_item_target_path)

                with open(file_target_path, 'wb') as f:
                    f.write(file_content)

                print(exec_result.output.decode('utf-8'))  # Drucken Sie das Ergebnis der cat-Ausgabe
            else:
                print(f"Fehler beim Lesen der Datei: {item_path}")

    container.exec_run(f"ls -A {source_path}")  # Zurück zum ursprünglichen Verzeichnis


def a():

    container = client.containers.get("Docker_Vol_Explorer")
    print(container.name)

    # Beispiel für den Aufruf der Funktion export_data_recursive
    container.exec_run(f"cd /")
    export_data_recursive(container, "data", "expoted_data")

    exit()

def b():
    # Beispielanwendung
    list_volumes()
    volume_name = input("Gib den Namen des Volumes ein: ")
    selected_volume = select_volume(volume_name)
    container = None
    if selected_volume:
        finished = False
        while not finished:
            print(f"Selected Volume: {selected_volume.name}")
            action = input("Möchtest du das Volume mounten (m), unmounten (u) oder auf die Daten zugreifen (a)? (m/u/a): ")
            if action.lower() == "m":
                container = mount_volume(volume_name)
            elif action.lower() == "u":
                unmount_volume(volume_name)
            elif action.lower() == "a":
                if container is not None:
                    path = input("Gib den Pfad zu den Daten ein, auf die du zugreifen möchtest: ")
                    access_volume_data(container, path)
                else:
                    print("Das Volume muss zuerst gemountet werden, um auf die Daten zugreifen zu können.")
            else:
                print("Ungültige Eingabe. Bitte gib 'm' für mounten, 'u' für unmounten oder 'a' für den Datenzugriff ein.")
                continue

            choice = input("Möchtest du weitere Aktionen für das Volume durchführen? (j/n): ")
            if choice.lower() == "n":
                finished = True

a()
