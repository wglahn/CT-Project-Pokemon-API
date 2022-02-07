from .import bp as main
from .forms import EntryForm
from flask import render_template, request #, flash, redirect, url_for
import requests
from flask_login import login_required #, login_user, current_user, logout_user

# Routes

@main.route('/', methods=['GET'])
def index():
    return render_template('index.html.j2')

@main.route('/entry', methods = ['GET', 'POST'])
@login_required
def entry():
    form = EntryForm()
    if request.method == 'POST' and form.validate_on_submit():
        name = request.form.get('name').lower()
        url = f"https://pokeapi.co/api/v2/pokemon/{name}"
        response = requests.get(url)
        if response.ok:
            pokemon_dict={
                "name":response.json()['forms'][0]['name'],
                "ability":response.json()['abilities'][0]['ability']['name'],
                "hp":response.json()['stats'][0]['base_stat'],
                "attack":response.json()['stats'][1]['base_stat'],
                "defense":response.json()['stats'][2]['base_stat'],
                "sprite": response.json()['sprites']['front_shiny']
                }
            return render_template('entry.html.j2', form=form, pokemon = pokemon_dict)

        else:
            error_string = f"{name} does not exist. Please try again."
            return render_template('entry.html.j2', form=form, error = error_string)
 
    else: # if its a get request
        return render_template('entry.html.j2', form=form)