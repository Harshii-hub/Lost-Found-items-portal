from flask import Flask, render_template, request, redirect, session
from pymongo import MongoClient
import os
import re

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

mongo_client = MongoClient(os.getenv('MONGODB_URI', 'mongodb://localhost:27017/'))
db = mongo_client[os.getenv('MONGODB_DATABASE', 'lost_and_found')]


@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        db.users.insert_one({
            'username': username,
            'email': email,
            'password': password
        })

        return redirect('/login')

    return render_template('register.html')
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        user = db.users.find_one({'username': username, 'password': password})

        if user:
            return redirect('/')

    return render_template('login.html')


@app.route('/')
def home():

    search = request.args.get('search')
    filter_type = request.args.get('filter')

    if search:
        items = db.items.find({'name': {'$regex': re.escape(search), '$options': 'i'}})

    elif filter_type:
        items = db.items.find({'type': filter_type})

    else:
        items = db.items.find()

    return render_template('index.html', items=items)
@app.route('/add', methods=['GET', 'POST'])
def add_item():

    if request.method == 'POST':

        name = request.form['name']
        description = request.form['description']
        location = request.form['location']
        item_type = request.form['type']
        image = request.files.get('image')

        filename = ""

        if image and image.filename != "":
           filename = image.filename

           image.save(
        os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
)

        db.items.insert_one({
            'name': name,
            'description': description,
            'location': location,
            'type': item_type,
            'image': filename
        })

        return redirect('/')

    return render_template('add_item.html')


if __name__ == '__main__':
    app.run(debug=True)