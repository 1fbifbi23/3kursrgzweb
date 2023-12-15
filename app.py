from flask import Flask, redirect, url_for, render_template, Blueprint, request
from rgz import rgz

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
app.secret_key = '123'

app.register_blueprint(rgz)

