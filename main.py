from __future__ import print_function   
from nba_api.stats.endpoints import playercareerstats
from nba_api.stats.static import players
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import random
import requests
import time
# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = '1q_UxIZU8_-qr9ufR89KKkUOXyQo3zEQ_ii0EHj5FUVs'
sheet = None
nba_players = None    

selected_player = []
parse_selected = []

def connect_spreadsheet():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    return sheet 

def number_assingment(players):
    selection_number = 0
    for player in players: 
        player["number"] = selection_number
        selection_number = selection_number + 1

def select(nba_players):
    used_values = [] 
    for i in range(100): 
        r = random.randint(0,len(nba_players))
        if r not in used_values and playerCheck(nba_players[r]):
            print("Player Selected")
            selected_player.append(nba_players[r])
            used_values.append(r)
        else:
            i = i-1

def findSeason(season_tag, carrer_stats_raw):
    for season in carrer_stats_raw['rowSet']: 
        if season[1] == season_tag:
            return season

def parseCareerStats(carrer_stats): 
    value = {}
    base = carrer_stats['resultSets'][0]
    season = findSeason('2019-20', base)
    value["FG_PCT"] = season[11]
    value["FG3_PCT"] = season[14]
    value["FGA"] = season[10]
    return value

def playerCheck(player): 
    while(True):
        try:
            print("Player check inside")
            carrer_stats = playercareerstats.PlayerCareerStats(player_id=player["id"]).get_dict()
            base = carrer_stats['resultSets'][0] 
            print("Player check")
            if findSeason('2019-20', base) is None:
                return False
            else:
                return True
        except requests.exceptions.Timeout:
            print("Player check failed")
            continue

def getPlayerInfo(players):
    queue = []
    for player in players: 
        player_value = {}
        try:
            carrer_stats = playercareerstats.PlayerCareerStats(player_id=player["id"]).get_dict()
            player_value['full_name'] = player['full_name']
            stats = parseCareerStats(carrer_stats)
            player_value['FG_PCT'] = stats['FG_PCT']
            player_value['FG3_PCT'] = stats['FG3_PCT']
            player_value['FGA'] = stats['FGA']
            # Add points for 2 and 3
            player_value["2_Points"] = stats['FGA'] * stats['FG_PCT']
            player_value["3_Points"]  =stats['FGA'] * stats['FG3_PCT']
            parse_selected.append(player_value)
        except requests.exceptions.Timeout:
            print("Failed and added to queue")
            queue.append(player)
            continue
    while(len(queue) != 0):
        player_value = {}
        try: 
            player = queue[len(queue)-1]
            carrer_stats = playercareerstats.PlayerCareerStats(player_id=player["id"]).get_dict()  
            player_value['full_name'] = player['full_name'] 
            stats = parseCareerStats(carrer_stats)  
            player_value['FG_PCT'] = stats['FG_PCT']
            player_value['FG3_PCT'] = stats['FG3_PCT'] 
            player_value['FGA'] = stats['FGA'] 
            player_value["2_Points"] = stats['FGA'] * stats['FG_PCT']
            player_value["3_Points"] = stats['FGA'] * stats['FG3_PCT']
            parse_selected.append(player_value)
            queue.pop(len(queue)-1)
            print("Pop out of the queue")
        except requests.exceptions.Timeout:
            print("Request failed in queue")
            continue
def setValuesInGoogle(parse_selected, sheet):
    print("Adding values to google sheet")
    for n in range(len(parse_selected)-1):
        srange = "A"+str(n+1)+":F"
        player = parse_selected[n]
        _body = {"values":[
            [player['full_name'], player['FG_PCT'], player['FG3_PCT'], player['FGA'], player['2_Points'], player['3_Points']]
                ]}
        sheet.values().append(spreadsheetId=SPREADSHEET_ID, range=srange, valueInputOption="RAW", body=_body).execute()

def main():
    nba_players = players.get_active_players()
    s = connect_spreadsheet()
    if nba_players is not None:
        print("Assigning Player")
        number_assingment(nba_players)
        print("Selecting Player")
        select(nba_players)
        print("Getting Player info")
        getPlayerInfo(selected_player)
        #Place data in the form 
        setValuesInGoogle(parse_selected, s)

if __name__ == "__main__":
    main()

