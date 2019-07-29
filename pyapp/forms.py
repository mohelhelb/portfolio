from wtforms import Form, PasswordField, StringField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from pyapp.hub import db
from pyapp.models import Post, User

# Users
class TemplateForm(Form):
    email=StringField(label="Email Address",
                      validators=[DataRequired(), Email(), Length(max=35)])
    password=PasswordField(label="Password",
                           validators=[DataRequired(), Length(min=4, max=35)])

# Users: Registration Form
class RegisterForm(TemplateForm):
    username=StringField(label="Username",
                         validators=[DataRequired(), Length(min=2, max=35)])
    confirm_password=PasswordField(label="Confirm Password",
                                   validators=[DataRequired(), EqualTo("password")])

    @staticmethod
    def validate_username(form, field):
        try:
            target=getattr(User, field.name)
        except AttributeError:
            pass # *** pending issue
        else:
            user=User.query.filter(target==field.data).first()
            if user:
                raise ValidationError(f"{field.label.text} already taken")
        finally:
            db.session.close()

    @staticmethod
    def validate_email(form, field):
        try:
            target=getattr(User, field.name)
        except AttributeError:
            pass # *** pending issue
        else:
            user=User.query.filter(target==field.data).first()
            if user:
                raise ValidationError(f"{field.label.text} already taken")
        finally:
            db.session.close()

# Users: Login Form
class LoginForm(TemplateForm):
    pass


# Posts
class PostForm(Form):
    title=StringField(label="Title",
                      validators=[DataRequired(), Length(min=5, max=50)])

    content=TextAreaField(label="Content",
                          validators=[DataRequired(), Length(min=25)])

    @staticmethod
    def validate_title(form, field):
        try:
            target=getattr(Post, field.name)
        except AttributeError:
            pass # *** pending issue
        else:
            post=Post.query.filter(target==field.data).first()
            if post:
                raise ValidationError(f"{field.label.text} already taken")
        finally:
            db.session.close()

    def custom_validate(self):
        if not self.validate():
            if self.title.errors and self.content.errors:
                try:
                    self.title.errors.remove(f"{self.title.label.text} already taken")
                except ValueError:
                    pass # *** pending issue
                finally:
                    return False
            elif self.title.errors:
                try:
                    self.title.errors.remove(f"{self.title.label.text} already taken")
                except ValueError:
                    pass # *** pending issue
                else:
                    return True
            return False
        return True
