from flask import Blueprint,jsonify, render_template, redirect, request, session, url_for
import openai
import json
from atlassian import Jira
import pip_system_certs.wrapt_requests


main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template('index.html')

@main.route('/test')
def test():
    return render_template('test.html', resp_gpt = session['resp_gpt'])


@main.route('/create_jira_task')
def create_jira_task():
    res_gpt = session.get('resp_gpt')
    data = json.loads(res_gpt["choices"][0]["message"]["content"])
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
        username="",
        password=""
    )

    response = jira.issue_create(fields)

    return print(f"task criada com o código {response['key']}")


@main.route('/gerar_descricao', methods=['POST'])
def call_gpt():

    openai.api_type = "azure"
    openai.api_base = "https://cognicao-dev-clustheo.openai.azure.com/"
    openai.api_version = "2023-03-15-preview"
    openai.api_key = "2a4a3463bc2c4a6e8b336c1fcfd9db2a"

    data = request.get_json()

    SYSTEM_PROMPT = '''Você é um auxiliar de criação de tarefas para um
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
                           "content": SYSTEM_PROMPT},
                          {"role": "user",
                           "content": data['prompt']}],
                temperature=0.7,
                max_tokens=800,
                top_p=0.95,
                frequency_penalty=0,
                presence_penalty=0,
                stop=None)

    session['resp_gpt'] = response

    return jsonify({'response':str(response['choices'][0]['message']['content']).replace('"','').replace("{","").replace("}", "")})
