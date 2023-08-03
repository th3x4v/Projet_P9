# Openclassroom Projet 04
Projet réalisé dans le cadre de ma formation OpenClassrooms Développeur d'Applications Python.  
Il s'agit d'une application web réalisée avec Django pour une société fictive, LitReviews.  
L'application est un réseau social permettant de demander et poster des critiques de livres.

## Fonctionnalités

- Se connecter et s'inscrire ;
- Consulter son profil et le modifier, ajouter une image de profil ;
- Consulter un flux contenant les tickets et critiques des utilisateurs auxquels on est abonné ;
- Créer des tickets de demande de critique ;
- Créer des critiques, en réponse ou non à des tickets ;
- Voir ses propres posts, les modifier ou les supprimer ;
- Suivre d'autres utilisateurs, ou se désabonner.

## Installation

Installer Python : https://www.python.org/downloads/ 
 
Lancez ensuite la console, placez vous dans le dossier de votre choix puis clonez ce repository:
```
git clone https://github.com/th3x4v/Projet_P9.git
```
Placez vous dans le dossier Projet_P9, puis créez un nouvel environnement virtuel:
```
python -m venv venv
```
Ensuite, activez-le.
Windows:
```
venv\scripts\activate.bat
```
Linux:
```
source venv/bin/activate
```
Installez ensuite les packages requis:
```
pip install -r requirements.txt
```
Ensuite, placez vous à la racine du projet (là ou se trouve le fichier manage.py), puis effectuez les migrations:
```
python manage.py makemigrations
```
Puis: 
```
python manage.py migrate
```
Il ne vous reste plus qu'à lancer le serveur: 
```
python manage.py runserver
```
Vous pouvez ensuite utiliser l'applicaton à l'adresse suivante:
```
http://127.0.0.1:8000/LITReviews/home/
```