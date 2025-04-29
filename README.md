# 🚀 API Flask avec Neo4j - Gestion de Réseau Social

Ce projet implémente une API RESTful avec Flask et Neo4j pour gérer des utilisateurs, leurs posts et commentaires avec un système de relations sociales.

1) **Neo4j**:
Neo4j est une base de données orientée graphe qui stocke les données sous forme de nœuds, de relations et de propriétés. Contrairement aux bases de données relationnelles traditionnelles qui utilisent des tables, Neo4j est optimisée pour représenter et interroger des données fortement interconnectées.

2) **Flask**:
Flask est un micro-framework web Python léger et flexible pour construire des applications web et des API RESTful.

3) **py2neo**:
py2neo est une bibliothèque Python qui permet d'interagir avec une base de données Neo4j. Elle fournit une interface Pythonique pour exécuter des requêtes Cypher et manipuler les données sous forme d'objets Python.

## 📋 Table des matières
- [Prérequis](#-prérequis)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Structure du Projet](#-structure-du-projet)
- [Routes API](#-routes-api)
- [Exemples de Requêtes](#-exemples-de-requêtes)
- [Tests](#-tests)
- [Livrables](#-livrables)

## ⚙️ Prérequis
- Python 3.8+
- Docker
- Neo4j (via Docker)
- py2neo 
- Flask
- Postman (pour tester l'API)
- Github (dépôt)

## 🛠 Installation
1. **Cloner le dépôt**
   ```bash
   git clone [votre-repo-url]
   cd [nom-du-projet]

    ``1. Configurer l'environnement virtuel``
    python -m venv venv
    
    source venv/bin/activate  # Linux/Mac
    
    venv\Scripts\activate    # Windows

    ``2. Installer les dépendances``
    pip install -r requirements.txt

    ``3. Lancer Neo4j avec Docker``
    docker-compose up -d

    ``4. Lancer l'application``
    python run.py


## 🔧Configuration

Créez un fichier .env à la racine :

NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
FLASK_DEBUG=1
FLASK_HOST=0.0.0.0
FLASK_PORT=5000

## 📂 Structure du Projet

PythonProject/
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── routes/
│   │   ├── users.py
│   │   ├── posts.py
│   │   └── comments.py
├── venv (rep à l'inter)  
├── .env
├── docker-compose.yml
├── README.md
├── requirements.txt
└── run.py

## 🌐 Routes API
👥 Utilisateurs

    GET /users - Lister tous les utilisateurs

    POST /users - Créer un utilisateur

    GET /users/<id> - Obtenir un utilisateur

    PUT /users/<id> - Mettre à jour un utilisateur

    DELETE /users/<id> - Supprimer un utilisateur

    POST /users/<id>/friends - Ajouter un ami

    GET /users/<id>/friends - Lister les amis

📝 Posts

    GET /posts - Lister tous les postes

    POST /users/<user_id>/posts - Créer un poste

    POST /posts/<post_id>/like - Aimer un poste

💬 Commentaires

    GET /comments - Récupère tous les commentaires du système

    GET /comments/<comment_id> - Récupère un commentaire par son ID

    PUT /comments/<comment_id> - Mettre à jour un commentaire

    DELETE /comments/<comment_id> - Supprimer un commentaire

    POST /posts/<post_id>/comments - Ajouter un commentaire

    GET /posts/<post_id>/comments - Lister les commentaires

    POST /comments/<comment_id>/like - Aimer un commentaire

    DELETE /posts/<post_id>/comments/<comment_id> - Supprimer un commentaire spécifique à un post

    DELETE /comments/<comment_id>/like - Retirer un like d'un commentaire


## 📡 Exemples de Requêtes

1) Créer un utilisateur

curl -X POST http://localhost:5000/api/users \
-H "Content-Type: application/json" \
-d '{"name": "Alice", "email": "alice@example.com"}'

2) Récupérer un utilisateur

curl http://localhost:5000/api/users/[user_id]

3) Créer un post

curl -X POST http://localhost:5000/api/users/1/posts \
-H "Content-Type: application/json" \
-d '{"title": "Mon premier post", "content": "Bonjour le monde!"}'

4) Liker un post

curl -X POST http://localhost:5000/api/posts/[post_id]/like \
  -H "Content-Type: application/json" \
  -d '{"user_id":"[user_id]"}'

5) Ajouter un commentaire

curl -X POST http://localhost:5000/api/posts/[post_id]/comments \
  -H "Content-Type: application/json" \
  -d '{"content":"Super post!","user_id":"[user_id]"}'

6) Supprimer un commentaire

curl -X DELETE http://localhost:5000/api/comments/[comment_id]


## 🧪 Tests
- Vérification des installations : 
python --version
docker --version
pip --version


- Accès
API: http://localhost:5000/api

Neo4j Browser: http://localhost:7474 (user: neo4j, password: password)

**Lancer l'API :**
 python run.py

**Importer la collection Postman (docs/postman_collection.json)**

**Exécuter les tests manuellement ou avec :**
 pytest tests/

## 📦 Livrables

    Code source complet
    Documentation (ce README)
    Collection Postman

📄 Licence

MIT License

✨ Projet réalisé par [Miryam GAKOSSO] - 2025
