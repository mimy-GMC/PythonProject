import uuid
from py2neo import Node, Relationship
from datetime import datetime

class User:
    """Classe représentant un utilisateur dans le graphe Neo4j""" 

    @staticmethod
    def create(graph, name, email):
        user = Node("User", 
                   id=str(uuid.uuid4()),
                   name=name, 
                   email=email, 
                   created_at=int(datetime.now().timestamp()))
        graph.create(user)
        return user
    
    @staticmethod
    def find_by_id(graph, user_id):
        return graph.nodes.match("User", id=user_id).first()

    @staticmethod
    def update(graph, user_id, **kwargs):
        """ **kwargs: Paires clé-valeur des propriétés à mettre à jour """
        user = User.find_by_id(graph, user_id)
        if not user:
            return None
        for key, value in kwargs.items():
            user[key] = value
        graph.push(user)
        return user
    
    @staticmethod
    def delete(graph, user_id):
        user = User.find_by_id(graph, user_id)
        if user:
            graph.delete(user)
            return True
        return False
    
    @staticmethod
    def add_friend(graph, user_id, friend_id):
        # Vérifier si les deux utilisateurs existent
        print(f"Searching User ID: {user_id}")
        print(f"Searching Friend ID: {friend_id}")
        user = graph.nodes.match("User", id=user_id).first()
        friend = graph.nodes.match("User", id=friend_id).first()
        print(f"User found: {user}")
        print(f"Friend found: {friend}") 
        if not user or not friend:
            print("One of the users was not found.")
            return None

        # Vérifier si la relation existe déjà
        existing_rel = graph.match((user, friend), r_type="FRIENDS_WITH").first()
        if existing_rel:
            return existing_rel  # Retourne la relation existante
        
        rel = Relationship(user, "FRIENDS_WITH", friend)
        graph.create(rel)
        return rel

class Post:
    """Classe représentant un post dans le graphe Neo4j"""

    @staticmethod
    def create(graph, title, content, user_id):
        user = User.find_by_id(graph, user_id)
        if not user:
            return None
            
        post = Node("Post",
                   id=str(uuid.uuid4()),
                   title=title,
                   content=content,
                   created_at=int(datetime.now().timestamp()))
        rel = Relationship(user, "CREATED", post)
        graph.create(post)
        graph.create(rel)
        return post
    
    @staticmethod
    def find_by_id(graph, post_id):
        return graph.nodes.match("Post", id=post_id).first()

    @staticmethod
    def update(graph, post_id, **kwargs):
        post = Post.find_by_id(graph, post_id)
        if not post:
            return None
        for key, value in kwargs.items():
            post[key] = value
        graph.push(post)
        return post
    
    @staticmethod
    def delete(graph, post_id):
        post = Post.find_by_id(graph, post_id)
        if post:
            graph.delete(post)
            return True
        return False

    @staticmethod
    def add_like(graph, user_id, post_id):
        user = User.find_by_id(graph, user_id)
        post = Post.find_by_id(graph, post_id)
        if not user or not post:
            return None
        rel = Relationship(user, "LIKES", post)
        graph.create(rel)
        return rel

class Comment:
    """Classe représentant un comment dans le graphe Neo4j"""
    @staticmethod
    def create(graph, content, user_id, post_id):
        user = User.find_by_id(graph, user_id)
        post = Post.find_by_id(graph, post_id)
        if not user or not post:
            return None
            
        comment = Node("Comment", 
                       id=str(uuid.uuid4()),
                       content=content,
                       created_at=int(datetime.now().timestamp())
                    )
        
        # Relation avec le créateur
        created_rel = Relationship(user, "CREATED", comment)
        # Relation avec le post
        has_comment_rel = Relationship(post, "HAS_COMMENT", comment)
        
        graph.create(comment)
        graph.create(created_rel)
        graph.create(has_comment_rel)
        return comment

    @staticmethod
    def find_by_id(graph, comment_id):
        return graph.nodes.match("Comment", id=comment_id).first()

    @staticmethod
    def update(graph, comment_id, **kwargs):
        comment = Comment.find_by_id(graph, comment_id)
        if not comment:
            return None
        for key, value in kwargs.items():
            comment[key] = value
        graph.push(comment)
        return comment

    @staticmethod
    def delete(graph, comment_id):
        comment = Comment.find_by_id(graph, comment_id)
        if comment:
            graph.delete(comment)
            return True
        return False

    @staticmethod
    def add_like(graph, user_id, comment_id):
        user = User.find_by_id(graph, user_id)
        comment = Comment.find_by_id(graph, comment_id)
        if not user or not comment:
            return None
        rel = Relationship(user, "LIKES", comment)
        graph.create(rel)
        return rel