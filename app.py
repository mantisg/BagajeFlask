from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
import datetime

app = Flask(__name__)

# MongoDB connection
connection_string = "mongodb+srv://jbliven93:LucAsheArt022024@bagajedb.0ofh3.mongodb.net/"
client = MongoClient(connection_string)

# Define the database and collection you want to use
db = client['BagajeDB']
posts_collection = db['posts']
users_collection = db['users']
responses_collection = db['responses']

@app.route("/")
def home():
    posts = posts_collection.find()
    users = users_collection.find()
    responses = responses_collection.find()
    return render_template('home.html', posts=posts, users=users, responses=responses)

@app.route('/admin')
def admin_page():
    users = users_collection.find()
    return render_template('admin-page.html', users=users)

@app.route('/about')
def about_page():
    return render_template('about.html')

@app.route('/sign-up')
def signup():
    users = users_collection.find()
    return render_template('signup.html', users=users)

@app.route('/sign-in')
def signin():
    users = users_collection.find()
    return render_template('signin.html', users=users)

@app.route('/admin/post', methods=['POST'])
def handle_submit_post():
    form_data = request.form.to_dict()

    last_post = posts_collection.find_one(sort=[("id", -1)])
    next_id = last_post['id'] + 1 if last_post else 1

    form_data['id'] = next_id

    posts_collection.insert_one(form_data)

    return jsonify({'message': 'Form submitted successfully'}), 200

@app.route('/posts/<post_id>', methods=['DELETE'])
def delete_post(post_id):
    try:
        posts_collection.delete_one({'_id': ObjectId(post_id)})
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        print(f"Error deleting post: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500
    
@app.route('/posts/<post_id>/comments', methods=['POST'])
def add_comment(post_id):
    try:
        # Convert the post_id from string to ObjectId
        post_id = ObjectId(post_id)
        comment = request.json
        comment['CreatedAt'] = datetime.datetime.utcnow()
        posts_collection.update_one(
            {'_id': post_id},
            {'$push': {'comments': comment}}
        )
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        print(f"Error adding comment: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500
    
@app.route('/posts/<post_id>/comments/<int:comment_index>', methods=['DELETE'])
def delete_comment(post_id, comment_index):
    try:
        # Pull the comment at the specified index
        result = posts_collection.update_one(
            {'_id': ObjectId(post_id)},
            {'$unset': {f'comments.{comment_index}': 1}}
        )
        
        # Remove the null entry created by $unset
        posts_collection.update_one(
            {'_id': ObjectId(post_id)},
            {'$pull': {'comments': None}}
        )
        
        if result.modified_count > 0:
            return jsonify({'success': True, 'message': 'Comment deleted successfully'}), 200
        else:
            return jsonify({'success': False, 'message': 'Comment not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)