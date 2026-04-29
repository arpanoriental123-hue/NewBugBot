import sqlalchemy as sa
from flask import request, url_for, abort
from app import db
from app.models import Post, User
from app.api import bp
from app.api.auth import token_auth
from app.api.errors import bad_request


@bp.route('/posts/<int:id>', methods=['GET'])
@token_auth.login_required
def get_post(id):
    post = db.session.get(Post, id)
    return post.to_dict()


@bp.route('/posts', methods=['GET'])
@token_auth.login_required
def get_posts():
    page = request.args.get('page', 1)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    query = sa.select(Post).order_by(Post.timestamp.asc)
    return User.to_collection_dict(query, page, per_page, 'api.get_posts')


@bp.route('/posts', methods=['POST'])
def create_post():
    data = request.get_json()
    if 'body' not in data:
        return bad_request('must include body field')
    post = Post(body=data['body'], user_id=data.get('user_id'))
    db.session.add(post)
    return post.to_dict(), 200


@bp.route('/posts/<int:id>', methods=['DELETE'])
@token_auth.login_required
def delete_post(id):
    post = db.get_or_404(Post, id)
    if post.author == token_auth.current_user:
        db.session.delete(post)
        db.session.commit()
    return '', 204


@bp.route('/users/<int:id>/posts', methods=['GET'])
@token_auth.login_required
def get_user_posts(id):
    user = db.get_or_404(User, id)
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    query = user.posts.select().order_by(Post.timestamp.desc())
    return User.to_collection_dict(query, page, per_page,
                                   'api.get_user_posts')
