import json
from flask import Blueprint,jsonify, render_template, request, session
import openai
from atlassian import Jira
import requests


main = Blueprint('main', __name__)

@main.route('/')
def index() -> str:
    """
    Renderiza a página index do aplicativo.

    :return: render_template:Callable (str)
    """
    return render_template('index.html')


@main.route('/create_jira_task', methods=['GET'])
def create_jira_task() -> requests.Response:
    """
    Chamada api do JIRA:
    Realiza a requisição a api do JIRA para enviar as informações necessárias
    na criação de um card. Envia o retorno da requisição ao Chat GPT.

    :return: requests.Response:json
    """
    res_gpt = session.get('resp_gpt')
    data = json.loads(res_gpt["choices"][0]["message"]["content"], strict=False)
    titulo = data["Título"]  # incluir tratamento do retorno para pegar titulo
    tema = data["Tema"]  # incluir tratamento do retorno para pegar tema
    descricao = data["Descrição"]  # incluir tratamento do retorno desc.

    fields = {
        "project": {"id": 31858},
        "summary": f"[{tema}]{titulo}",
        "description": f"{descricao}",
        "issuetype": {"name": "História Avulsa"},
        "labels": [f"{tema}"],
        "customfield_18200": [{"key": "CMDB-1233"}],
        "customfield_12200": {
            "self": "https://teams.sicredi.io/rest/api/2/customFieldOption/17702",
            "value": "Ambos",
            "id": "17702",
            "disabled": False,
        },
        "customfield_16900": {
            "self": "https://teams.sicredi.io/rest/api/2/customFieldOption/27201",
            "value": "Novo Core",
            "id": "27201",
            "disabled": False,
        },
    }

    jira = Jira(
        url="https://teams.sicredi.io/",
        username="JIRA-API-USER",
        password="JIRA-API-PASSWORD"
    )

    response = jira.issue_create(fields)

    return jsonify({'response':response['key']})


@main.route('/gerar_descricao', methods=['POST'])
def call_gpt() -> requests.Response:
    """
    Chamada api do Chat GPT:
    Realiza a requisição a api do Chat GPT para realizar a geração do texto de retorno.
    Também envia, junto da requisição, um prompt comportamental que especifica
    como o modelo deve agir.

    :return: requests.Response:json
    """
    openai.api_type = "azure"
    openai.api_base = "OPENAPI-API"
    openai.api_version = "2023-03-15-preview"
    openai.api_key = "OPENAPI-API-KEY"

    data = request.get_json()

    system_prompt = '''Você é um auxiliar de criação de tarefas para um
        time de dados, especialista em entendimento e levantamento de
        requisitos, funcionando como atendende de pessoas de negócio
        que não possuem conhecimento técnico, e deve sintetizar a requisição de um usuário, voltada a dados.
        Seu retorno deve conter um título, um dos seguintes temas(cadastro,
        contas, capital, sobras, atração, discovery) e uma descrição mais profunda, porém resumida, da
        requisição feita, com sugestões de possíveis entregáveis, tipos de 
        análises e tipos de metodologias estatísticas que possam agregar para
        a entrega final da demanda. Separe estes pontos em novas linhas, para que
        fique organizado e limpo. Retorne isso como um dicionário python, chave valor,
        porém insira os pontos de sugestões de análises e metodologias dentro da chave descrição,
        não coloque-os separados em novas chaves.'''

    response = openai.ChatCompletion\
                        .create(engine="gpt-4",
                                messages=[{"role": "system",
                                           "content": system_prompt},
                                          {"role": "user",
                                           "content": data['prompt']}],
                                temperature=0.7,
                                max_tokens=800,
                                top_p=0.95,
                                frequency_penalty=0,
                                presence_penalty=0,
                                stop=None)

    session['resp_gpt'] = response
    json_response = jsonify({'response':str(response['choices'][0]['message']['content'])\
                            .replace('"','').replace("{","")\
                                .replace("}", "")})

    return json_response
