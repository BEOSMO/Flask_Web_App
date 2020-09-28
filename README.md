# Connecter une application Flask à Postgresql 

Dans cet exercice, nous allons tenter de connecter notre application à la base de données que nous avons créé précédemment. 
Le but va être de simplement stocker les différentes prédictions que l'utilisateur fait pour un salaire donné


## Le fichier de départ 

Dans le dossier `Exercices`, repartez du dossier `linear_regression_with_flask - NO BDD`. Clonez le dossier quelque part pour pouvoir le manipuler. 


## Ajouter un fichier config.py

Pour commencer, nous avons besoin d'ajouter un fichier `config.py`. Ce fichier va servir à sauvegarder nos différentes configurations en fonction de si notre application est en production ou en test. 

1. Créez donc le fichier `config.py` au niveau dossier racine 
2. Ajoutez le code suivant : 
    ```python 
    import os
    basedir = os.path.abspath(os.path.dirname(__file__))

    class Config(object):
        DEBUG = False
        TESTING = False
        CSRF_ENABLED = True
        SECRET_KEY = 'this-really-needs-to-be-changed'
        SQLALCHEMY_DATABASE_URI = os.environ["DBHOST"]

    class ProductionConfig(Config):
        DEBUG = False
        SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://{dbuser}:{dbpass}@{dbhost}/{dbname}'.format(
        dbuser=os.environ['DBUSER'],
        dbpass=os.environ['DBPASS'],
        dbhost=os.environ['DBHOST'],
        dbname=os.environ['DBNAME']
    )

    class StagingConfig(Config):
        DEVELOPMENT = True
        DEBUG = True

    class DevelopmentConfig(Config):
        DEVELOPMENT = True
        DEBUG = True
        SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://{dbuser}:{dbpass}@{dbhost}/{dbname}'.format(
        dbuser=os.environ['DBUSER'],
        dbpass=os.environ['DBPASS'],
        dbhost=os.environ['DBHOST'],
        dbname=os.environ['DBNAME']
        )

    class TestingConfig(Config):
        TESTING = True
    ```

Ce code nous permet de définir notre environnement ("production", "test", "development" etc.) ainsi que de nous connecter à notre base de données. Vous voyez d'ailleurs que nous n'avons pas mis de valeur, mais plutôt `os.environ["VARIABLE"]`. Ceci est ce qu'on appelle une [variable d'environnment](https://www.journaldev.com/24935/python-set-environment-variable), que nous expliquerons plus tard dans l'exercice. 


## Configuration de `app.py`

Maintenant que nous avons notre fichier de configuration, il va falloir que nous ajoutions quelques petites choses dans notre fichier `app.py`. Tout d'abord, nous allons devoir préciser si nous sommes dans un mode production ou dans un mode test, puis nous aurons besoin d'instancier notre gestionnaire de bases de données qu'on appelle SQLAlchemy 

1. Dans `app.py`, importez 
    * `from sql_alchemy import SQLAlchemy`
    * NB : cette librairie est le gestionnaire de base de données en Python. Elle est extrêmement pratique d'utilisation ! 
    * NBB : il est possible que vous ayez besoin de faire un `pip install sql_alchemy`

2. En dessous de votre variable `app`, ajoutez le code suivant :
    ```python 
    app.config.from_object(os.environ["APP_SETTINGS"])
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db = SQLAlchemy(app)
    ```

    * NB : ceci nous permet de configurer notre application. En fonction de la variable d'environnment `APP_SETTINGS`, vous pourrez spécifier le mode que vous souhaitez avoir pour votre application (test ou production)

3. Enfin, dans votre fonction `predict()`, ajoutez avant le `return`:
    ```python
        result = Result(
        YearsExperience = float(yearsExperience),
        Prediction = float(prediction)
    )
    db.session.add(result)
    db.session.commit()
    ```

    * NB : Ceci va nous permettre d'ajouter une nouvelle ligne dans notre base de données (que nous n'avons pas encore définie)



## Création du schéma de la base de données via `models.py`

Il va falloir maintenant que nous précisions le modèle de notre base de données dans un fichier. Pour cela, procédez de la manière suivante : 

1. Créez un fichier `models.py` au niveau de votre dossier racine. 
2. Ajoutez le code suivant : 
    ```python 
    from app import db

    class Result(db.Model):
        __tablename__ = "LinRegResults"

        id = db.Column(db.Integer, primary_key = True)
        YearsExperience = db.Column(db.Float)
        Prediction = db.Column(db.Float)

        def __init__(self, YearsExperience, Prediction):
            self.YearsExperience = YearsExperience
            self.Prediction = Prediction
    ```

Ce code permet de définir 3 colonnes : 
    * id 
    * YearsExperience
    * Prediction 

La suite aura pour but d'initialiser la base de données. 


## Enfin `manage.py`

Pour terminer, nous avons besoin de créer un nouveau fichier qui va nous servir de `manager`. Nous allons pouvoir à la fois gérer notre application mais aussi créer ce qu'on appelle des migrations de bases de données. En effet, à chaque fois que vous faites des changements, vous aurez besoin de *migrer* votre base. Apprenons donc à le faire comme suit :

1. Créez un fichier `manage.py`
2. Insérez le code suivant : 
    ```python 
    import os
    from flask_script import Manager
    from flask_migrate import Migrate, MigrateCommand

    from app import app, db

    migrate = Migrate(app, db)
    manager = Manager(app)

    manager.add_command('db', MigrateCommand)

    if __name__ == '__main__':
        manager.run()
    ```

    * NB : N'oubliez pas que vous aurez surement besoin de faire 
        * `pip install flask_script`
        * `pip install flask_migrate`

On est tout bon ! Il ne nous manque que quelques étapes...


## Wrap up all together ! 

Si tout s'est bien passé, vous devriez pouvoir faire les choses suivantes pour que tout fonctionne :

1. Exportez vos variables d'environnement dans votre console en faisant :
    * `export VARIABLE_NAME='VARIABLE_PASS`
    * Exemple : `(export) set DBUSER='oslane_b@jedha-bootcamp-postgresql'`
    * NB : Pour la variable `DBNAME`, vous devrez créer une base de données à l'intérieur de votre instance Postgresql. Si vous ne l'avez pas encore fait, créez en une via PGADMIN. 

2. Vous aurez besoin d'exporter la variable `APP_SETTINGS` pour laquelle vous aurez besoin de donner l'environement que vous souhaitez. Pour cette fois, faites :
    * `(export) set APP_SETTINGS="config.ProductionConfig"`

3. Vous aurez besoin de migrer les modifications dans votre base de données. Exécutez donc les commandes suivantes :
    * `python manage.py db init`
    * `python manage.py db migrate`
    * `python manage.py db upgrade`

4. Enfin, si tout est okay, faites : `python manage.py runserver`. Si tout a fonctionné, votre application devrait tourner. 

NB : Il est tout à fait normal que vous ayiez encore quelques erreurs. Soyez patient, regardez les erreurs que vous sort votre console et avancez par itérations :) 




* set DBUSER=oslane_b@jedha-bootcamp-postgresql   Admin username
* set DBPASS=051081912Gh$   Mot de passe que vous avez créé
* set DBHOST=jedha-bootcamp-postgresql.postgres.database.azure.com   Server name
* set DBNAME=FlaskBdd   le nom de la base de données créé dans votre instance PostgreSQL grâce à PG Admin
* set APP_SETTINGS=config.ProductionConfig

*    dbuser=os.environ['oslane_b@jedha-bootcamp-postgresql'],
*    dbpass=os.environ['051081912Gh$'],
*    dbhost=os.environ['jedha-bootcamp-postgresql.postgres.database.azure.com']
*    dbname=os.environ['FlaskBdd']