from flask import Flask, request, redirect, render_template, flash
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:blogging@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    body = db.Column(db.Text)

    def __init__(self, title, body):
        self.title = title
        self.body = body


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


if __name__ == '__main__':
    app.run()
