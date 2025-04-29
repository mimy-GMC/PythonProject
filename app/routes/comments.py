from flask import Blueprint, request, jsonify
from app import graph
from app.models import Comment

# Création d'un Blueprint Flask pour les routes des commentaires
comments_bp = Blueprint('comments', __name__)

# Route pour récupérer tous les commentaires
@comments_bp.route('/comments', methods=['GET'])
def get_comments():
    query = "MATCH (c:Comment) RETURN c"
    result = graph.run(query).data()
    return jsonify([dict(comment['c']) for comment in result]), 200


# Route pour récupérer un commentaire spécifique par son ID
@comments_bp.route('/comments/<string:comment_id>', methods=['GET'])
def get_comment(comment_id):
    comment = Comment.find_by_id(graph, comment_id)
    if not comment:
        return jsonify({"error": "Comment not found"}), 404
    return jsonify(dict(comment)), 200


# Route pour récupérer les commentaires d'un post spécifique
@comments_bp.route('/posts/<string:post_id>/comments', methods=['GET'])
def get_post_comments(post_id):
    query = """
    MATCH (p:Post {id: $post_id})-[:HAS_COMMENT]->(c:Comment)
    RETURN c
    """
    result = graph.run(query, post_id=post_id).data()
    return jsonify([dict(comment['c']) for comment in result]), 200


# Route pour créer un nouveau commentaire sur un post
@comments_bp.route('/posts/<string:post_id>/comments', methods=['POST'])
def create_comment(post_id):
    data = request.get_json() 

    # Vérification des champs obligatoires
    if not data or 'content' not in data or 'user_id' not in data:
        return jsonify({"error": "Missing content or user_id"}), 400
    
    # Validation de la longueur du contenu
    if len(data['content']) < 5 or len(data['content']) > 1000:
        return jsonify({"error": "Content must be between 5 and 1000 characters"}), 400
    
    try: 
        comment = Comment.create(graph, data['content'], data['user_id'], post_id)
        if not comment:
            return jsonify({"error": "User or post not found"}), 404
        return jsonify(dict(comment)), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Route pour supprimer un commentaire spécifique d'un post
@comments_bp.route('/posts/<string:post_id>/comments/<string:comment_id>', methods=['DELETE'])
def delete_post_comment(post_id, comment_id):
    # Vérifier que le commentaire appartient bien au post
    query = """
    MATCH (p:Post {id: $post_id})-[:HAS_COMMENT]->(c:Comment {id: $comment_id})
    DETACH DELETE c
    RETURN COUNT(c) as deleted
    """
    result = graph.run(query, post_id=post_id, comment_id=comment_id).data()
    if result[0]['deleted'] == 0:
        return jsonify({"error": "Comment not found or doesn't belong to post"}), 404
    return jsonify({"message": "Comment deleted"}), 200


# Route pour mettre à jour un commentaire
@comments_bp.route('/comments/<string:comment_id>', methods=['PUT'])
def update_comment(comment_id):
    data = request.get_json()

    # Vérification que le commentaire existe
    comment = Comment.find_by_id(graph, comment_id)
    if not comment:
        return jsonify({"error": "Comment not found"}), 404
    
    # Validation du contenu si présent
    if 'content' in data and (len(data['content']) < 5 or len(data['content']) > 1000):
        return jsonify({"error": "Content must be between 5 and 1000 characters"}), 400
    
    try:
        comment = Comment.update(graph, comment_id, **data)
        if not comment:
            return jsonify({"error": "Comment not found"}), 404
        return jsonify(dict(comment)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Route pour supprimer un commentaire (version générale, sans vérification de post)
@comments_bp.route('/comments/<string:comment_id>', methods=['DELETE'])
def delete_comment(comment_id):
    if not Comment.delete(graph, comment_id):
        return jsonify({"error": "Comment not found"}), 404
    return jsonify({"message": "Comment deleted"}), 200


# Route pour ajouter un like à un commentaire
@comments_bp.route('/comments/<string:comment_id>/like', methods=['POST'])
def like_comment(comment_id):
    data = request.get_json()
    if not data or 'user_id' not in data:
        return jsonify({"error": "Missing user_id"}), 400
    
    rel = Comment.add_like(graph, data['user_id'], comment_id)
    if not rel:
        return jsonify({"error": "User or comment not found"}), 404
    return jsonify({"message": "Comment liked"}), 201


# Route pour retirer un like d'un commentaire
@comments_bp.route('/comments/<string:comment_id>/like', methods=['DELETE'])
def unlike_comment(comment_id):
    data = request.get_json()
    if not data or 'user_id' not in data:
        return jsonify({"error": "Missing user_id"}), 400
    
    query = """
    MATCH (u:User {id: $user_id})-[r:LIKES]->(c:Comment {id: $comment_id})
    DELETE r
    RETURN COUNT(r) as deleted
    """
    result = graph.run(query, user_id=data['user_id'], comment_id=comment_id).data()
    if result[0]['deleted'] == 0:
        return jsonify({"error": "Like not found"}), 404
    return jsonify({"message": "Like removed"}), 200