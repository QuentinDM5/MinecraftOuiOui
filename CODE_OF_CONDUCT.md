# Code de conduite

## Pour le développement

### Utilisation de branches DEV

Nous développons **toujours** dans les branches sous le dossier **DEV**. La branche principale pour développer est donc **[DEV/main](https://github.com/QuentinDM5/MinecraftOuiOui_Config/tree/DEV/main)**. 

**Lors de modifications majeures**, il est conseillé de créer une **sous-branche à partir de [DEV/main](https://github.com/QuentinDM5/MinecraftOuiOui_Config/tree/DEV/main)** puis de créer des pull requests pour les merger dans cette dernière. 

Lorsque les **modifications intégrées dans [DEV/main](https://github.com/QuentinDM5/MinecraftOuiOui_Config/tree/DEV/main) sont valides**, on génère un **pull request** pour la branche **[main](https://github.com/QuentinDM5/MinecraftOuiOui_Config/tree/main)**. Assurons-nous d'avoir des **messages clairs** au sein des pull requests pour être certain de ce que nous avons implémenté et pour s'y retrouver plus aisément dans le temps.

### Sécurisation des données sensibles

**Lors de l'utilisation de fichier contenant des données sensibles** de configuration (*par exemple les fichiers .env*), il faut, avant le commit, **les ajouter au [.gitignore](https://github.com/QuentinDM5/MinecraftOuiOui_Config/blob/main/.gitignore)** et **créer un fichier .env_exemple** avec des données bidons. Cela afin d'éviter la transmission des données sensibles tout en permettant de faciliter le développement.

Il faut gérer le développement de sortes à ce que les **données de configuration sensibles soient distinguables du reste**. Cela dans le but de pouvoir les ajouter aisément au [.gitignore](https://github.com/QuentinDM5/MinecraftOuiOui_Config/blob/main/.gitignore).