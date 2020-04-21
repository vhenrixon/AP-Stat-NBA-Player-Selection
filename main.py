from __future__ import print_function   
from nba_api.stats.endpoints import playercareerstats
from nba_api.stats.static import players
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import random
# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1q_UxIZU8_-qr9ufR89KKkUOXyQo3zEQ_ii0EHj5FUVs'
SAMPLE_RANGE_NAME = 'A2:G100'
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
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                range=SAMPLE_RANGE_NAME).execute()
    values = result.get('values', [])
    print(values)

def number_assingment(players):
    selection_number = 0
    for player in players: 
        player["number"] = selection_number
        selection_number = selection_number + 1

def select(nba_players):
    used_values = [] 
    for i in range(90): 
        r = random.randint(0,len(nba_players))
        if r not in used_values: 
            selected_player.append(nba_players[i])
        else:
            i = i-1

def getPlayerInfo(players):
    for player in players: 
        carrer_stats = playercareerstats.PlayerCareerStats(player_id=player["id"]).get_dict()
        #parse_selected['full_name'] = player['full_name']
        #parse_selected['FG_PCT'] = carrer_stats['SeasonTotalsRegularSeason'][11] WRONG! 
        #parse_selected['FG3_PCT'] = carrer_stats['SeasonTotalsRegularSeason'][14]
        # FGA for the shots attempted 
        
        #Big rip I messed up! 
        #The SeasonTotalsRegular needs to also the season like 2019-20 which means I need to parse that data out and then find the info I need 
        

def main():
    nba_players = players.get_active_players()
    connect_spreadsheet()
    if nba_players is not None:
        number_assingment(nba_players)
        select(nba_players)
        getPlayerInfo(selected_player)

if __name__ == "__main__":
    main()

