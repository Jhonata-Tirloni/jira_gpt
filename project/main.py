from flask import Blueprint, render_template
import os
import openai
import json
from atlassian import jira


main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template('index.html')

@main.route('/gerar_descricao')
def call_gpt():
    return "text"
