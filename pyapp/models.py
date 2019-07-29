from datetime import datetime
from pyapp.hub import db

# User
class User(db.Model):
    __tablename__="users"
    user_id=db.Column(db.Integer, primary_key=True, autoincrement=True)
    username=db.Column(db.String(35), nullable=False, unique=True)
    email=db.Column(db.String(35), nullable=False, unique=True)
    password=db.Column(db.String(100), nullable=False)
    date_joined=db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    # Relation between user and posts
    my_posts=db.relationship("Post", backref="author")

    def __repr__(self):
        return f"""{type(self).__name__}(username="{self.username}", email="{self.email}")"""

    def save_user(self):
        db.session.add(self)
        db.session.commit()

    def delete_user(self):
        if self.my_posts:
            for post in self.my_posts:
                post.delete_post()
        db.session.delete(self)
        db.session.commit()


# Post
class Post(db.Model):
    __tablename__="posts"
    post_id=db.Column(db.Integer, primary_key=True, autoincrement=True)
    title=db.Column(db.String(50), nullable=False, unique=True)
    content=db.Column(db.Text, nullable=False)
    date_posted=db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    # Relation between posts and user
    author_id=db.Column(db.Integer, db.ForeignKey(f"{User.__tablename__}.{User.user_id.key}"), nullable=False)

    def __repr__(self):
        return f"""{type(self).__name__}(post_id={self.post_id})"""

    def save_post(self):
        db.session.add(self)
        db.session.commit()

    def delete_post(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def update_post(cls, post_id, title, content, author_id):
        target_keys={cls.title.key: title, cls.content.key: content, cls.author_id: author_id}
        cls.query.filter(cls.post_id==post_id).update(target_keys)
        db.session.commit()

    @classmethod
    def retrieve_all_posts(cls, chronological_order=False):
        try:
            first_post=Post.query.all()[0]
            last_post=Post.query.all()[-1]
        except IndexError:
            pass # *** pending issue
        else:
            min_post_id=first_post.post_id
            max_post_id=last_post.post_id
            if chronological_order:
                n=max_post_id
                while n>=min_post_id:
                    post=Post.query.filter_by(post_id=n).first()
                    if post:
                        yield post
                    n-=1
            else:
                n=min_post_id
                while n<=max_post_id:
                    post=Post.query.filter_by(post_id=n).first()
                    if post:
                        yield post
                    n+=1