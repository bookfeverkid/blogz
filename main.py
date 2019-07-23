from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'

class Blog(db.Model):

    id =db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(500))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner_id):
        self.title = title
        self.body = body
        self.owner_id = owner_id    

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    user_blog = db.relationship('Blog', backref='user')

    def __init__(self, email, password):
        self.email = email
        self.password = password
        #this is a list of blog posts for the user
        #self.user_blog = user_blog

#check for loggedin User
@app.before_request
def require_login():
    allowed_routes = ['login', 'signup','index', 'blog']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        #Validate Form data
        if user and user.password == password:
            session['email'] = email
            flash("Logged in " + email)
            return redirect('/new_post')
        if not user:
            flash('User does not exist', 'error')
            return redirect('/signup')            
        if not (User.password == password):
            flash('User password incorrect', 'error')
        return render_template("login.html", email=email)   

    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']
        
        #Create new User
        existing_user = User.query.filter_by(email=email).first()
        if not existing_user and len(password)>=5 and password ==verify:
            new_user = User(email, password)
            db.session.add(new_user)
            db.session.commit()
            session['email'] = email
            return render_template('new_post.html', email=email)
        # Validate form data
        if len(email)< 5 or len(email)> 20 or email =='':
            flash('Your email should be between 5 and 2 characters with no spaces.', 'error')
        if existing_user:
            flash('That email is already in use', 'error')
        if len(password)<5 or len(password)>20 or password =='':
            flash('Your password should be between 5 and 2 characters with no spaces.', 'error')
        if password != verify:
            flash('Your passwords do not match.', 'error')
       
    return render_template('signup.html')   

@app.route('/logout')
def logout():
    del session['email']
    return redirect('/blog')

@app.route('/', methods=['POST', 'GET'])
def index():
    users = User.query.all() 
    return render_template('index.html', title="Home", users =users)

@app.route('/blog')
def blog(): 
    post_id =request.args.get('id')
    if 'email' not in session:
        return redirect('/login')
    else:
        user = User.query.all()
        single_user=  User.query.filter_by(email=session['email']).first().id
        if post_id == None:
            #Display all Posts by All Users
            posts =  Blog.query.all()
            return render_template('blog.html', title="My Blog", posts=posts, user=user, single_user=single_user)
        else:
            #Display a single blog entry
            post = Blog.query.get(post_id)
            user= User.query.filter_by(id=post.owner_id).first()
            return render_template('entry.html', post=post, title="Blog Entry", user=user)

@app.route('/user_blog', methods=['GET'])
def user_blog():
    #add a conditional that checks the url for a id variable, if there is none, then grab the user from the email
    if request.args.get('id'):
        
        user = User.query.filter_by(id = request.args.get('id')).first()
    else:
        user =  User.query.filter_by(email=session['email']).first()
    user_id = user.id
    posts =  Blog.query.filter_by(owner_id=user_id).all()
    return render_template('single_user.html', title="User Blog", posts=posts, user=user)
                  
@app.route('/new_post', methods =['POST', 'GET'])
def new_post():
    if request.method == 'POST':
        entry_title = request.form['title']
        entry_body = request.form['body']
        owner_id = User.query.filter_by(email=session['email']).first().id

        #Validate new post form
        if not entry_title  and not entry_body:
            flash('No title or post content is written', 'error')
            return render_template('new_post.html')
        if not entry_title:
            flash('No title is Witten', 'error')
            return render_template('new_post.html', entry_body=entry_body) 
        if not entry_body:
            flash('Blog post is missing content')
            return render_template('new_post.html', entry_title=entry_title)
         
        new_post = Blog(entry_title, entry_body, owner_id)
        db.session.add(new_post)
        db.session.commit()
        blog_id =str(new_post.id)
        return redirect('/blog?id'+ blog_id)
    
    return render_template('new_post.html', title="Make New Post")   
        

if __name__== '__main__':
    app.run()