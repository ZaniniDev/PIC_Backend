"""
Exemplo de como testar a API PIC Backend em português
"""

import requests
import json
from datetime import datetime

# URL base da API
BASE_URL = "http://localhost:5000"

def testar_saude():
    """Testar endpoint de saúde"""
    print("🔍 Testando endpoint de saúde...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Resposta: {response.json()}")
    print("-" * 50)

def testar_registro():
    """Testar registro de usuário"""
    print("📝 Testando registro de usuário...")
    
    dados_usuario = {
        "nome": "Marcus Zanini",
        "telefone": "13991550539",
        "data_nascimento": "04-07-2000",
        "email": "zaninimarcus@hotmail.com",
        "bairro": "Parque Prainha",
        "cidade": "São Vicente",
        "estado": "SP",
        "cep": "11325-010",
        "rua": "Avenida Engenheiro Saturnino de Brito"
    }
    
    response = requests.post(
        f"{BASE_URL}/cadastrar",
        json=dados_usuario,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status: {response.status_code}")
    print(f"Resposta: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    if response.status_code == 201:
        return response.json()["token_acesso"]
    
    print("-" * 50)
    return None

def testar_login():
    """Testar login de usuário"""
    print("🔐 Testando login de usuário...")
    
    dados_login = {
        "telefone": "13991550539",
        "data_nascimento": "04-07-2000"
    }
    
    response = requests.post(
        f"{BASE_URL}/login",
        json=dados_login,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status: {response.status_code}")
    print(f"Resposta: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    if response.status_code == 200:
        return response.json()["token_acesso"]
    
    print("-" * 50)
    return None

def testar_perfil(token):
    """Testar busca de perfil do usuário"""
    if not token:
        print("❌ Token não disponível, pulando teste de perfil")
        return
    
    print("👤 Testando busca de perfil...")
    
    response = requests.get(
        f"{BASE_URL}/perfil",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    )
    
    print(f"Status: {response.status_code}")
    print(f"Resposta: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print("-" * 50)

def main():
    """Executar todos os testes"""
    print("🚀 Iniciando testes da API PIC Backend\n")
    
    # Testar saúde
    testar_saude()
    
    # Testar registro
    token = testar_registro()
    
    # Testar login
    if not token:
        token = testar_login()
    
    # Testar perfil
    testar_perfil(token)
    
    print("✅ Testes concluídos!")

if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("❌ Erro: Não foi possível conectar à API. Certifique-se de que o servidor está rodando em http://localhost:5000")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")