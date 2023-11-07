from app import *
from statistics import mean,mode
from bs4 import BeautifulSoup
from datetime import datetime, date
import time
import requests
import ipdb

with app.app_context():


    '''what data does it need for each player?
        Player game data from similar games
            -last 5 games home/away (wherever they are playing)
            -last 8 games at specific time
            -5 most recent games
            -10 most recent matchups against this team
        If there are injuries
            -check if the roster contains anyone on the injured list. If it does, find games where at least 5 players were on the roster and not the injured one. Take up to 5 of those games
            -check the latest few similar games (listed above) and redistribute the stats that player would have earned

    '''



    #parse espn injury page
    injury_url = "https://www.espn.com/nba/injuries"
    injury_page = requests.get(injury_url, headers={'User-Agent':"Mozilla/5.0"})
    injuries = BeautifulSoup(injury_page.text, 'html.parser')
    injury_page = injuries.select('.ResponsiveTable')

    #collect injury dictionary
    injured_list = {}

    for injured in injury_page:
        team_name = injured.select('.Table__Title')[0].text
        
        players = injured.select('tbody')[0].select('tr')
        injured_players = []
        for player in players:
            if player.select('td')[3].text=='Out':
                injured_players.append(player.select('td')[0].text)
                
        injured_list[team_name] = injured_players



    action_network_points_url = 'https://sportsbook.draftkings.com/leagues/basketball/nba?category=player-points&subcategory=points'
    action_network_assists_url = 'https://sportsbook.draftkings.com/leagues/basketball/nba?category=player-assists&subcategory=assists'
    action_network_rebounds_url = 'https://sportsbook.draftkings.com/leagues/basketball/nba?category=player-rebounds&subcategory=rebounds'

    action_network_points = requests.get(action_network_points_url, headers={'User-Agent':"Mozilla/5.0"})
    action_network_assists = requests.get(action_network_assists_url, headers={'User-Agent':"Mozilla/5.0"})
    action_network_rebounds = requests.get(action_network_rebounds_url, headers={'User-Agent':"Mozilla/5.0"})

    points = BeautifulSoup(action_network_points.text, 'html.parser')
    assists = BeautifulSoup(action_network_assists.text, 'html.parser')
    rebounds = BeautifulSoup(action_network_rebounds.text, 'html.parser')





    odds_dict = {}
    all_players = Player.query.all()
    for player in all_players:
        odds_dict[player.name]={}

    game_points = points.select('tbody')
    
    for match in game_points:
        points_rows = match.select('tr')
        
        for row in points_rows:
            name = row.select('.sportsbook-row-name')[0].text
            if name.endswith(" "):
                name = name.rstrip(name[-1])
            if name in odds_dict:
                line = float(row.select('.sportsbook-outcome-cell__line')[0].text)
                odds_dict[name]["points"] = line
            else:
                odds_dict[name] = {}
                odds_dict[name]["points"] = line

    game_assists = assists.select('tbody')

    for match in game_assists:
        assists_rows = match.select('tr')
        
        for row in assists_rows:
            name = row.select('.sportsbook-row-name')[0].text
            if name.endswith(" "):
                name = name.rstrip(name[-1])
            if name in odds_dict:
                line = float(row.select('.sportsbook-outcome-cell__line')[0].text)
                odds_dict[name]["assists"] = line
            else:
                odds_dict[name] = {}
                odds_dict[name]["assists"] = line

    game_rebounds = rebounds.select('tbody')

    for match in game_rebounds:
        rebounds_rows = match.select('tr')
        
        for row in rebounds_rows:
            name = row.select('.sportsbook-row-name')[0].text
            if name.endswith(" "):
                name = name.rstrip(name[-1])
            if name in odds_dict:
                line = float(row.select('.sportsbook-outcome-cell__line')[0].text)
                odds_dict[name]["rebounds"] = line
            else:
                odds_dict[name] = {}
                odds_dict[name]["rebounds"] = line

    new_odds_dict = odds_dict.copy()

    for item in odds_dict:
        if odds_dict[item] == {}:
            del(new_odds_dict[item])

    ipdb.set_trace()

    #new_odds_dict is a dicitonary of all today's props



    #collect data
    player_home_or_away = True
    player_name = "Jalen Green"
    player_team = "Houston Rockets"
    other_team = "Sacramento Kings"
    game_time = datetime.time(19,30)

    injury = False
    opponent_injury = False
    games_with_injury = []
    games_with_opp_injury = []

    #collect my own data about every game they've played in
    current_player = Player.query.filter(Player.name==player_name).first()
    games = current_player.games

   

    #we got the injuries. Time to check the roster



    #loop of game players if there is an injury and filter down to only games they have not played in. If the list
    #is not big enough, include recent games but add that players average stats rationed to the rest of the team

    #if the other team has injuries, try to find matchups against them without that player
    if player_team in injured_list:
        injury = True
        games_with_injury = games.copy()
        #gets all the players in each game
        for game_players in [game.game.players for game in games]:
            #this_current_player is the current player's specific PlayerGame
            this_current_player = [game for game in game_players if game.player.name==current_player.name][0]
            team_players = [player for player in game_players if player.home==this_current_player.home]
            team_player_names = [player.player.name for player in team_players]
            #make a new injured list with only starters
            
            for injured_player in (injured_list[player_team]):
                injured_player_games = Player.query.filter(Player.name==injured_player).first().games[-3:]
                minutes = mean([game.minutes for game in injured_player_games])
                if minutes > 2000:
                    if injured_player in team_player_names and this_current_player in games_with_injury:
                        games_with_injury.remove(this_current_player)


   
   
    #latest 5 games at time
    games_at_time = [game for game in games if game.game.date.time()==game_time][-3:]


    #last 5 games
    latest_games = [game for game in games][-3:]
    #last 8 home/away games
    latest_home_or_away_games = [game for game in games if game.home==player_home_or_away][-10:]

    
    #get latest matchups vs team
    #check recent minutes
    minutes_list = [game.minutes for game in latest_games]
    minutes = mean(minutes_list)
    
    games_vs_opponent = [game for game in games if (game.game.home==other_team or game.game.visitor==other_team)][-8:]

            
   
    

    #check opponent injuries

    if other_team in injured_list:
        opponent_injury = True
        games_with_opp_injury = games_vs_opponent.copy()
        #gets all the players in each game
        for game_players in [game.game.players for game in games]:
            #this_current_player is the current player's specific PlayerGame
            this_current_player = [game for game in game_players if game.player.name==current_player.name][0]
            opponent_players = [player for player in game_players if player.home!=this_current_player.home]
            opponent_player_names = [player.player.name for player in opponent_players]
            #make a new injured list with only starters
            
            for injured_player in (injured_list[other_team]):
                if Player.query.filter(Player.name==injured_player):
                    injured_player_games = Player.query.filter(Player.name==injured_player).first().games[-5:]
                    minutes = mean([game.minutes for game in injured_player_games])
                    if minutes > 2000:
                        if injured_player in opponent_player_names and this_current_player in games_with_opp_injury:
                            games_with_opp_injury.remove(this_current_player)
   



    #make a big array of games
    latest_home_or_away_games.extend(latest_games)
    latest_home_or_away_games.extend(games_at_time)
    latest_home_or_away_games.extend(games_vs_opponent)
    if injury:
        latest_home_or_away_games.extend(games_with_injury[-3:])
    if opponent_injury:
        latest_home_or_away_games.extend(games_with_opp_injury[-3:])

    #find most similar game
    most_similar = mode(latest_home_or_away_games)
    assists_similar = most_similar.assists
    points_similar = most_similar.points
    trb_similar = most_similar.trb


    new_game_list = set(latest_home_or_away_games)

    uniq_game_list = list(new_game_list)

    uniq_game_list = [game for game in uniq_game_list if (minutes-minutes*.15 <= game.minutes <=minutes+minutes*.9)]

    assists_list = [game.assists for game in uniq_game_list]
    points_list = [game.points for game in uniq_game_list]
    trb_list = [game.trb for game in uniq_game_list]

    assists_factor = mean(assists_list)
    points_factor = mean(points_list)
    trb_factor = mean(trb_list)

    assists_predict = 0.6*assists_factor+0.4*assists_similar
    points_predict = 0.6*points_factor+0.4*points_similar
    trb_predict = 0.6*trb_factor+0.4*trb_similar

    ipdb.set_trace()

    print("hi")
