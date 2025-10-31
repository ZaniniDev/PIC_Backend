import re
from flask import Flask, request, jsonify, g
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError
from database import SessionLocal, init_db 
from models.formulario import Formulario
from models.resposta import Resposta
from models.respostas_formulario import RespostaFormulario
from models.usuario import Usuario
from config import Config
from flask_cors import CORS

# Inicializa o banco antes de subir a API
init_db()

app = Flask(__name__)
CORS(app)

# Configuração JWT
app.config['JWT_SECRET_KEY'] = Config.JWT_SECRET_KEY
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=12)
jwt = JWTManager(app)
app.config['JSON_AS_ASCII'] = False

@jwt.invalid_token_loader
def token_invalido_callback(error_string):
    print(f"[JWT] Token inválido: {error_string}")
    return {"erro": "Token inválido", "detalhes": error_string}, 401

@jwt.unauthorized_loader
def token_ausente_callback(error_string):
    print(f"[JWT] Token ausente ou cabeçalho errado: {error_string}")
    return {"erro": "Token ausente", "detalhes": error_string}, 401

@jwt.expired_token_loader
def token_expirado_callback(jwt_header, jwt_payload):
    print(f"[JWT] Token expirado: {jwt_payload}")
    return {"erro": "Token expirado"}, 401

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
        
        return jsonify({
            "mensagem": "Usuário registrado com sucesso",
            "usuario": {
                "nome": novo_usuario.nome,
                "telefone": novo_usuario.telefone,
                "bairro": novo_usuario.bairro,
                "cidade": novo_usuario.cidade,
                "estado": novo_usuario.estado,
                "level": novo_usuario.level
            }
        }), 201
        
    except IntegrityError:
        return jsonify({"erro": "Telefone já cadastrado"}), 409
    except Exception as e:
        print(e)
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
        token_acesso = create_access_token(identity=str(usuario.id))
        print(token_acesso)
        
        return jsonify({
            "mensagem": "Login realizado com sucesso",
            "token": token_acesso,
            "usuario": {
                "nome": usuario.nome,
                "data_nascimento": usuario.data_nascimento,
                "telefone": usuario.telefone,
                "bairro": usuario.bairro,
                "cidade": usuario.cidade,
                "estado": usuario.estado,
                "level": usuario.level
            }
        }), 200
        
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/perfil', methods=['GET'])
@jwt_required()
def obter_perfil():
    db = get_session()
    try:
        
        id_usuario_atual = int(get_jwt_identity())
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

@app.route('/usuario/formularios_respondidos', methods=['GET'])
@jwt_required()
def buscar_formularios_respondidos_usuario():
    try:
        id_usuario_atual = get_jwt_identity()
    except Exception as e:
        print("Erro ao validar token:", e)
        return jsonify({"erro": "Token inválido", "detalhes": str(e)}), 401
    
    db = get_session()
    try:
        # Busca todos os ids de formulario respondido pelo usuario
        ids_formularios = db.query(RespostaFormulario.id_formulario).filter(
            RespostaFormulario.id_usuario == id_usuario_atual
        ).distinct().all()

        # Extrai apenas os IDs da tupla retornada pelo SQLAlchemy
        lista_ids = [id_form[0] for id_form in ids_formularios]

        print("Quantidade formulario respondidos:", len(lista_ids))

        return jsonify({
            "mensagem": "Formulários respondidos encontrados",
            "ids_formularios": lista_ids
        }), 200
        
    except Exception as e:
        return jsonify({"erro": "Erro ao buscar formulários", "detalhes": str(e)}), 500
    finally:
        db.close()

@app.route('/formulario/responder', methods=['POST'])
@jwt_required()
def responder_formulario():
    try:
        identidade = get_jwt_identity()
    except Exception as e:
        print("Erro ao validar token:", e)
        return {"valido": False, "erro": str(e)}, 401
    
    id_usuario_atual = get_jwt_identity()
    data = request.get_json()
    db = get_session()

    id_formulario = data.get('id_formulario')
    respostas = data.get('respostas')

    # Busca o formulario através do id no banco de dados
    formulario = db.query(Formulario).filter(Formulario.id == id_formulario).first()
    if not formulario:
        return jsonify({"status": "error", "message": "Formulário não encontrado"}), 404

    # Busca a resposta do usuario para esse formulario
    resposta_usuario_formulario = db.query(RespostaFormulario).filter(
        RespostaFormulario.id_formulario == id_formulario,
        RespostaFormulario.id_usuario == id_usuario_atual
    ).first()

    # Verifica se o usuário já respondeu o formulário
    if resposta_usuario_formulario:
        return jsonify({
            "status": "error",
            "message": f"formulario ja respondido"
        }), 400

    # 💾 Processar respostas (aqui apenas simulado)
    for r in respostas:
        pergunta = r.get('pergunta')
        resposta = r.get('resposta')
        tipo_pergunta = r.get('tipo_pergunta', 'texto')  # Padrão 'texto' se não especificado

        resposta = Resposta(
            id_formulario=id_formulario,
            id_usuario=id_usuario_atual,
            pergunta=pergunta,
            resposta=resposta,
            tipo_pergunta=tipo_pergunta
        )
        db.add(resposta)
        db.commit()
        db.refresh(resposta)      

    # Adiciona a resposta na tabela respostasformulario
    resposta_formulario = RespostaFormulario(
        id_formulario=id_formulario,
        id_usuario=id_usuario_atual,
        respondido=datetime.utcnow(),
        status="respondido"
    )
    db.add(resposta_formulario)
    db.commit()
    db.refresh(resposta_formulario) 

    # Ajuste para a mensagem ir com utf-8

    return jsonify({
        "status": "success",
        "message": f"Respostas do formulário {id_formulario} registradas com sucesso para o usuário {id_usuario_atual}"
    }), 200

@app.route('/formulario/respostas/all', methods=['GET'])
@jwt_required()
def obter_todas_respostas_formularios():
    id_usuario_atual = get_jwt_identity()

    db = get_session()

    try:
        respostas = db.query(Resposta).all()
        
        respostas_lista = []
        for resposta in respostas:
            respostas_lista.append({
                "id_formulario": int(resposta.id_formulario),
                "id_usuario": resposta.id_usuario,
                "pergunta": resposta.pergunta,
                "resposta": resposta.resposta,
                "tipo_pergunta": resposta.tipo_pergunta,
                "created_at": resposta.created_at.isoformat(),
                "updated_at": resposta.updated_at.isoformat()
            })
        
        return jsonify(
            respostas_lista
        ), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)