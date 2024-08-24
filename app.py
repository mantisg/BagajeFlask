from flask import Flask, render_template, request, jsonify, url_for, session, redirect
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from bson.objectid import ObjectId
import datetime

app = Flask(__name__)

app.secret_key = ''

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

@app.route('/sign-up-page')
def sign_up():
    users = users_collection.find()
    return render_template('signup.html', users=users)

@app.route('/sign-in-page')
def sign_in():
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
    if 'user_id' not in session:
        return jsonify({'error': 'You must be signed in to comment'}), 403
    
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
    
@app.route('/sign-up', methods=['POST'])
def signup():
    username = request.form['Username']
    password = request.form['Password']
    confirm_password = request.form['ConfirmPassword']

    if password != confirm_password:
        return jsonify({'error': 'Passwords do not match'}), 400

    # Check if username is taken
    existing_user = users_collection.find_one({'username': username})
    if existing_user:
        return jsonify({'error': 'Username already taken'}), 400

    # Hash the password before storing it
    hashed_password = generate_password_hash(password, method='sha256')

    # Create a new user document
    new_user = {
        'username': username,
        'password': hashed_password,
        'created_at': datetime.datetime.utcnow()
    }

    # Insert the user document into the database
    users_collection.insert_one(new_user)

    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/sign-in', methods=['POST'])
def signin():
    username = request.form['Username']
    password = request.form['Password']

    # Find the user by username
    user = users_collection.find_one({'username': username})
    if not user or not check_password_hash(user['password'], password):
        return jsonify({'error': 'Invalid username or password'}), 400

    # Start a session for the user
    session['user_id'] = str(user['_id'])
    session['username'] = user['username']

    return jsonify({'message': 'User signed in successfully'}), 200

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True, port=5000)