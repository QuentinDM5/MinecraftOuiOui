# -*- coding: utf-8 -*-
import subprocess
import os
import datetime
import time
import logging
import tarfile
from dotenv import load_dotenv
"""
Script permettant de lancer et gérer le serveur Minecraft OuiOui ainsi que ses backups.
"""

#region Initialisation
# Charger des variables d'environnement depuis le fichier .env
load_dotenv()
#endregion

#region Classes
class MissingEnvValue(Exception):
    """
    Exception personnalisée pour les erreurs liées à l'absence de valeur pour une variable d'environnement.
    """

class MissingCompressionResultException(Exception):
    """
    Exception personnalisée pour les erreurs liées à l'absence de résultat suite à une compression.
    """
#endregion

#region Fonctions utilitaires
def handle_exception(error_message: str, exception: Exception=None):
    """
    Gère une exception avec un message d'erreur. Cela afin d'insérer le message complet de l'erreur dans les fichiers log tout en faisant un raise.
    """
    if exception is not None:
        error_message = " -> ".join([error_message, str(exception)])

    logging.error(error_message)
    raise Exception(error_message)

def get_env_value(env_name: str) -> str:
    """
    Renvoie la valeur issue de la variable d'environnement dont le nom fut donné en gérant l'absence de valeur.
    """
    if env_name is None or "":
        handle_exception(f"\"{env_name}\" n'est pas un nom de variable d'environnement valide.")

    env_value = os.getenv(env_name)

    if env_value is None:
        raise MissingEnvValue(f"Aucune valeur définie pour la variable d'environnement \"{env_name}\"")
    
    return env_value

def compress_directory(directory_path, output_filename):
    """
    Compresse au format .tar.gz le directory_path reçu pour générer l'output_filename avec un niveau de compression maximal.
    """
    # Vérifier que le dossier entrant existe bien
    if not os.path.exists(directory_path):
        handle_exception(f"Le dossier à compresser \"{directory_path}\" n'existe pas.")
    
    # Vérifier que le dossier entrant est bien un dossier
    if not os.path.isdir(directory_path):
        handle_exception(f"Le chemin \"{directory_path}\" ne correspond pas à un dossier.")
    
    try:
        logging.info(f"Compression du dossier {directory_path} en cours...")
        # Utilisation de l'outil tar avec l'option -z pour la compression gzip et -9 pour le niveau de compression maximum
        with tarfile.open(output_filename, 'w:gz', compresslevel=9) as tar:
            tar.add(directory_path, arcname=os.path.basename(directory_path))
        logging.info(f"Compression du dossier {directory_path} réussie. Archive créée : {output_filename}")
    except subprocess.CalledProcessError as e:
        handle_exception(f"Une erreur s'est produite lors de la compression du dossier {directory_path}: {str(e)}")
#endregion

#region Fonctions du programme principal
def init_logger():
    """
    Initialise le logger.

    """
    # Récupérer les variables de configuration depuis celles d'environnement
    logs_path = get_env_value("LOGS_LAUNCHER_PATH")

    # Si le dossier de logs n'existe pas, le créer
    if not os.path.exists(logs_path):
        os.makedirs(logs_path)

    # Créer le nom du fichier de log en fonction de la date et de l'heure actuelle
    current_datetime = datetime.datetime.now()
    log_filename = f"log_launcher_{current_datetime.strftime('%Y%m%d_%H%M%S')}.log"

    # Générer le chemin complet pour le nouveau fichier de log
    log_fullpath = os.path.join(logs_path, log_filename)

    # Configuration du logger
    #logging.basicConfig(filename=log_fullpath, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', encoding='utf-8') #Retrait pour Python 3.8.2
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    file_handler = logging.FileHandler(log_fullpath, mode='w', encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

def handle_backups():
    """
    Gère les backups du serveur Minecraft.
    Elle supprime les vieilles backups et génère de nouvelles si nécessaire.
    """
    logging.info("Début du processus de backups.")

    # Récupérer les variables de configuration depuis celles d'environnement
    minecraft_server_path = get_env_value("MINECRAFT_SERVER_PATH")
    backups_path = get_env_value("BACKUPS_PATH")
    nb_days_before_delete = int(get_env_value("NB_DAYS_BEFORE_DELETE_BACKUP"))
    nb_hours_before_new = int(get_env_value("NB_HOURS_BEFORE_NEW_BACKUP"))

    # Si le dossier de backups n'existe pas, le créer
    if not os.path.exists(backups_path):
        os.makedirs(backups_path)
        logging.info(f"Le dossier {backups_path} a été créé.")

    # Récupération du datetime actuelle
    now = datetime.datetime.now()

    # Récupérer les backups et initialiser qu'aucune backup n'est nécessaire
    backups_files = os.listdir(backups_path)
    is_backup_needed = False

    # Si aucune backup préexistante, alors une backup est nécessaire
    if len(backups_files) <= 0:
        logging.info("Aucune backup présente, sa génération est donc nécessaire.")
        is_backup_needed = True
        
    # Si backup non nécessaire (donc s'il y en a des préexistantes)
    if not is_backup_needed:
        # Initialiser qu'il n'y a pas de backup récente
        is_there_a_recent_backup = False

        # Ranger les backups préexistantes
        for backup_file in os.listdir(backups_path):
            backup_path = os.path.join(backups_path, backup_file)
        
            # Vérifier si le fichier est un dossier compressé
            if backup_file.endswith('.tar.gz'):
                # Récupérer la date de création du fichier
                creation_date = datetime.datetime.fromtimestamp(os.path.getctime(backup_path))
                
                # Si la backup date de plus de nb_days_before_delete jours
                if now - creation_date > datetime.timedelta(days=nb_days_before_delete):
                    # Supprimer la backup
                    os.remove(backup_path)
                    logging.info(f"Le fichier {backup_file} a été supprimé car il date de plus de {nb_days_before_delete} jour(s).")
                # Sinon, si la backup date de moins de nb_hours_before_new heures
                elif now - creation_date < datetime.timedelta(hours=nb_hours_before_new):
                    # Spécifier qu'une backup récente existe
                    logging.info(f"La backup {backup_file} a été créée il y a moins de {nb_hours_before_new} heure(s).")
                    is_there_a_recent_backup = True
            else:
                logging.info(f"Le fichier {backup_file} n'est pas un fichier .tar.gz.")

        is_backup_needed = not is_there_a_recent_backup

    # Si backup nécessaire (donc s'il y en a aucune qui date de moins de nb_hours_before_new heures)
    if is_backup_needed:
        # Générer le nom de la backup
        backup_filename = f"backup_OuiOui_{now.strftime('%Y%m%d_%H%M%S')}.tar.gz"

        # Générer le path pour la nouvelle backup
        new_backup_path = os.path.join(backups_path, backup_filename)

        # Générer la backup
        compress_directory(minecraft_server_path, new_backup_path)

    logging.info("Fin du processus de backups.")


#def handle_minecraft_server() -> str | None: #Retrait pour Python 3.8.2
def handle_minecraft_server() -> str:
    """
    Gère le serveur Minecraft.
    Il démarre le serveur, l'éteint à l'heure donnée en config, appelle le backups_handler, puis recommence.
    """
    logging.info("Début du processus pour la gestion du serveur Minecraft.")
    # Déclaration pour la valeur de retour en cas d'erreur
    return_value = None

    # Obtenir la date du jour en tant que dernier redémarrage
    last_reboot_date = datetime.date.today()

    # Récupérer les valeurs de configuration pour le serveur Minecraft
    minecraft_server_path = get_env_value("MINECRAFT_SERVER_PATH")
    time_when_reboot = get_env_value("TIME_WHEN_REBOOT")
    java_exe_path = get_env_value("JAVA_EXE_PATH")
    max_ram_gb = int(get_env_value("MAX_RAM_GB"))
    min_ram_gb = int(get_env_value("MIN_RAM_GB"))
    minecraft_server_jar_path = get_env_value("MINECRAFT_SERVER_JAR_PATH")

    # Constituer la commande à lancer
    fullLaunchCommand = f"{java_exe_path} -Xmx{max_ram_gb}G -Xms{min_ram_gb}G -jar {minecraft_server_jar_path} nogui"

    # Lancer du serveur Minecraft en tant que sous-processus
    server_process = None
    try:
        try:
            server_process = subprocess.Popen(fullLaunchCommand.split(), cwd=minecraft_server_path)
            logging.info(f"Serveur Minecraft démarré à {datetime.datetime.now()} avec la commande {fullLaunchCommand}")
        except Exception as e:
            handle_exception(f"Impossible de démarrer (1ère fois) le serveur Minecraft à {datetime.datetime.now()} avec la commande {fullLaunchCommand}", e)
        
        # Vérifier que le processus fut bien récupéré avant de boucler
        if server_process is not None:
            logging.info(f"En attente de {time_when_reboot} après le {last_reboot_date} pour le redémarrage automatique...")

            # Initialisation du nombre de redémarrages
            nb_reboots = 0

            # Boucler sur le redémarrage automatique et la gestion des backups du serveur Minecraft
            while True:
                # Récupérer les informations temporelles actuelles
                current_date = datetime.date.today()
                current_time = time.strftime("%H:%M")

                # Si le processus lié au serveur s'est terminé de lui-même
                returncode = server_process.poll()
                if returncode != None and returncode != 0:
                    handle_exception(f"Le sous-processus du serveur Minecraft s'est interrompu avec le code de retour -> {returncode}")

                # S'il est actuellement un jour différent de celui du dernier redémarrage et qu'il est l'heure de redémarrer
                if current_date != last_reboot_date and current_time == time_when_reboot:
                    logging.info(f"Il est {time_when_reboot} après {last_reboot_date} -> Extinction du serveur Minecraft...")

                    # La date du dernier redémarrage est désormais celui de la date courante et incrémentation du nombre de redémarrages
                    last_reboot_date = current_date
                    nb_reboots = nb_reboots + 1

                    # Arrêter le processus
                    server_process.terminate()
                    server_process.wait()  # Attendre que le processus se termine
                    logging.info("Serveur Minecraft éteint.")

                    # Gérer les backups liées au serveur
                    handle_backups()

                    # Récupérer à nouveau les valeurs de la configuration (au cas où elles auraient été modifiées entre-temps sans couper le service)
                    time_when_reboot = get_env_value("TIME_WHEN_REBOOT")
                    java_exe_path = get_env_value("JAVA_EXE_PATH")
                    max_ram_gb = int(get_env_value("MAX_RAM_GB"))
                    min_ram_gb = int(get_env_value("MIN_RAM_GB"))
                    minecraft_server_jar_path = get_env_value("MINECRAFT_SERVER_JAR_PATH")

                    # Constituer la commande à lancer
                    fullLaunchCommand = f"{java_exe_path} -Xmx{max_ram_gb}G -Xms{min_ram_gb}G -jar {minecraft_server_jar_path} nogui"

                    # Relancer le serveur Minecraft en tant que sous-processus
                    try:
                        server_process = subprocess.Popen(fullLaunchCommand.split(), cwd=minecraft_server_path)
                        logging.info(f"Serveur Minecraft redémarré pour la {nb_reboots}ère/ème fois à {datetime.datetime.now()} avec la commande {fullLaunchCommand}")
                    except Exception as e:
                        handle_exception(f"Impossible de redémarrer le serveur Minecraft à {datetime.datetime.now()} avec la commande {fullLaunchCommand}.", e)
                    
                    # Vérifier que le processus fut bien récupéré
                    if server_process is None:
                        handle_exception("Le processus n'a pas su être récupéré lors du redémarrage.")
                        
                    logging.info(f"En attente de {time_when_reboot} après le {last_reboot_date} pour le redémarrage automatique...")
                else:
                    seconds_between_checks = int(get_env_value("SECONDS_BETWEEN_CHECKS"))
                    # Attendre seconds_between_checks secondes avant de vérifier à nouveau quand redémarrer
                    time.sleep(seconds_between_checks)
        else:
            handle_exception("Le processus n'a pas su être récupéré lors du premier lancement.")
    except Exception as e:
        error_message = f"La gestion du serveur et de ses backups a dû être interrompue. -> {e}"
        logging.error(error_message)
        return_value = error_message
    finally:
        # Si le processus du serveur Minecraft tourne encore
        if server_process is not None and server_process.poll() is None:
            logging.info("Tentative d'extinction propre du serveur Minecraft...")
            server_process.terminate()
            server_process.wait()
            logging.info("Extinction propre du serveur Minecraft réussie.")

    return return_value
#endregion

#region Programme principal
def main():
    """
    Programme principal, gérant le logging, les backups et le serveur Minecraft.
    """
    # Initialisation du logger
    init_logger()
    logging.info("Initialisation du logger réussie, début du Launcher.")

    # Gestion des backups
    handle_backups()

    # Lancement et gestion du serveur Minecraft
    result_server = handle_minecraft_server()

    # Gérer l'éventuelle erreur reçue depuis la gestion du serveur Minecraft
    if result_server is not None:
        handle_exception(result_server)

    logging.info("Fin du Launcher.")


if __name__ == "__main__":
    main()
#endregion
