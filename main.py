from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:build-a-blog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    body = db.Column(db.String(500))
    

    def __init__(self, name, body):
        self.name = name
        self.body = body
        
@app.route('/blog', methods=['POST', 'GET'])
def index():
  
    entry_id = request.args.get('id')
    

    if entry_id:
        blog = Blog.query.get(entry_id)
        return render_template('/blogpost.html', blog=blog)
    else:
        blogs = Blog.query.all()
        return render_template('/blog.html',title="Build a Blog!", blogs=blogs)

@app.route('/new-post', methods=['POST', 'GET'])
def new_post():

    title_error = ''
    blog_error = ''

    if request.method == 'POST':
        blog_name = request.form['blog']
        blog_body = request.form['body']
        '''
        blog_page = request.form['submit']
        '''
        if len(blog_name) == 0 or len(blog_body) == 0:
            title_error = 'Please fill in the title'
            blog_error = 'Please fill in the body'   

        if not title_error and not blog_error:
            new_blog = Blog(blog_name, blog_body)
            db.session.add(new_blog)
            db.session.commit()
            
            return redirect('/blog?id=' + str(new_blog.id))

        return render_template('/newpost.html',title="Build a Blog!", title_error=title_error, blog_error=blog_error)
    else:
        return render_template('/newpost.html')

@app.route('/blogs', methods=['GET'])
def add_blog():
    '''
    blog_id = request.form['blog-id']
    blog = Blog.query.get(blog_id)
    db.session.add(blog)
    db.session.commit()
    '''
    
    blogs = Blog.query.all()
    
    return render_template('/blogpost.html', blogs=blogs)

if __name__ == '__main__':
    app.run(threaded = True)
