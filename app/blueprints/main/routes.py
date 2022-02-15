from .import bp as main
from .forms import BattleForm, TeamForm, OpponentForm
from flask import render_template, request, flash, redirect, url_for
import requests
from flask_login import login_required, current_user
from app.models import User, Pokemon, UserPokemon, Result
from random import randint
from sqlalchemy import desc

# Routes

@main.route('/', methods=['GET'])
def index():
    return render_template('index.html.j2')

@main.route('/team', methods = ['GET', 'POST'])
@login_required
def team():
    form = TeamForm()
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

            # user = User
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

            return render_template('team.html.j2', form=form, pokemen = current_user.pokemen)

        else:
            flash(f"{name.title() } does not exist. Please try again.")
            return render_template('team.html.j2', form=form, pokemen = current_user.pokemen)
 
    else: # if its a get request
        return render_template('team.html.j2', form=form, pokemen = current_user.pokemen)

@main.route('/delete/<int:id>')
@login_required
def delete(id):
    poke =  UserPokemon.query.get((id, current_user.id))
    poke.delete()
    flash(f'{Pokemon.query.get(id).name.title()} was deleted.')
    return redirect(url_for('main.team'))

@main.route('/opponent', methods = ['GET', 'POST'])
@login_required
def opponent():
    form = OpponentForm()
    form.opponent.query = User.query.filter(User.id != current_user.id).order_by(User.full_name)

    if request.method == 'POST' and form.validate_on_submit():

        if len(list(current_user.pokemen)) == 5: #check to see if User has 5 pokemon
            opponent_id = request.form.get('opponent')
            opponent = User.query.get(opponent_id)

            if len(list(opponent.pokemen)) == 5: #check to see if Opponent has 5 pokemon

                return render_template('opponent.html.j2', form=form, pokemen=opponent.pokemen, id=opponent_id)
            else:
                flash(f'{opponent.full_name.title()} has not essembled a team. Please select a different opponent')
                return render_template('opponent.html.j2', form=form)
        else:
            #User does not have 5 pokemon to battle with
            flash('You have not essembled a 5 member team. Please select more Pokemon')
            return render_template('opponent.html.j2', form=form)        
  
    # else: # if its a get request
    return render_template('opponent.html.j2', form=form)

@main.route('/battle/<int:id>', methods = ['GET', 'POST'])
@login_required
def battle(id=None):
    form = BattleForm()
    u_poke = current_user.pokemen
    o_poke = User.query.get(id)

    if request.method == 'POST':
        u_select = int(form.icon.data) #User's choice
        o_select = randint(1,3) #Opponents choice

        if u_select == 1:
            u_selection_text = "Rock"
        elif u_select == 2:
            u_selection_text = "Paper"
        elif u_select == 3:
            u_selection_text = "Scissors"

        if o_select == 1:
            selection_text = "Rock"
        elif o_select == 2:
            selection_text = "Paper"
        elif o_select == 3:
            selection_text = "Scissors"
        
        if u_select == 1 and o_select == 1: #User selects Rock and Opponent selects Rock
            outcome = "draw"
        elif u_select == 1 and o_select == 2: #User selects Rock and Opponent selects Paper
            outcome = "lose"
        elif u_select == 1 and o_select == 3: #User selects Rock and Opponent selects Scissors
            outcome = "win"
        if u_select == 2 and o_select == 1: #User selects Paper and Opponent selects Rock
            outcome = "win"
        elif u_select == 2 and o_select == 2: #User selects Paper and Opponent selects Paper
            outcome = "draw"
        elif u_select == 2 and o_select == 3: #User selects Paper and Opponent selects Scissors
            outcome = "lose"  
        if u_select == 3 and o_select == 1: #User selects Scissors and Opponent selects Rock
            outcome = "lose"
        elif u_select == 3 and o_select == 2: #User selects Scissors and Opponent selects Paper
            outcome = "win"
        elif u_select == 3 and o_select == 3: #User selects Scissors and Opponent selects Scissors
            outcome = "draw"                       

        if outcome == "draw":
            flash(o_poke.full_name + " selects " + selection_text + ". You tied!", "info")
        else:
            flash(o_poke.full_name + " selects " + selection_text + ". You " + outcome + "!", "error")

        result_dict = {
            "result":outcome.title(),
            "selection":u_selection_text,
            "user_id":current_user.id
        }

        #save results
        result = Result()
        result.from_dict(result_dict)
        result.save()

    return render_template('battle.html.j2', form=form, id=id, o_poke=o_poke.pokemen, \
        u_poke=u_poke, u_name=current_user.full_name, o_name=o_poke.full_name)

@main.route('/results')
@login_required
def results():

    result = Result()

    results = result.query.filter_by(user_id=current_user.id).order_by(desc('created_on')).limit(8)

    wins = result.query.filter_by(result='Win', user_id=current_user.id).count()
    losses = result.query.filter_by(result='Lose', user_id=current_user.id).count()
    draws = result.query.filter_by(result='Draw', user_id=current_user.id).count()
    total_results = wins + losses + draws

    rocks = result.query.filter_by(selection='Rock', user_id=current_user.id).count()
    papers = result.query.filter_by(selection='Paper', user_id=current_user.id).count()
    scissors = result.query.filter_by(selection='Scissors', user_id=current_user.id).count()
    total_selection = rocks + papers + scissors

    if total_results > 0:
        line1 = f"Winning Percentage = {(round(wins/total_results*100))}% &nbsp Wins = {wins} \
            &nbsp Losses = {losses} &nbsp Draws = {draws}"
        line2 = f"Rock Used = {(round(rocks/total_selection*100))}% &nbsp Paper Used = \
            {(round(papers/total_selection*100))}% &nbsp Scissors Used = \
                {(round(scissors/total_selection*100))}%" 
    else:
        line1 = "You need to battle before you get results! Go have some fun!"
        line2 = ""

    return render_template('results.html.j2', line1=line1, line2=line2, results=results)