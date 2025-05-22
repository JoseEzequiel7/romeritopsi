from flask import Flask, render_template, request, redirect, url_for, session, make_response, flash
from werkzeug.security import generate_password_hash, check_password_hash

# ======================================
# Configuração Inicial do Flask
# ======================================
app = Flask(__name__)
app.config['SECRET_KEY'] = 'infoweb-1m'  # Em produção, use variáveis de ambiente, nao altere o ['SECRET_KEY'], está em modelo basico!

# ======================================
# Dados em Memória (Simulando um Banco de Dados)
# ======================================
usuarios = {
    # Usuário pré-cadastrado para testes
    'admin': {
        'senha': generate_password_hash('admin123'),
        'carrinho': []  # Lista de produtos no carrinho
    }
}

produtos = [
    {"id": 1, "nome": "Camiseta Básica", "preco": 49.90},
    {"id": 2, "nome": "Calça Jeans Slim", "preco": 129.90},
    {"id": 3, "nome": "Tênis Casual", "preco": 199.90},
    {"id": 4, "nome": "Boné Estilizado", "preco": 39.90}
]

# ======================================
# Rotas Principais
# ======================================

@app.route('/')
def index():
#    Página inicial do site.
#    Exibe o nome do usuário logado (se houver) e renderiza a página inicial.

    username = request.cookies.get('username')
    return render_template('index.html', username=username)

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
#    Rota para cadastro de novos usuários.
#    - GET: Exibe o formulário de cadastro.
#    - POST: Processa os dados do formulário e cria um novo usuário.
    if request.method == 'POST':
        username = request.form.get('username').strip()
        senha = request.form.get('password').strip()

        # Validações de entrada
        if not username or not senha:
            flash('Preencha todos os campos!', 'error')
            return redirect(url_for('cadastro'))

        if username in usuarios:
            flash('Usuário já existe!', 'error')
            return redirect(url_for('cadastro'))

        # Criação do novo usuário
        usuarios[username] = {
            'senha': generate_password_hash(senha),
            'carrinho': []
        }

        flash('Cadastro realizado com sucesso!', 'success')
        return redirect(url_for('login'))

    return render_template('cadastro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
#    Rota para login de usuários.
#    - GET: Exibe o formulário de login.
#    - POST: Valida as credenciais e autentica o usuário.
    if request.method == 'POST':
        username = request.form.get('username').strip()
        senha = request.form.get('password').strip()

        usuario = usuarios.get(username)
        
        # Validação de credenciais
        if not usuario or not check_password_hash(usuario['senha'], senha):
            flash('Credenciais inválidas!', 'error')
            return redirect(url_for('login'))

        # Autenticação bem-sucedida
        session['username'] = username
        response = make_response(redirect(url_for('index')))
        response.set_cookie('username', username, max_age=60*60*24)  # Cookie expira em 1 dia
        flash(f'Bem-vindo(a), {username}!', 'success')
        return response

    return render_template('login.html')

@app.route('/logout')
def logout():
#    Rota para logout do usuário.
#    Remove a sessão e o cookie do navegador.
    if 'username' in session:
        username = session['username']
        session.pop('username')
        response = make_response(redirect(url_for('index')))
        response.set_cookie('username', '', expires=0)
        flash(f'Até logo, {username}!', 'info')
        return response
    return redirect(url_for('index'))

@app.route('/produtos')
def listar_produtos():
#    Rota para listar os produtos disponíveis.
#    Apenas usuários autenticados podem acessar.
    if 'username' not in session:
        flash('Faça login para acessar os produtos!', 'error')
        return redirect(url_for('login'))
    
    return render_template('produtos.html', produtos=produtos)

@app.route('/adicionar/<int:produto_id>')
def adicionar_carrinho(produto_id):
#    Rota para adicionar um produto ao carrinho.
#    - produto_id: ID do produto a ser adicionado.
    if 'username' not in session:
        return redirect(url_for('login'))

    usuario = usuarios[session['username']]
    produto = next((p for p in produtos if p['id'] == produto_id), None)

    if produto:
        usuario['carrinho'].append(produto)
        flash(f'{produto["nome"]} adicionado ao carrinho!', 'success')
    else:
        flash('Produto não encontrado!', 'error')

    return redirect(url_for('listar_produtos'))

@app.route('/carrinho')
def ver_carrinho():
#    Rota para visualizar o carrinho de compras.
#    Exibe os itens no carrinho e o valor total.
    if 'username' not in session:
        return redirect(url_for('login'))

    usuario = usuarios[session['username']]
    carrinho = usuario['carrinho']
    total = sum(item['preco'] for item in carrinho)

    return render_template('carrinho.html', carrinho=carrinho, total=total)

@app.route('/esvaziar')
def esvaziar_carrinho():
#    Rota para esvaziar o carrinho de compras.
#    Remove todos os itens do carrinho do usuário.
    if 'username' not in session:
        return redirect(url_for('login'))

    usuario = usuarios[session['username']]
    usuario['carrinho'] = []
    flash('Carrinho esvaziado com sucesso!', 'success')
    return redirect(url_for('ver_carrinho'))

# ======================================
# Inicialização da Aplicação
# ======================================
if __name__ == '__main__':
    app.run(debug=True)