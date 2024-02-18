from flask import render_template, request, flash, redirect, url_for, abort
from Comunidade.forms import FormCriarConta, FormLogin, FormEditarPerfil, FormCriarPost
from Comunidade import app, database, bcrypt
from Comunidade.models import Usuario, Post
from translate import Translator
from flask_login import login_user, logout_user, current_user, login_required
import secrets
import os
from PIL import Image
from wtforms import BooleanField


tradutor = Translator(from_lang="English", to_lang="Portuguese")


@app.route("/")
def home():
    posts = Post.query.order_by(Post.id.desc())
    return render_template("home.html", posts=posts)


@app.route("/contato")
def contato():
    return render_template("contato.html")


@app.route("/usuarios")
def usuarios():
    lista_usuarios = Usuario.query.all()
    return render_template("usuarios.html", lista_usuarios=lista_usuarios)


@app.route("/login", methods=["GET", "POST"])
def login():
    form_login = FormLogin()
    form_criar = FormCriarConta()

    if form_login.validate_on_submit() and "botao_login" in request.form:
        usuario = Usuario.query.filter_by(email=form_login.email.data).first()
        if usuario and bcrypt.check_password_hash(usuario.senha, form_login.senha.data):
            login_user(usuario, remember=form_login.lembrar_dados.data)
            flash("Login feito com sucesso", "alert-success")
            par_next = request.args.get("next")
            if par_next:
                return redirect(par_next)
            return redirect(url_for("home"))
        else:
            flash("Usuário ou senha inválidos", "alert-danger")
    if form_criar.validate_on_submit() and "botao_submit" in request.form:
        # Codigo para criar a conta do novo usuario
        senha_cryp = bcrypt.generate_password_hash(form_criar.senha.data).decode("utf-8")
        usuario = Usuario(
            username=form_criar.username.data,
            email=form_criar.email.data,
            senha=senha_cryp)
        database.session.add(usuario)
        database.session.commit()
        login_user(usuario)
        flash("Conta criada com sucesso!", "alert-success")
        return redirect(url_for("home"))
    return render_template("login.html", form_login=form_login, form_criar=form_criar, tradutor=tradutor)


@app.route("/sair")
@login_required
def sair():
    logout_user()
    flash("Logout feito com sucesso.", "alert-success")
    return redirect(url_for("home"))


@app.route("/perfil")
@login_required
def perfil():
    foto_perfil = url_for("static", filename=f"fotos_perfil/{current_user.foto_perfil}")
    return render_template("perfil.html", foto_perfil=foto_perfil)


@app.route("/post/criar", methods=["GET", "POST"])
@login_required
def criar_post():
    form = FormCriarPost()
    if form.validate_on_submit():
        post = Post(titulo=form.titulo.data, corpo=form.corpo.data, autor=current_user)
        database.session.add(post)
        database.session.commit()
        flash('Post criado com sucesso!', 'alert-success')
        return redirect(url_for('home'))
    return render_template("criarpost.html", form=form)


def salvar_foto(imagem):
    # criar e adicionar o código a imagem
    codigo = secrets.token_hex(8)
    nome, extensao = os.path.splitext(imagem.filename)
    nome_arquivo = nome + codigo + extensao
    caminho = os.path.join(app.root_path, 'static/fotos_perfil', nome_arquivo)
    #reduzir imagem e salvar
    tamanho = (350, 350)
    imagem_reduzida = Image.open(imagem)

    #corrigindo erro ao tentar fazer upload de imagens jpg com fundo transparente:
    if extensao.lower() == ".jpg" or extensao.lower() == ".jpeg":
        imagem_reduzida = imagem_reduzida.convert("RGB")

    imagem_reduzida.thumbnail(tamanho)
    imagem_reduzida.save(caminho)

    return nome_arquivo


def atualizar_cursos(form):
    lista_cursos = []
    for campo in form:
        if 'curso_' in campo.name:
            if campo.data:
                lista_cursos.append(campo.label.text)
    lista_cursos = ';'.join(lista_cursos)
    if len(lista_cursos) == 0:
        lista_cursos = "Não Informado"
    return lista_cursos


@app.route("/perfil/editar", methods=["GET", "POST"])
@login_required
def editar_perfil():
    form = FormEditarPerfil()
    if form.validate_on_submit():
        current_user.email = form.email.data
        current_user.username = form.username.data
        current_user.cursos = atualizar_cursos(form)
        if form.foto_perfil.data:
            nome_foto = salvar_foto(form.foto_perfil.data)
            current_user.foto_perfil = nome_foto
        database.session.commit()
        flash("Alterações salvas!", "alert-success")
        return redirect(url_for("perfil"))
    elif request.method == "GET":
        form.email.data = current_user.email
        form.username.data = current_user.username
        cursos_selecionados = current_user.cursos.split(';')
        for campo in form:
            for curso in cursos_selecionados:
                if curso in str(campo.label):
                    campo.data = BooleanField(default='checked')
    foto_perfil = url_for("static", filename=f"fotos_perfil/{current_user.foto_perfil}")
    return render_template("editarperfil.html", foto_perfil=foto_perfil, form=form, tradutor=tradutor)


@app.route('/post/<post_id>', methods=["GET", "POST"])
@login_required
def exibir_post(post_id):
    post = Post.query.get(post_id)
    if current_user == post.autor:
        form = FormCriarPost()
        if request.method == "GET":
            form.titulo.data = post.titulo
            form.corpo.data = post.corpo
        elif form.validate_on_submit():
            post.titulo = form.titulo.data
            post.corpo = form.corpo.data
            database.session.commit()
            flash('Post atualizado!', 'alert-success')
            return redirect(url_for('home'))
    else:
        form = None
    return render_template('post.html', post=post, form=form)

@app.route('/post/<post_id>/excluir', methods=["GET", "POST"])
@login_required
def excluir_post(post_id):
    post = Post.query.get(post_id)
    if current_user == post.autor:
        database.session.delete(post)
        database.session.commit()
        flash('Post Excluído.', 'alert-danger')
        return redirect(url_for('home'))
    else:
        abort(403)