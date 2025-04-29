# Importer les modules nécessaires
from flask import Blueprint, request, jsonify
# Importer l'instance Neo4j
from app import graph
from app.models import User
# Importer le module NodeMatcher de py2neo pour les requêtes Neo4j
from py2neo import NodeMatcher
# Ajout pour la validation d' email
import re

# Création d'un Blueprint Flask pour les routes utilisateurs
users_bp = Blueprint('users', __name__)
# Initialisation du NodeMatcher pour interroger les noeuds dans Neo4j 
matcher = NodeMatcher(graph)

def validate_email(email):
    # Valider le format d'un email
    email_regex = r"[^@]+@[^@]+\.[^@]+"
    return re.match(email_regex, email)

# Route pour récupérer tous les utilisateurs
@users_bp.route('/users', methods=['GET'])
def get_users():
    query = "MATCH (u:User) RETURN u"
    result = graph.run(query).data()
    return jsonify([dict(user['u']) for user in result]), 200


# Route pour créer un nouvel utilisateur
@users_bp.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    if not data or 'name' not in data or 'email' not in data:
        return jsonify({"error": "Missing name or email"}), 400
    
    # Vérification du format de l'email
    if not validate_email(data['email']):
        return jsonify({"error": "Invalid email format"}), 400
    
    # Vérification de la longueur du nom
    if len(data['name']) < 3 or len(data['name']) > 50:
        return jsonify({"error": "Name must be between 3 and 50 characters"}), 400
    
    # Vérifier si l'email existe déjà
    existing_user = graph.nodes.match("User", email=data['email']).first()
    if existing_user:
        return jsonify({"error": "Email already exists"}), 400
    
    try:        
        user = User.create(graph, data['name'], data['email'])
        return jsonify(dict(user)), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Route pour récupérer un utilisateur par son ID
@users_bp.route('/users/<string:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.find_by_id(graph, user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(dict(user)), 200

# Route pour mettre à jour un utilisateur
@users_bp.route('/users/<string:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json()

    user = User.find_by_id(graph, user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Validation des champs si présents
    if 'email' in data:
        if not validate_email(data['email']):
            return jsonify({"error": "Invalid email format"}), 400
        # Vérifier que l'email n'est pas déjà utilisé par un autre utilisateur
        existing = graph.nodes.match("User", email=data['email']).where(f"_.id <> '{user_id}'").first()
        if existing:
            return jsonify({"error": "Email already exists"}), 409
        
    if 'name' in data and (len(data['name']) < 3 or len(data['name']) > 50):
        return jsonify({"error": "Name must be between 3 and 50 characters"}), 409
    
    try:
        update_user = User.update(graph, user_id, **data)
        return jsonify(dict(update_user)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

# Route pour supprimer un utilisateur
@users_bp.route('/users/<string:user_id>', methods=['DELETE'])
def delete_user(user_id):
    if not User.delete(graph, user_id):
        return jsonify({"error": "User not found"}), 404
    return jsonify({"message": "User deleted"}), 200


# Route pour récupérer les amis d'un utilisateur
@users_bp.route('/users/<string:user_id>/friends', methods=['GET'])
def get_friends(user_id):
    query = """
    MATCH (u:User {id: $user_id})-[:FRIENDS_WITH]-(f:User)
    RETURN f
    """
    result = graph.run(query, user_id=user_id).data()
    return jsonify([dict(friend['f']) for friend in result]), 200


# Route pour ajouter un ami
@users_bp.route('/users/<string:user_id>/friends', methods=['POST'])
def add_friend(user_id):
    data = request.get_json()
    if not data or 'friend_id' not in data:
        return jsonify({"error": "Missing friend_id"}), 400
    
    rel = User.add_friend(graph, user_id, data['friend_id'])
    if not rel:
        return jsonify({"error": "User or friend not found"}), 404
    return jsonify({"message": "Friend added"}), 201


# Route pour supprimer un ami
@users_bp.route('/users/<string:user_id>/friends/<string:friend_id>', methods=['DELETE'])
def remove_friend(user_id, friend_id):
    query = """
    MATCH (u:User {id: $user_id})-[r:FRIENDS_WITH]-(f:User {id: $friend_id})
    WITH r
    LIMIT 1
    DELETE r
    RETURN COUNT(r) AS deleted
    """
    result = graph.run(query, user_id=user_id, friend_id=friend_id).data()
    if result and result[0]['deleted'] > 0:
        return jsonify({"message": "Friendship removed"}), 200
    else:
        return jsonify({"error": "Friendship not found"}), 404

# Route pour vérifier si deux utilisateurs sont amis
@users_bp.route('/users/<string:user_id>/friends/<string:friend_id>', methods=['GET'])
def check_friends(user_id, friend_id):
    query = """
    MATCH (u:User {id: $user_id})-[r:FRIENDS_WITH]-(f:User {id: $friend_id})
    RETURN COUNT(r) > 0 as are_friends
    """
    result = graph.run(query, user_id=user_id, friend_id=friend_id).data()
    return jsonify({"are_friends": result[0]['are_friends']}), 200


# Route pour récupérer les amis communs entre deux utilisateurs
@users_bp.route('/users/<string:user_id>/mutual-friends/<string:other_id>', methods=['GET'])
def get_mutual_friends(user_id, other_id):
    query = """
    MATCH (u1:User {id: $user_id})-[:FRIENDS_WITH]-(mutual:User)-[:FRIENDS_WITH]-(u2:User {id: $other_id})
    RETURN mutual
    """
    result = graph.run(query, user_id=user_id, other_id=other_id).data()
    return jsonify([dict(friend['mutual']) for friend in result]), 200
