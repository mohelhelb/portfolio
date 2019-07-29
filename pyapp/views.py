from flask import flash, redirect, render_template, request, session, url_for
from pyapp.hub import app, bcrypt, db
from pyapp.models import Post, User
from pyapp.forms import LoginForm, PostForm, RegisterForm
from pyapp.ftools import access_control


# home
@app.route(rule="/<path:path>", methods=["GET"])
@app.route(rule="/home", methods=["GET"])
@app.route(rule="/", methods=["GET"])
def home(path="/"):
    return render_template("home.html")

# about
@app.route(rule="/about", methods=["GET"])
def about():
    return render_template("about.html")

# posts
@app.route(rule="/posts", methods=["GET"])
def posts():
    posts=Post.retrieve_all_posts(chronological_order=False)
    return render_template("posts.html", posts=posts)

# post
@app.route(rule="/posts/<int:post_id>", methods=["GET"])
def post(post_id):
    post=Post.query.filter_by(post_id=post_id).first()
    if post:
        return render_template("post.html", post=post)
    return "Page Not Found" # *** pending issue

# register
@app.route(rule="/register", methods=["GET", "POST"])
def register():
    form=RegisterForm(request.form)
    if request.method=="POST" and form.validate():
        # Add user to database
        username=form.username.data
        email=form.email.data
        password=bcrypt.generate_password_hash(form.password.data)
        user=User(username=username, email=email, password=password)
        user.save_user()
        # Session Set-up
        session["active"]=True
        session["username"]=user.username
        # Message Flashing
        flash("You have successfully registered", category="success")
        return redirect(url_for("dashboard", username=session["username"]))
    return render_template("register.html", form=form)

# login
@app.route(rule="/login", methods=["GET", "POST"])
def login():
    form=LoginForm(request.form)
    if request.method=="POST" and form.validate():
        user=User.query.filter(User.email==form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            # Session Set-up
            session["active"]=True
            session["username"]=user.username
            # Message Flashing
            flash("You have successfully logged in", category="success")
            return redirect(url_for("dashboard", username=session["username"]))
        # Message Flashing
        flash("Oops! Try again", category="danger")
        return redirect(url_for("login"))
    return render_template("login.html", form=form)

# dashboard
@app.route(rule="/dashboard/<string:username>", methods=["GET"])
@access_control
def dashboard(username):
    # Retrieve user-created posts
    user=User.query.filter_by(username=username).first()
    assert user is not None, "User is missing" # *** pending issue
    # Number of posts
    my_posts=user.my_posts
    session["num_my_posts"]=len(my_posts)
    return render_template("dashboard.html", my_posts=my_posts, username=username)

# add
@app.route(rule="/dashboard/<string:username>/add", methods=["GET", "POST"])
@access_control
def add(username):
    form=PostForm(request.form)
    if request.method=="POST" and form.validate():
        # Add post to database
        title=form.title.data
        content=form.content.data
        author=User.query.filter_by(username=username).first()
        post=Post(title=title, content=content, author=author)
        post.save_post()
        # Message Flashing
        flash("Your post has been added", category="success")
        return redirect(url_for("dashboard", username=username))
    return render_template("add.html", form=form)

# edit
@app.route(rule="/dashboard/<string:username>/edit/<int:post_id>", methods=["GET", "POST"])
@access_control
def edit(username, post_id):
    form=PostForm(request.form)
    user=User.query.filter_by(username=username).first()
    post=Post.query.filter(Post.post_id==post_id, Post.author==user).first()
    if request.method=="GET" and post:
        # Populate form fields
        form.title.data=post.title
        form.content.data=post.content
        return render_template("edit.html", form=form)
    elif request.method=="GET":
        # Message Flashing
        flash("The post you want to update does not exit", category="info")
        return redirect(url_for("dashboard", username=username))
    if request.method=="POST" and form.custom_validate():
        post.update_post(post_id, form.title.data, form.content.data, user.user_id)
        # Message Flashing
        flash("Your post has been updated", category="success")
        return redirect(url_for("dashboard", username=username))
    elif request.method=="POST":
        # Populate form fields
        form.title.data=request.form["title"]
        form.content.data=request.form["content"]
        return render_template("edit.html", form=form)

# delete
@app.route(rule="/dashboard/<string:username>/delete/<int:post_id>", methods=["GET"])
@access_control
def delete(username, post_id):
    # Retrieve the post to be deleted by id
    post=Post.query.filter_by(post_id=post_id).first()
    if post:
        # Delete post
        post.delete_post()
        # Message Flashing
        flash("Your post has been deleted", category="success")
        return redirect(url_for("dashboard", username=username))
    # Message Flashing
    flash("The post you want to delete does not exist", category="info")
    return redirect(url_for("dashboard", username=username))

# delete account
@app.route(rule="/dashboard/<string:username>/delete_account", methods=["GET"])
@access_control
def delete_account(username):
    user=User.query.filter_by(username=username).first()
    user.delete_user()
    # Session Teardown
    session.clear()
    # Message Flashing
    flash("Your account has been deleted", category="success")
    return redirect(url_for("register"))

# account
@app.route(rule="/dashboard/<string:username>/account", methods=["GET"])
@access_control
def account(username):
    user=User.query.filter_by(username=username).first()
    personal_data={"Username": user.username,
                   "Email": user.email,
                   "Joined date": user.date_joined.strftime("%B %d, %Y"),
                   "Number of posts": session["num_my_posts"]}
    return render_template("account.html", personal_data=personal_data)

# logout
@app.route(rule="/logout/<string:username>", methods=["GET"])
@access_control
def logout(username):
    # Session Teardown
    session.clear()
    # Message Flashing
    flash("You have successfully logged out", category="success")
    return redirect(url_for("login"))
