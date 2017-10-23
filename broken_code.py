from flask import Flask, request, redirect, render_template, flash, session
from flask_sqlalchemy import SQLAlchemy


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
    password=db.Column(db.String(255))

    def  __init__(self, username, password):
        self.username=username
        self.password=password
    


@app.route('/blog', methods=['GET'])    
def index():
    id=request.args.get('id')
    if id !=None:
        blog_post = Blog.query.get(id)
        return render_template('blog-display.html', blog_post=blog_post)
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
        new_post = Blog(blog_title, blog_text)
        new_post.body=blog_text
        db.session.add(new_post)
        db.session.commit()
        id=new_post.id
        a='/blog?id='+str(id)
        return redirect(a)

@app.route('/newpost', methods=['GET'])
def get_newpost_template():
    return render_template('newpost.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method=='POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['user'] = user
            flash("Logged in")
            print(session)
            return redirect ('/newpost')
        else:
            if password != User.password:
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
            return redirect('/newpost')
            session['username'] = username
        else:
            username_error="It looks like you may have already registered with us.  Try logging in." 
            return render_template('signup.html', username_error=username_error)
    else:
        return render_template('signup.html')

# @app.route('/logout')
# def logout():
#     del session['username']
#     return redirect('/login')

        
if __name__ == '__main__':
    app.run()
