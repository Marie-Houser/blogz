from flask import Flask, request, redirect, render_template, flash, session
from flask_sqlalchemy import SQLAlchemy
from hashutils import make_pw_hash, check_pw_hash


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:password@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    body = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner_id):
        self.title = title
        self.body = body
        self.owner_id=owner_id

class User(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    username=db.Column(db.String(255))
    pw_hash = db.Column(db.String(120))
    # blogs = db.relationship('Blog', backref = 'owner_id')

    def  __init__(self, username, password):
        self.username=username
        self.pw_hash = make_pw_hash(password)
    
@app.before_request
def require_login():
    allowed_routes = ['login', 'list_blogs', 'index', 'signup', 'display_user_posts']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')
    

@app.route('/blog', methods=['GET'])    
def list_blogs():
    id=request.args.get('id')
    if id !=None:
        user = User.query.get(id)
        blog_post = Blog.query.get(id)
        return render_template('blog-display.html', blog_post=blog_post, user=user)
    blog_posts = Blog.query.all() 
    return render_template('blog.html', blog_posts=blog_posts)

@app.route('/newpost', methods=['POST'])
def new_post():
    blog_title = request.form['blog_title']
    blog_text = request.form['blog_text']
    if blog_text=="" and blog_title=="":
        error_one="Please enter a title for your blog."
        error_two="Please enter text for your blog."
        return render_template('/newpost.html', blog_title=blog_title, blog_text=blog_text, error_one=error_one, error_two=error_two)
    elif blog_title=="":
        error_one="Please enter a title for your blog."
        return render_template('/newpost.html', blog_title=blog_title, blog_text=blog_text, error_one=error_one)
    elif blog_text=="":
        error_two="Please enter text for your blog."
        return render_template('/newpost.html', blog_title=blog_title, blog_text=blog_text, error_two=error_two)
    else:
        user = User.query.filter_by(username=session['user']).first()
        user_id=user.id
        owner_id=user_id
        new_post = Blog(blog_title, blog_text, owner_id)
        new_post.body=blog_text
        new_post.owner_id=owner_id
        db.session.add(new_post)
        db.session.commit()
        id=new_post.id
        a='/blog?id='+str(id)
        return redirect(a)

@app.route('/newpost', methods=['GET', 'POST'])
def get_newpost_template():
    return render_template('newpost.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method=='POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_pw_hash(password, user.pw_hash):
            session['username'] = username
            flash("Logged in")
            return redirect ('/newpost')
        else:
            if check_pw_hash(password, user.pw_hash) ==False:
                flash('That password does not match what is in our database.  Would you mind trying a different one?', 'error')
            elif User.query.filter_by(username=username).first() ==[]:
                flash("We don't seem to have you in our database.  Please signup for an account!", 'error')
            
    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method=='POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        username_error=""
        password_error=""
        verify_error=""

        if username=="":
            username_error='Please enter a username.'
            return render_template('signup.html', username_error=username_error)
        if len(username)<=3:
            username_error='Please enter a username longer than 3 characters.'
            return render_template('signup.html', username_error=username_error, username=username)
        if password =="":
            password_error='Please enter a password.'
            return render_template('signup.html', password_error=password_error, username=username)
        if len(password)<=3:
            password_error='Please enter a password longer than 3 characters.'
            return render_template('signup.html', password_error=password_error, username=username)

        if verify != password:
            verify_error='Those passwords do not seem to match.  Try retyping please.'
            return render_template('signup.html', verify_error=verify_error, username=username)

        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
            
        else:
            username_error="It looks like you may have already registered with us.  Try logging in." 
            return render_template('signup.html', username_error=username_error)
    else:
        return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['user']
    return redirect('/blog')

# "Home" page
@app.route('/')
def index():
    users= User.query.all()
    return render_template('index.html', users=users)

@app.route('/user', methods=['GET'])    
def display_user_posts():
    username=request.args.get('user')
    user=User.query.get(username)
    if username !=None:
        owner_id=username
        blog_posts = Blog.query.filter_by(owner_id=owner_id).all()
        print(blog_posts)
        return render_template('blog-with-user.html', blog_posts=blog_posts, user=user)
    blog_posts = Blog.query.all() 
    return render_template('blog.html', blog_posts=blog_posts)
        
if __name__ == '__main__':
    app.run()
