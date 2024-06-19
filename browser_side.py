import requests

def make_session(token):
    session = requests.Session()
    session.cookies.set("_ncfa", token, domain="www.geoguessr.com")
    return session

def create_challenge(session, map_id):
    challenge = session.post("https://www.geoguessr.com/api/v3/challenges", json={
        'forbidMoving': True,
        'forbidRotating': False,
        'forbidZooming': False,
        'map': map_id,
        'rounds': 5,
        'timeLimit': 120
    })
    assert challenge.status_code == 200
    challenge_token = challenge.json()['token']
    return challenge_token

def get_results(session, challenge_token):
    game_token = session.post(f"https://www.geoguessr.com/api/v3/challenges/{challenge_token}").json()['token']

    # Play the game (time out every round) until it's over
    for i in range(100):
        session.get(f"https://www.geoguessr.com/api/v3/games/{game_token}?client=web")
        resp = session.post(f"https://www.geoguessr.com/api/v3/games/{game_token}", json={
            'lat': 0,
            'lng': 0,
            'timedOut': True,
            'token': game_token
        })
        if resp.status_code != 200:
            break

    scoreboard = session.get(f"https://www.geoguessr.com/api/v3/results/highscores/{challenge_token}?friends=false&limit=26&minRounds=5")
    assert scoreboard.status_code == 200
    scoreboard = scoreboard.json()

    # Remove players that timed out all rounds
    results = {}
    results['roundCount'] = scoreboard['items'][0]['game']['roundCount']
    results['timeLimit'] = scoreboard['items'][0]['game']['timeLimit']
    results['players'] = []
    for player in scoreboard['items']:
        timed_out_all = True
        for guess in player['game']['player']['guesses']:
            if not guess['timedOut']:
                timed_out_all = False
                break
        if not timed_out_all:
            pl = {}
            pl['playerName'] = player['playerName']
            pl['totalScore'] = player['totalScore']
            pl['rounds'] = []
            for i in range(results['roundCount']):
                round = {
                    'lat': player['game']['rounds'][i]['lat'],
                    'lng': player['game']['rounds'][i]['lng'],
                    'guessLat': player['game']['player']['guesses'][i]['lat'],
                    'guessLng': player['game']['player']['guesses'][i]['lng'],
                    'guessTime': player['game']['player']['guesses'][i]['time'],
                    'distanceMiles': player['game']['player']['guesses'][i]['distance']['miles']['amount'],
                    'roundScore': player['game']['player']['guesses'][i]['roundScore']['amount']
                }
                pl['rounds'].append(round)
            results['players'].append(pl)
    return results
