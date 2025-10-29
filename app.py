import re
from flask import Flask, request, jsonify, g
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError
from database import SessionLocal, get_db, init_db 
from models.usuario import Usuario
from config import Config

# Inicializa o banco antes de subir a API
init_db()

app = Flask(__name__)

# Configuração JWT
app.config['JWT_SECRET_KEY'] = Config.JWT_SECRET_KEY
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=12)
jwt = JWTManager(app)

# 🧩 Função para obter uma sessão do banco (padrão Flask)
def get_session():
    db = SessionLocal()
    try:
        return db
    except Exception as e:
        db.close()
        raise e
    
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "PIC Backend API"})

@app.route('/usuario/cadastrar', methods=['POST'])
def cadastrar():
    data = request.get_json()
    
    if not data:
        return jsonify({"erro": "Dados JSON são obrigatórios"}), 400
    
    # Validar campos obrigatórios
    campos_obrigatorios = ['nome', 'telefone', 'data_nascimento']
    for campo in campos_obrigatorios:
        if campo not in data:
            return jsonify({"erro": f"Campo obrigatório ausente: {campo}"}), 400
    
    try:
        data_nascimento = datetime.strptime(data['data_nascimento'], '%d/%m/%Y').date()
        telefone = re.sub(r'\D', '', data['telefone'])  # Remove caracteres não numéricos
    except ValueError:
        return jsonify({"erro": "Formato de data_nascimento inválido. Use DD/MM/AAAA"}), 400

    db = get_session()
    try:
        # Criar novo usuário
        novo_usuario = Usuario(
            nome=data['nome'],
            telefone=telefone,
            data_nascimento=data_nascimento,
            bairro=data.get('bairro'),
            cidade=data.get('cidade'),
            estado=data.get('estado')
        )
        
        db.add(novo_usuario)
        db.commit()
        db.refresh(novo_usuario)
        
        # Criar token de acesso
        token_acesso = create_access_token(identity=novo_usuario.telefone)
        
        return jsonify({
            "mensagem": "Usuário registrado com sucesso",
            "token_acesso": token_acesso,
            "usuario": {
                "nome": novo_usuario.nome,
                "telefone": novo_usuario.telefone,
                "bairro": novo_usuario.bairro,
                "cidade": novo_usuario.cidade,
                "estado": novo_usuario.estado
            }
        }), 201
        
    except IntegrityError:
        return jsonify({"erro": "Telefone já cadastrado"}), 409
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data:
        return jsonify({"erro": "Dados JSON são obrigatórios"}), 400
    
    # Validar campos obrigatórios
    campos_obrigatorios = ['telefone', 'data_nascimento']
    for campo in campos_obrigatorios:
        if campo not in data:
            return jsonify({"erro": f"Campo obrigatório ausente: {campo}"}), 400
    
    # Processar data de nascimento
    try:
        data_nascimento = datetime.strptime(data['data_nascimento'], '%d/%m/%Y').date()
        # Tratamento de dados para considerar somente os numeros do telefone
        telefone = re.sub(r'\D', '', data['telefone'])  # Remove caracteres não numéricos
    except ValueError:
        return jsonify({"erro": "Formato de data_nascimento inválido. Use DD/MM/AAAA"}), 400

    db = get_session()

    try:
        print(data['telefone'])
        # Encontrar usuário por telefone e data de nascimento
        usuario = db.query(Usuario).filter(
            Usuario.telefone == telefone,
            Usuario.data_nascimento == data_nascimento
        ).first()
        
        if not usuario:
            return jsonify({"erro": "Credenciais inválidas"}), 401
        
        # Criar token de acesso
        token_acesso = create_access_token(identity=usuario.id)
        print(token_acesso)
        
        return jsonify({
            "mensagem": "Login realizado com sucesso",
            "token": token_acesso,
            "usuario": {
                "id": usuario.id,
                "nome": usuario.nome,
                "data_nascimento": usuario.data_nascimento,
                "telefone": usuario.telefone,
                "bairro": usuario.bairro,
                "cidade": usuario.cidade,
                "estado": usuario.estado
            }
        }), 200
        
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/perfil', methods=['GET'])
@jwt_required()
def obter_perfil():
    db = get_session()
    try:
        
        id_usuario_atual = get_jwt_identity()
        usuario = db.query(Usuario).filter(Usuario.id == id_usuario_atual).first()
        
        if not usuario:
            return jsonify({"erro": "Usuário não encontrado"}), 404
        
        return jsonify({
            "usuario": {
                "id": usuario.id,
                "nome": usuario.nome,
                "telefone": usuario.telefone,
                "data_nascimento": usuario.data_nascimento.isoformat(),
                "bairro": usuario.bairro,
                "cidade": usuario.cidade,
                "estado": usuario.estado,
                "email": usuario.email,
                "cep": usuario.cep,
                "rua": usuario.rua,
                "criado_em": usuario.created_at.isoformat(),
                "atualizado_em": usuario.updated_at.isoformat()
            }
        }), 200
        
    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()

@app.route('/formulario/responder', methods=['POST'])
@jwt_required()
def responder_formulario():
    id_usuario_atual = get_jwt_identity()
    data = request.get_json()

    id_formulario = data.get('id_formulario')
    nome_formulario = data.get('descricao_formulario')
    perguntas = data.get('perguntas_respostas', [])

    # Verificação fictícia — aqui simulamos consulta no banco
    ja_respondido = verificar_se_ja_respondeu(id_usuario_atual, id_formulario)

    if ja_respondido:
        return jsonify({
            "status": "error",
            "message": f"Usuário {id_usuario_atual} já respondeu o formulário {nome_formulario}."
        }), 400

    # 💾 Processar respostas (aqui apenas simulado)
    for p in perguntas:
        id_pergunta = p.get('id_pergunta')
        descricao = p.get('descricao_pergunta')
        resposta = p.get('resposta')
        anexo = p.get('anexo')

        print(f"Salvando resposta: {id_pergunta=} {descricao=} {resposta=} {anexo=}")

        # Aqui você chamaria algo como:
        # salvar_resposta(id_usuario_atual, id_formulario, id_pergunta, resposta, anexo)

    return jsonify({
        "status": "success",
        "message": f"Respostas do formulário {id_formulario} registradas com sucesso para o usuário {id_usuario_atual}"
    }), 200


# --- Funções fictícias auxiliares --- #
def verificar_se_ja_respondeu(id_usuario, id_formulario):
    """
    Verifica se o usuário já respondeu o formulário.
    Aqui está uma simulação — em produção você consultaria o banco.
    """
    # Exemplo fictício: suponha que o usuário 10 respondeu o formulário 1
    if id_usuario == 10 and id_formulario == 1:
        return True
    return False


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)