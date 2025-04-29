from flask import Blueprint, request, jsonify
# Importer l'instance Neo4j depuis app
from app import graph
from app.models import Post

# Création d'un Blueprint Flask pour les routes des posts
posts_bp = Blueprint('posts', __name__)

# Route pour récupérer tous les posts
@posts_bp.route('/posts', methods=['GET'])
def get_posts():
    query = "MATCH (p:Post) RETURN p"
    result = graph.run(query).data()
    return jsonify([dict(post['p']) for post in result]), 200


# Route pour récupérer un post spécifique par son ID
@posts_bp.route('/posts/<string:post_id>', methods=['GET'])
def get_post(post_id):
    post = Post.find_by_id(graph, post_id)
    if not post:
        return jsonify({"error": "Post not found"}), 404
    return jsonify(dict(post)), 200


# Route pour récupérer tous les posts d'un utilisateur spécifique
@posts_bp.route('/users/<string:user_id>/posts', methods=['GET'])
def get_user_posts(user_id):
    query = """
    MATCH (u:User {id: $user_id})-[:CREATED]->(p:Post)
    RETURN p
    """
    result = graph.run(query, user_id=user_id).data()
    return jsonify([dict(post['p']) for post in result]), 200


# Route pour créer un nouveau post pour un utilisateur spécifique
@posts_bp.route('/users/<string:user_id>/posts', methods=['POST'])
def create_post(user_id):
    data = request.get_json()
    if not data or 'title' not in data or 'content' not in data:
        return jsonify({"error": "Missing title or content"}), 400
    
    # Validation de la longueur des champs
    if len(data['title']) < 5 or len(data['title']) > 100:
        return jsonify({"error": "Title must be between 5 and 100 characters"}), 400
    
    if len(data['content']) < 10 or len(data['content']) > 2000:
        return jsonify({"error": "Content must be between 10 and 2000 characters"}), 400
        
    try:
        post = Post.create(graph, data['title'], data['content'], user_id)
        if not post:
            return jsonify({"error": "User not found"}), 404
        return jsonify(dict(post)), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Route pour mettre à jour un post existant
@posts_bp.route('/posts/<string:post_id>', methods=['PUT'])
def update_post(post_id):
    data = request.get_json()
    post = Post.find_by_id(graph, post_id)
    if not post:
        return jsonify({"error": "Post not found"}), 404
    
    # Validation des champs si présents
    if 'title' in data and (len(data['title']) < 5 or len(data['title']) > 100):
        return jsonify({"error": "Title must be between 5 and 100 characters"}), 400
    
    if 'content' in data and (len(data['content']) < 10 or len(data['content']) > 2000):
        return jsonify({"error": "Content must be between 10 and 2000 characters"}), 400
    
    try:
        updated_post = Post.update(graph, post_id, **data)
        return jsonify(dict(updated_post)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Route pour supprimer un post
@posts_bp.route('/posts/<string:post_id>', methods=['DELETE'])
def delete_post(post_id):
    if not Post.delete(graph, post_id):
        return jsonify({"error": "Post not found"}), 404
    return jsonify({"message": "Post deleted"}), 200


# Route pour ajouter un like à un post
@posts_bp.route('/posts/<string:post_id>/like', methods=['POST'])
def like_post(post_id):
    data = request.get_json()
    if not data or 'user_id' not in data:
        return jsonify({"error": "Missing user_id"}), 400
    
    rel = Post.add_like(graph, data['user_id'], post_id)
    if not rel:
        return jsonify({"error": "User or post not found"}), 404
    return jsonify({"message": "Post liked"}), 201


# Route pour retirer un like d'un post
@posts_bp.route('/posts/<string:post_id>/like', methods=['DELETE'])
def unlike_post(post_id):
    data = request.get_json()
    if not data or 'user_id' not in data:
        return jsonify({"error": "Missing user_id"}), 400
    
    query = """
    MATCH (u:User {id: $user_id})-[r:LIKES]->(p:Post {id: $post_id})
    DELETE r
    RETURN COUNT(r) as deleted
    """
    result = graph.run(query, user_id=data['user_id'], post_id=post_id).data()
    if result[0]['deleted'] == 0:
        return jsonify({"error": "Like not found"}), 404
    return jsonify({"message": "Like removed"}), 200