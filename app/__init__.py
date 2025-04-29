# Importation des modules nécessaires
# Framework Flask pour créer l'API
from flask import Flask 
from py2neo import Graph
# Importer dotenv pour charger les variables d'environnement depuis .env
from dotenv import load_dotenv
# Pour accéder aux variables d'environnement système
import os

# Chargement des variables d'environnement depuis le fichier .env
load_dotenv()

# Création de l'application Flask
app = Flask(__name__)

# Configuration Neo4j
app.config["NEO4J_URI"] = os.getenv("NEO4J_URI", "bolt://localhost:7687")
app.config["NEO4J_AUTH"] = (
    os.getenv("NEO4J_USER", "neo4j"),
    os.getenv("NEO4J_PASSWORD", "password")
)

# Connexion à la base de données Neo4j
# Graph est l'objet qui permettre d'exécuter les requêtes Cypher
graph = Graph(app.config["NEO4J_URI"], auth=app.config["NEO4J_AUTH"])

# Import des routes
from app.routes import users, posts, comments

# Enregistrement des blueprints avec le préfixe '/api'
app.register_blueprint(users.users_bp, url_prefix='/api')
app.register_blueprint(posts.posts_bp, url_prefix='/api')
app.register_blueprint(comments.comments_bp, url_prefix='/api')