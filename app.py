from flask import Flask, render_template, request, redirect, url_for, session, make_response
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'turma-1m'  

usuarios = {}

produtos = [
    {'id': 1, 'nome': 'Camiseta', 'preco': 29.90},
    {'id': 2, 'nome': 'Calça Jeans', 'preco': 89.90},
    {'id': 3, 'nome': 'Tênis', 'preco': 149.90},
]

@app.route('/')
def index():
    nome_usuario = request.cookies.get('usuario')
    return render_template('index.html', nome_usuario=nome_usuario)

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        usuario = request.form['usuario']
        senha = request.form['senha']
        if usuario in usuarios:
            return 'Usuário já existe!'
        usuarios[usuario] = generate_password_hash(senha)
        return redirect(url_for('login'))
    return render_template('cadastro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        senha = request.form['senha']
        senha_hash = usuarios.get(usuario)
        if senha_hash and check_password_hash(senha_hash, senha):
            session['usuario'] = usuario
            session['carrinho'] = []
            resp = make_response(redirect(url_for('index')))
            resp.set_cookie('usuario', usuario, max_age=60*5)
            return resp
        return 'Usuário ou senha inválidos.'
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)

