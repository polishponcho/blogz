from flask import Flask, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogzpassword@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'somestring'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    body = db.Column(db.String(500))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    

    def __init__(self, name, body, owner):
        self.name = name
        self.body = body
        self.owner = owner

class User(db.Model): 
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')
    
    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'blogpost', 'singleuser', 'index', 'blog', 'home', 'blog']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():
    

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        username_error = ''
        password_error = ''
        user = User.query.filter_by(username=username).first()
        if user != None:
            if user.password != password:
                password_error = 'Invalid password'
        if user == None:
            username_error = 'Username does not exist'
                
        if user and user.password == password:
            session['username'] = username
            return redirect('/home')
        else:
            return render_template('login.html', username_error=username_error, password_error=password_error)

        
    return render_template('login.html')    

@app.route('/signup', methods=['POST', 'GET']) 
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        username_error = ''
        password_error = ''
        verify_error = ''

        # TODO = validate user's data
        
        existing_user = User.query.filter_by(username=username).first()

        if len(username) < 3:
            username_error = 'Need more characters'
            
            
        if username == '':
            username_error = 'Please enter username'
            username = ''

        if len(password) < 3:
            password_error = 'Need more characters'
            
        if len(password) == 0:
            password_error = 'Please enter password'
            password = ''
        
        if len(verify) < 3:
            verify_error = 'Need more characters'
           
        if len(verify) == 0:
            verify_error = 'Please enter password'
            verify = ''
        
        if password != verify:
            verify_error = 'Passwords do not match'
            verify = ''
        if existing_user != None and username == existing_user.username:
            username_error = 'Already exists'
            username = ''
        
        if username_error == '' and password_error == '' and verify_error == '':
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/new-post')
        else:
            return render_template('signup.html', title = 'Blogz', username_error=username_error, password_error=password_error, verify_error=verify_error)
            
            
    return render_template('signup.html', title = 'Blogz')

@app.route('/home')
def home():
    users = User.query.all()
    return render_template('/index.html', title = 'blog users!', users=users)

@app.route('/blog', methods=['POST', 'GET'])
def index():
    
    is_user = request.args.get('user')
    is_id = request.args.get('id')
    owner = User.query.filter_by(username=is_user).first()
    
    if is_user:
        user = Blog.query.get(is_user)
        blogs = Blog.query.filter_by(owner=owner).all()
        users = Blog.query.filter_by(owner=owner).all()
        return render_template('/singleuser.html', title="Blog Posts!", is_user=is_user, user=user, blogs=blogs, users=users )
    
    if is_id:
        blog = Blog.query.get(is_id)
        users = Blog.query.filter_by(owner=owner).all()
        
        return render_template('/blogpost.html', users=users, blog=blog)

    else:
        blogs = Blog.query.all()
        user = Blog.query.filter_by(owner=owner).all()
        return render_template('/blog.html',title="Blog Posts!", blogs=blogs,  user=user, owner=owner)

@app.route('/new-post', methods=['POST', 'GET'])
def new_post():

    title_error = ''
    blog_error = ''

    if request.method == 'POST':
        blog_name = request.form['blog']
        blog_body = request.form['body']
        
        if len(blog_name) == 0 or len(blog_body) == 0:
            title_error = 'Please fill in the title'
            blog_error = 'Please fill in the body'   

        if not title_error and not blog_error:
            owner = User.query.filter_by(username=session['username']).first()
            new_blog = Blog(blog_name, blog_body, owner)
            db.session.add(new_blog)
            db.session.commit()
            
            return redirect('/blog?id=' + str(new_blog.id))

        return render_template('/newpost.html',title="Build a Blog!", title_error=title_error, blog_error=blog_error)
    else:
        return render_template('/newpost.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

if __name__ == '__main__':
    app.run(threaded = True)
