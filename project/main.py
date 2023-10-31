from flask import Blueprint, render_template, redirect, session, url_for
# import os
import openai
import json
from atlassian import Jira


main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template('index.html')


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


@main.route('/gerar_descricao')
def call_gpt():

    SYSTEM_PROMPT = '''Você é um auxiliar de criação de tarefas para um
        time de dados, funcionando como atendende de pessoas de negócio
        que não possuem conhecimento técnico.
        Sua tarefa é sintetizar a requisição de um usuário voltada a dados.
        Seu retorno deve conter um título, um dos seguintes temas(cadastro,
        contas, capital, sobras, atração) e uma descrição mais profunda da
        requisição feita.
        Retorne isso como um dicionário python, chave valor'''

    text = input("Escreva sua solicitação ao time Data Vader aqui: ")

    response = openai\
        .ChatCompletion\
        .create(engine="gpt-4",
                messages=[{"role": "system",
                           "content": SYSTEM_PROMPT},
                          {"role": "user",
                           "content": text}],
                temperature=0.7,
                max_tokens=800,
                top_p=0.95,
                frequency_penalty=0,
                presence_penalty=0,
                stop=None)

    session['resp_gept'] = response

    return redirect(url_for('create_jira_task'))
