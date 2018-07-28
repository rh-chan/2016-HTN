import os
import sqlite3

from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
from yelp_search import return_search
import json
import rank_algo

app = Flask(__name__)
app.config.from_object(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'choosr.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)


@app.route('/')

def hello_world():
  return render_template('index.html')

def connect_db():
	# Connects to the DB
	rv = sqlite3.connect(app.config['DATABASE'])
	rv.row_factory = sqlite3.Row
	return rv


def init_db():
	"""Initializes the database."""
	db = get_db()
	with app.open_resource('schema.sql', mode='r') as f:
	    db.cursor().executescript(f.read())
	db.commit()


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    with app.app_context():
	    if not hasattr(g, 'sqlite_db'):
	        g.sqlite_db = connect_db()
	    return g.sqlite_db
# users table operations
def add_to_users(room_id, name, suggestion_status, ranking_status):
    db = get_db()
    db.execute("""INSERT INTO users (room_id, name, suggestion_status, ranking_status)
                VALUES (?, ?, ?, ?)""",
               [room_id, name, suggestion_status, ranking_status])
    db.commit()
    cur = db.execute("SELECT max(user_id) FROM users")
    user_id = cur.fetchone()[0]
    return user_id


def retrieve_from_users(room_id):
    db = get_db()
    cur = db.execute("SELECT * FROM users WHERE room_id=?", room_id)
    entries = cur.fetchall()
    return entries

def delete_from_users(user_id):
    db = get_db()
    db.execute("DELETE FROM users WHERE user_id=?", user_id)
    db.commit()

def update_user_suggestion_status(user_id, suggestion_status):
    db = get_db()
    db.execute("UPDATE users SET suggestion_status=? WHERE user_id=?", [suggestion_status, user_id])
    db.commit()

def update_user_ranking_status(user_id, ranking_status):
    db = get_db()
    db.execute("UPDATE users SET ranking_status=? WHERE user_id=?", [ranking_status, user_id])
    db.commit()

# room table operations
def add_to_room(room_name, status):
    db = get_db()
    db.execute("INSERT INTO rooms (room_name, status) VALUES (?, ?)",
                     [room_name, status])
    db.commit()
    cur = db.execute("SELECT max(room_id) FROM rooms")
    room_id = cur.fetchone()[0]
    return room_id

def retrieve_from_room(room_id):
    db = get_db()
    cur = db.execute("SELECT status FROM rooms WHERE room_id=?", room_id)
    return cur.fetchall()[0][0]

def delete_from_room(room_id):
    db = get_db()
    db.execute("DELETE FROM rooms WHERE room_id=?", room_id)
    db.commit()

def update_room_status(room_id, status):
    db = get_db()
    db.execute("UPDATE rooms SET status=? WHERE room_id=?", [status, room_id])
    db.commit()

def retrieve_room_submitted(room_id):
    db = get_db()
    cur = db.execute("""SELECT name FROM users WHERE room_id=? AND suggestion_status='true'""", room_id)
    entries = cur.fetchall()
    return entries

# suggestions table operations
def add_to_suggestions(room_id, suggestions, rank):
    db = get_db()
    suggestions_list = json.loads(suggestions)
    for suggestion in suggestions_list:
        address = suggestion['location_address'][0]
        db.execute("INSERT INTO suggestions (room_id, suggestion, suggestion_name, rating, address, rank) values (?, ?, ?, ?, ?, ?)",
                    [room_id, suggestion['id'], suggestion['name'], suggestion['rating'], address, rank])
    db.commit()

def retrieve_from_suggestions(room_id):
    db = get_db()
    cur = db.execute("SELECT * FROM suggestions WHERE room_id=?", room_id)
    rows = [x for x in cur]
    cols = [x[0] for x in cur.description]
    suggestions = []
    for row in rows:
        suggestion = {}
        for prop, val in zip(cols, row):
            suggestion[prop] = val
        suggestions.append(suggestion)
    return suggestions

def delete_from_suggestions(room_id):
    db = get_db()
    db.execute("DELETE FROM suggestions WHERE room_id=?", room_id)
    db.commit()

def update_suggestions_rank(room_id, suggestion, rank):
    db = get_db()
    db.execute("UPDATE suggestions SET rank=? WHERE room_id=? AND suggestion=?", [rank, room_id, suggestion])
    db.commit()

# user_rankings table operations
def add_to_user_rankings(user_id, suggestion, rank):
    db = get_db()
    db.execute("INSERT INTO user_rankings (user_id, suggestion, rank) VALUES (?, ? ,?)",
               [user_id, suggestion, rank])
    db.commit()

def retrieve_from_user_rankings(user_id):
    db = get_db()
    cur = db.execute("SELECT * FROM user_rankings WHERE user_id=?", user_id)
    entries = cur.fetchall()
    return entries

def delete_from_user_rankings(user_id):
    db = get_db()
    db.execute("DELETE FROM user_rankings WHERE room_id=?", user_id)
    db.commit()

def rank_algo_candidates(room_id):
    db = get_db()
    cur = db.execute("SELECT suggestion FROM suggestions WHERE room_id = ? ", room_id)
    entries = cur.fetchall()
    candidates = [candidate[0] for candidate in entries]
    return candidates

def rank_algo_suggestion_rank(room_id):
    db = get_db()
    cur = db.execute("SELECT user_id, suggestion, rank FROM user_rankings NATURAL JOIN users WHERE users.room_id = ?", room_id)
    rows = [x for x in cur]
    cols = [x[0] for x in cur.description]
    rankings = []
    for row in rows:
        user_ranking = {}
        for prop, val in zip(cols, row):
            user_ranking[prop] = val
        rankings.append(user_ranking)

    #parsing
    intermed_dict = {}
    for d in rankings:
        user_id = str(d['user_id'])
        if user_id in intermed_dict:
            intermed_dict[user_id].append({'rank': d['rank'], 'suggestion': d['suggestion']})
        else:
            intermed_dict[user_id] = [{'rank': d['rank'], 'suggestion': d['suggestion']}]

    output = []
    for index, value in intermed_dict.iteritems():
        ranking_dict = {}
        for v in value:
            ranking_dict[v['suggestion']] = v['rank']
        output.append(ranking_dict)
    return output

@app.route('/yelp_search', methods=['GET'])
def yelp_search():
  if request.method == 'GET':
    search_string = request.args.get('name')
    location = request.args.get('location')
    businesses_json = return_search(search_string, location)
    return json.dumps(businesses_json)

@app.route('/room', methods=['GET', 'POST'])
def room():
    if request.method == 'POST':
        room_id = add_to_room(request.form['room_name'], 0)
        user_id = add_to_users(room_id, request.form['name'], 'false', 'false')
        return json.dumps({'room_id': room_id, 'user_id': user_id})
    elif request.method == 'GET':
        room_data = retrieve_from_room(request.args.get('room_id'))
        return json.dumps(room_data)


@app.route('/user', methods=['GET', 'POST'])
def user():
    if request.method == 'POST':
        user_id = add_to_users(request.form['room_id'], request.form['name'], 'false', 'false')
        return json.dumps(user_id)
    elif request.method == 'GET':
        user_data = retrieve_from_users(request.args.get('room_id'))
        return json.dumps(user_data)

@app.route('/suggestions', methods=['GET', 'POST'])
def suggestions():
    if request.method == 'POST':
        add_to_suggestions(request.form['room_id'], request.form['suggestions'], 0)
        update_user_suggestion_status(request.form['user_id'], "true")
        return json.dumps("yes")
    elif request.method == 'GET':
        suggestions = retrieve_from_suggestions(request.args.get('room_id'))
        return json.dumps(suggestions)


@app.route('/room_submitted', methods=['GET', 'POST'])
def room_submitted():
    if request.method == 'GET':
        submitted_users = retrieve_room_submitted(request.args.get('room_id'))
        return_list= [user[0] for user in submitted_users]
        return json.dumps(return_list)

@app.route('/update_room_status', methods=['GET'])
def update_room_status_route():
    if request.method == 'GET':
        room_id = request.args.get('room_id')
        update_room_status(room_id,2)
        return json.dumps("Room: {} status updated".format(room_id))


@app.route('/user_rankings', methods=['GET', 'POST'])
def user_rankings():
    if request.method == 'POST':
        add_to_user_rankings(request.form['name'], request.form['suggestions'], request.form['rank'])
    elif request.method == 'GET':
        user_rankings = retrieve_from_user_rankings(request.args.get('user_id'))
        return json.dumps(user_rankings)

@app.route('/rank_algo', methods=['GET', 'POST'])
def rank_algo_endpoint():
    if request.method == 'GET':
        room_id = request.args.get('room_id')
        parsed_data = rank_algo.parse_ranks(rank_algo_suggestion_rank(room_id))
        ranked_candidates = rank_algo.compute_ranks(rank_algo_candidates(room_id), parsed_data)
        db = get_db()
        for index, candidate in enumerate(ranked_candidates):
            db.execute("UPDATE suggestions SET rank=? WHERE room_id=? AND suggestion=?", [index, int(room_id),  candidate[0]])
        db.commit()
        return json.dumps(ranked_candidates)

@app.route('/suggestion_vote', methods=['POST'])
def suggestion_vote():
    if request.method == 'POST':
        user_id = request.form['user_id']
        rank = request.form['rank']
        suggestion = request.form['suggestion']
        add_to_user_rankings(user_id, suggestion, rank)
        return json.dumps('ma nig is ice')

@app.route('/voting_end', methods=['POST'])
def voting_end():
    if request.method == 'POST':
        user_id = request.form['user_id']
        update_user_ranking_status(user_id, "true")
        return json.dumps('updated user_ranking_status')

@app.route('/check_room_votes', methods=['GET'])
def check_room_votes():
    if request.method == 'GET':
        room_id = request.args.get('room_id')
        db = get_db()
        cur = db.execute("SELECT count('user_id') FROM users WHERE room_id=? AND ranking_status='false'", [room_id])
        status = cur.fetchone()[0]
        result = False
        if status == 0:
            result = True
        return json.dumps(result)


if __name__ == '__main__':
  connect_db()
  init_db()

  app.run(debug=True, port=8000, host='0.0.0.0')
