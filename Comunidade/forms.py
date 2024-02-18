from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField,SubmitField,PasswordField, ValidationError, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from Comunidade.models import Usuario
from flask_login import current_user


class FormCriarConta(FlaskForm):
    username = StringField("Nome", validators=[DataRequired()])
    email = StringField("E-mail", validators=[DataRequired(), Email()])
    senha = PasswordField("Senha", validators=[DataRequired(), Length(6, 20)])
    senha_confirm = PasswordField("Confirme sua senha", validators=[DataRequired(), EqualTo("senha", message="Passwords do not coincide")])
    botao_submit = SubmitField("Criar conta")

    def validate_email(self, email):
        usuario = Usuario.query.filter_by(email=email.data).first()
        if usuario:
            raise ValidationError("E-mail já cadastrado, tente outro ou faça login para continuar")


class FormLogin(FlaskForm):
    email = StringField("E-mail", validators=[DataRequired(), Email()])
    senha = PasswordField("Senha", validators=[DataRequired(), Length(6, 20)])
    lembrar_dados = BooleanField("Lembrar Login")
    botao_login = SubmitField("Login")


class FormEditarPerfil(FlaskForm):
    username = StringField("Nome", validators=[DataRequired()])
    email = StringField("E-mail", validators=[DataRequired(), Email()])
    botao_editar = SubmitField("Salvar alterações")
    foto_perfil = FileField("Alterar Foto de Perfil", validators=[FileAllowed(['jpg', 'png'])])
    curso_excel = BooleanField("Excel Impressionador")
    curso_vba = BooleanField("VBA Impressionador")
    curso_python = BooleanField("Python Impressionador")
    curso_powerbi = BooleanField("PowerBI Impressionador")
    curso_sql = BooleanField("SQL Impressionador")


    def validate_email(self, email):
        if current_user.email != email.data:
            usuario = Usuario.query.filter_by(email=email.data).first()
            if usuario:
                raise ValidationError("Este e-mail já está em uso")
            

class FormCriarPost(FlaskForm):
    titulo = StringField("Título", validators=[DataRequired(), Length(2, 126)])
    corpo =  TextAreaField("Escreva seu Post", validators=[DataRequired(), Length(2, 5000)])
    botao_criarpost = SubmitField("Criar Post")