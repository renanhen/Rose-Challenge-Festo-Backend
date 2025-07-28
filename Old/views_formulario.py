from flask import render_template, request, redirect, session, flash, url_for
from Old.app import app

@app.route('/')
def index():
    return render_template('formulario.html', titulo="Previsão")


