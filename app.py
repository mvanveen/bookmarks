from flask import Flask, jsonify, request
from sqlalchemy.exc import NoResultFound

from db import get_session, Bookmark, Tag, User

app = Flask(__name__)

@app.route('/api/posts/all', methods=['GET'])
def get_all_bookmarks():
    session = get_session()
    bookmarks_query = session.query(Bookmark).all()
    bookmarks = [
        {
            "href": bookmark.url,
            "description": bookmark.title,
            "extended": bookmark.description,
            "time": bookmark.created_at.isoformat(),
            "tags": " ".join([tag.name for tag in bookmark.tags])
        } for bookmark in bookmarks_query
    ]
    return jsonify(bookmarks)

@app.route('/api/posts/add', methods=['POST'])
def add_bookmark():
    session = get_session()
    data = request.json
    user = session.query(User).filter_by(username=data.get('username')).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    new_bookmark = Bookmark(
        url=data['href'],
        title=data.get('description', ''),
        description=data.get('extended', ''),
        created_at=data.get('time'),
        user_id=user.id
    )
    session.add(new_bookmark)
    session.commit()

    # Handle tags
    tags = data.get('tags', '').split(' ')
    for tag_name in tags:
        tag = session.query(Tag).filter_by(name=tag_name).first()
        if not tag:
            tag = Tag(name=tag_name)
            session.add(tag)
            session.commit()
        new_bookmark.tags.append(tag)
    session.commit()

    return jsonify({"success": True, "id": new_bookmark.id}), 201

@app.route('/api/posts/delete', methods=['POST'])
def delete_bookmark():
    session = get_session()
    data = request.json
    try:
        bookmark = session.query(Bookmark).filter_by(url=data['href']).one()
        session.delete(bookmark)
        session.commit()
        return jsonify({"success": True}), 200
    except NoResultFound:
        return jsonify({"error": "Bookmark not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
