from __future__ import annotations
from datetime import date
from flask import Flask, abort, render_template, redirect, url_for, flash, session
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from forms import CreatePostForm, RegisterForm, LoginForm, CommentForm
from flask_gravatar import Gravatar


app = Flask(__name__)
app.config["SECRET_KEY"] = "CreateYourOwnSecretKey"
ckeditor = CKEditor(app)
Bootstrap5(app)

login_manager = LoginManager()
login_manager.init_app(app)


# CONNECT TO DB
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///posts.db"
db = SQLAlchemy()
db.init_app(app)


# CONFIGURE TABLES
class BlogPost(db.Model):
    """
    Database model for a blog post.
    Attributes:
        id (Integer): The primary key, unique identifier for the blog post.
        author_id (Integer): Foreign key, linking to the author's user ID.
        title (String): Title of the blog post, unique and non-nullable.
        subtitle (String): Subtitle of the blog post, non-nullable.
        date (String): Publication date of the blog post, non-nullable.
        body (Text): Content of the blog post, non-nullable.
        img_url (String): URL of the blog post's feature image, non-nullable.
        comments (relationship): Link to comments associated with the blog post.
    """

    __tablename__ = "blog_posts"
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    author = db.relationship("User", back_populates="posts")
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)

    comments = db.relationship("Comment", back_populates="parent_post")


class User(UserMixin, db.Model):
    """
    Database model for a user.
    Attributes:
        id (Integer): The primary key, unique identifier for the user.
        email (String): Email address of the user, unique and non-nullable.
        password (String): Hashed password for user account security, non-nullable.
        name (String): Name of the user, non-nullable.
        posts (relationship): Link to blog posts authored by the user.
        comments (relationship): Link to comments made by the user.
    """

    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(500), unique=True, nullable=False)
    password = db.Column(db.String(500), nullable=False)
    name = db.Column(db.String(500), nullable=False)
    posts = db.relationship("BlogPost", back_populates="author")
    comments = db.relationship("Comment", back_populates="comment_author")


class Comment(db.Model):
    """
    Database model for a comment.
    Attributes:
        id (Integer): The primary key, unique identifier for the comment.
        text (Text): Content of the comment, non-nullable.
        author_id (Integer): Foreign key, linking to the commenter's user ID.
        post_id (Integer): Foreign key, linking to the associated blog post's ID.
        comment_author (relationship): Link to the user who authored the comment.
        parent_post (relationship): Link to the blog post associated with the comment.
    """

    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    comment_author = db.relationship("User", back_populates="comments")
    post_id = db.Column(db.Integer, db.ForeignKey("blog_posts.id"))
    parent_post = db.relationship("BlogPost", back_populates="comments")


# Adding profile avatars for the comments section
gravatar = Gravatar(
    app,
    size=100,
    rating="g",
    default="retro",
    force_default=False,
    force_lower=False,
    use_ssl=False,
    base_url=None,
)

with app.app_context():
    db.create_all()


def admin_only(function):
    """
    Decorator to restrict access to certain views to only the admin user.
    Args:
        function (function): A Flask view function that requires admin access.
    Returns:
        function: The original view function, if the current user is admin, otherwise a
    403 error.
    """

    @wraps(function)
    def decorated_function(*args, **kwargs):
        if current_user.id == 1:
            return function(*args, **kwargs)
        return abort(403)

    return decorated_function


@login_manager.user_loader
def load_user(user_id):
    """
    User loader callback for Flask-Login.
    Retrieves a user from the database using the provided user ID.
    Args:
        user_id (int): Unique identifier for the user.
    Returns:
        User: A user object if found, otherwise None.
    """
    return db.session.execute(db.select(User).where(User.id == user_id)).scalar()


@app.route("/register", methods=["GET", "POST"])
def register():
    """
    Route for handling the registration of new users.
    Displays the registration form and processes the form submission.
    Returns:
        render_template/redirect: Redirects to the 'get_all_posts'
                                    page if registration is successful,
                                    otherwise renders the registration
                                    template.
    """

    register_form = RegisterForm()
    if register_form.validate_on_submit():
        email = register_form.email.data
        password = generate_password_hash(
            register_form.password.data, method="pbkdf2:sha256", salt_length=8
        )
        name = register_form.password.data

        user = db.session.execute(db.Select(User).where(User.email == email)).scalar()

        if user:
            flash(
                "There is an existing user with this email! Try to login with your credentials",
                "danger",
            )
            return redirect("login")
        else:
            new_user = User(email=email, password=password, name=name)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for("get_all_posts", current_user=current_user))

    return render_template(
        "register.html", form=register_form, current_user=current_user
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Route for handling user login.
    Displays the login form and processes the form submission.
    Returns:
        render_template/redirect: Redirects to the 'get_all_posts' page if login is successful,
                                  otherwise renders the login template with an error message.
    """
    login_form = LoginForm()

    if login_form.validate_on_submit():
        password = login_form.password.data
        user = db.session.execute(
            db.Select(User).where(User.email == login_form.email.data)
        ).scalar()

        # Try to give the least amount of information for XSS attacks
        if user:
            if check_password_hash(user.password, password):
                login_user(user)
                flash(f"User: {user.name} Logged in Successfully", "success")
                return redirect(url_for("get_all_posts"))
        flash("Please try again! Wrong credentials", "danger")
    return render_template("login.html", form=login_form, current_user=current_user)


@app.route("/logout")
def logout():
    """
    Route for handling user logout.
    Logs out the current user and clears the session.
    Returns:
        redirect: Redirects to the 'get_all_posts' page.
    """
    logout_user()
    session.clear()  # Clear session data
    return redirect(url_for("get_all_posts"))


@app.route("/")
def get_all_posts():
    """
    Route for displaying all blog posts.
    Fetches all posts from the database and renders them on the index page.
    Returns:
        render_template: Renders the 'index.html' template with all blog posts.
    """
    result = db.session.execute(db.select(BlogPost))
    posts = result.scalars().all()
    return render_template("index.html", all_posts=posts, current_user=current_user)


@app.route("/post/<int:post_id>", methods=["GET", "POST"])
def show_post(post_id):
    """
    Route for displaying a specific blog post and its comments.
    Args:
        post_id (int): The unique identifier of the blog post.
    Returns:
        render_template: Renders the 'post.html' template for the specified blog post.
    """
    requested_post = db.get_or_404(BlogPost, post_id)
    comment_form = CommentForm()

    if comment_form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("You need to login or register to comment.")
            return redirect(url_for("login"))

        new_comment = Comment(
            text=comment_form.comment_text.data,
            comment_author=current_user,
            parent_post=requested_post,
        )
        db.session.add(new_comment)
        db.session.commit()

    return render_template(
        "post.html",
        post=requested_post,
        current_user=current_user,
        form=comment_form,
        all_comments=requested_post.comments,
    )


@app.route("/new-post", methods=["GET", "POST"])
@admin_only
def add_new_post():
    """
    Route for adding a new blog post.
    This view is protected by the 'admin_only' decorator, ensuring only authorized users can access it.
    Displays a form for creating a new post and processes the form submission.
    Returns:
        render_template/redirect: Renders the 'make-post.html' template with a form if GET method is used,
                                  or redirects to 'get_all_posts' if the form submission is successful.
    """
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user,
            date=date.today().strftime("%B %d, %Y"),
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form, current_user=current_user)


@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@admin_only
def edit_post(post_id):
    """
    Route for editing an existing blog post.
    This view is protected by the 'admin_only' decorator.
    Args:
        post_id (int): The unique identifier of the blog post to be edited.
    Displays a form pre-filled with the existing post data and processes the form submission.
    Returns:
        render_template/redirect: Renders the 'make-post.html' template with the edit form if GET method is used,
                                  or redirects to the specific 'show_post' page if the form submission is successful.
    """
    post = db.get_or_404(BlogPost, post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body,
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.author = current_user
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))
    return render_template(
        "make-post.html", form=edit_form, is_edit=True, current_user=current_user
    )


@app.route("/delete/<int:post_id>")
@admin_only
def delete_post(post_id):
    """
    Route for deleting an existing blog post.
    This view is protected by the 'admin_only' decorator.
    Args:
        post_id (int): The unique identifier of the blog post to be deleted.
    Processes the deletion of the specified post.
    Returns:
        redirect: Redirects to the 'get_all_posts' page after the post has been deleted.
    """
    post_to_delete = db.get_or_404(BlogPost, post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for("get_all_posts"))


@app.route("/about")
def about():
    return render_template("about.html", current_user=current_user)


@app.route("/contact")
def contact():
    return render_template("contact.html", current_user=current_user)


if __name__ == "__main__":
    app.run(debug=True, port=5002)