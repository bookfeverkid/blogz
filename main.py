from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:buildablog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):

    id =db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(500))

    def __init__(self, title, body):
        self.title = title
        self.body = body




@app.route('/')
def index():
    return redirect('/blog')

@app.route('/blog')
def Display_Blog():
    posts =  Blog.query.all()
    if request.method == 'POST':
        entry_title = request.form['title']
        entry_body = request.form['body']
        entry_id = int(request.form['id'])
        

    return render_template('blog.html', title="My Blog", posts=posts)

@app.route('/new_post', methods =['POST', 'GET'])
def new_post():
    if request.method == 'POST':
        entry_title = request.form['title']
        entry_body = request.form['body']
        title_error=""
        body_error=""
        
        if not entry_title:
            title_error = "Title of post is blank"
        if not entry_body:
            body_error = "Body of post is blank"

        if not body_error and not title_error:          
            new_post = Blog(entry_title, entry_body)
            db.session.add(new_post)
            db.session.commit()
            return redirect('/blog')
        else:
            return render_template('new_post.html', title="Make New Post",title_error=title_error, body_error=body_error, entry_title=entry_title, entry_body=entry_body) 
    return render_template('new_post.html', title="Make New Post")   
    

    
        

if __name__== '__main__':
    app.run()