from .import bp as main
from .forms import EntryForm
from flask import render_template, request, flash #, redirect, url_for
import requests
from flask_login import login_required, current_user #, login_user, logout_user
from app.models import User, Pokemon, UserPokemon

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

            #check to see if pokemon is in database, if not add
            poke = Pokemon.query.filter(Pokemon.name==name).first()
            
            if not poke:
                #create an empty pokemon
                new_poke = Pokemon()
                #build pokemon with dict data
                new_poke.from_dict(pokemon_dict)
                #save pokemon to the database
                new_poke.save()
                poke = new_poke

            # user = current_user
            if list(current_user.pokemen) != []: #check to see if user has any pokemon
                if len(list(current_user.pokemen)) < 5: #check to see if user already has 5 pokemon
                    poke_list = list(current_user.pokemen)
                    if poke not in poke_list:
                        if not poke.users: #check to see if another user already has this pokemon
                            current_user.pokemen.append(poke)
                            current_user.save()
                            flash(f'You have added {poke.name.title()} to your team!')
                        else:
                            flash(f'Sorry another user already has {poke.name.title()}. Please try a different Pokemon.')
                    else:
                        flash(f'You already have {poke.name.title()} on your team!')
                else:
                    flash('You already have 5 Pokemon. Please delete an existing Pokemon before adding another.')
            else:
                if not poke.users: #check to see if another user already has this pokemon
                    current_user.pokemen.append(poke)
                    current_user.save()
                    flash(f'You have added {poke.name.title()} to your team!')
                else:
                    flash(f'Sorry another user already has {poke.name.title()}. Please try a different Pokemon.')

            return render_template('entry.html.j2', form=form, pokemon = pokemon_dict)

        else:
            flash(f"{name.title()} does not exist. Please try again.")
            return render_template('entry.html.j2', form=form)
 
    else: # if its a get request
        return render_template('entry.html.j2', form=form)