from app import *
from statistics import mean,mode
from bs4 import BeautifulSoup
from datetime import datetime, date, timedelta
from operator import itemgetter
from sqlalchemy import or_
from scrape_a_day import scrape_a_day
import calendar
import itertools
import time
import requests
import ipdb


with app.app_context():

    time_url = "https://time.is/"
    time_page = requests.get(time_url, headers = {'User-Agent':"Mozilla/5.0"})
    time_doc = BeautifulSoup(time_page.text, 'html.parser')
    date_string = time_doc.select("#dd")[0].text
    time_string = time_doc.select('#clock')[0].text 
    format_time = datetime.strptime(time_string,"%X%p").time()
    #set current date to todays date and run the algorithm to see projections
    current_date = datetime.strptime(date_string, "%A, %B %d, %Y").date()
    # current_date = datetime(2023,11,27).date()


    yesterday = current_date - timedelta(1)
    most_recent_game_date = Game.query.all()[-1].date.date()
    time_list = date_string.replace(",","").split()
    month = time_list[1].lower()
    year = int(time_list[3])
    end_months = ["september", "october", "november", "december"]
    if month in end_months:
        year = year+1
    year_string = str(year)

    

    month_of_yesterday = calendar.month_name[yesterday.month].lower()
    year_of_yesterday = yesterday.year
    if month_of_yesterday in end_months:
        year_of_yesterday = yesterday.year+1
    else:
        year_of_yesterday = yesterday.year
    year_of_yesterday_string = str(year_of_yesterday)

    if most_recent_game_date != yesterday:
        scrape_a_day(yesterday,month_of_yesterday,year_of_yesterday)
    else:
        print("All games have been downloaded\n")
    

    

    pra_switch = False

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


    '''Changes to make
        -Add and position to player class
        -Add team name to playergame class
        -Add how team does against that position
        -Edit injury algo so that it is much more specific
            -Checks that they played the game on their current team during those games
        -Change most similar game so that it takes the last most common

    '''

    #get game data

    schedule_page_url = f"https://www.basketball-reference.com/leagues/NBA_{year_string}_games-{month}.html"
    schedule_page = requests.get(schedule_page_url, headers = {'User-Agent':"Mozilla/5.0"})
    schedule = BeautifulSoup(schedule_page.text, 'html.parser')

    monthly_games = schedule.select('tbody')[0].select('tr')

    # current_date = date.today()

    


    todays_games = []
    list_of_teams = []
    for game in monthly_games:
        date = datetime.strptime(game.select('th')[0].text,"%a, %b %d, %Y").date()
        if date == current_date:
            game_data = {}
            game_data["home"] = game.select('td')[3].text
            game_data["away"] = game.select('td')[1].text
            list_of_teams.append(game.select('td')[3].text)
            list_of_teams.append(game.select('td')[1].text)
            my_time = game.select('td')[0].text

            empty_time = my_time.replace('p','').replace('a','').replace(":","")
            if my_time[-1]=='p':
                empty_time = str(int(empty_time)+1200)
                if int(empty_time) >= 2400:
                    empty_time = "0"+empty_time[2:4]
            if int(empty_time)<1000:
                empty_time = '0'+empty_time

            time = datetime.strptime(empty_time,"%H%M").time()
            game_data["time"]=time

            todays_games.append(game_data)



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


    #collect player prop data

    #create empty odds dictionary

    odds_dict = {}
    all_players = Player.query.all()
    for player in all_players:
        odds_dict[player.name]={}


    #draftkings player props

    action_network_points_url = 'https://sportsbook.draftkings.com/sites/US-SB/api/v5/eventgroups/42648/categories/1215?format=json'
    action_network_assists_url = 'https://sportsbook.draftkings.com/sites/US-SB/api/v5/eventgroups/42648/categories/1217?format=json'
    action_network_rebounds_url = 'https://sportsbook.draftkings.com/sites/US-SB/api/v5/eventgroups/42648/categories/1216?format=json'
   

    #action network player props

    # action_network_points_url = 'https://www.actionnetwork.com/nba/props/points'
    # action_network_assists_url = 'https://www.actionnetwork.com/nba/props/assists'
    # action_network_rebounds_url = 'https://www.actionnetwork.com/nba/props/rebounds'

    action_network_points = requests.get(action_network_points_url, headers={'User-Agent':"Mozilla/5.0"}, allow_redirects=False)
    action_network_assists = requests.get(action_network_assists_url, headers={'User-Agent':"Mozilla/5.0"}, allow_redirects=False)
    action_network_rebounds = requests.get(action_network_rebounds_url, headers={'User-Agent':"Mozilla/5.0"}, allow_redirects=False)

    try: 
        points_page = action_network_points.json()["eventGroup"]["offerCategories"][2]["offerSubcategoryDescriptors"][0]["offerSubcategory"]["offers"]
    except KeyError:
        try:
            points_page = action_network_points.json()["eventGroup"]["offerCategories"][3]["offerSubcategoryDescriptors"][0]["offerSubcategory"]["offers"]
        except KeyError:
            try:
                points_page = action_network_points.json()["eventGroup"]["offerCategories"][4]["offerSubcategoryDescriptors"][0]["offerSubcategory"]["offers"]
            except KeyError:
                try:
                    points_page = action_network_points.json()["eventGroup"]["offerCategories"][5]["offerSubcategoryDescriptors"][0]["offerSubcategory"]["offers"]
                except KeyError:
                    try:
                        points_page = action_network_points.json()["eventGroup"]["offerCategories"][6]["offerSubcategoryDescriptors"][0]["offerSubcategory"]["offers"]
                    except KeyError:
                        try:
                            points_page = action_network_points.json()["eventGroup"]["offerCategories"][7]["offerSubcategoryDescriptors"][0]["offerSubcategory"]["offers"]
                        except KeyError:
                            try:
                                points_page = action_network_points.json()["eventGroup"]["offerCategories"][8]["offerSubcategoryDescriptors"][0]["offerSubcategory"]["offers"]
                            except KeyError:
                                points_page = action_network_points.json()["eventGroup"]["offerCategories"][9]["offerSubcategoryDescriptors"][0]["offerSubcategory"]["offers"]

    try: 
        rebounds_page = action_network_rebounds.json()["eventGroup"]["offerCategories"][2]["offerSubcategoryDescriptors"][0]["offerSubcategory"]["offers"]
    except KeyError:
        try:
            rebounds_page = action_network_rebounds.json()["eventGroup"]["offerCategories"][3]["offerSubcategoryDescriptors"][0]["offerSubcategory"]["offers"]
        except KeyError:
            try:
                rebounds_page = action_network_rebounds.json()["eventGroup"]["offerCategories"][4]["offerSubcategoryDescriptors"][0]["offerSubcategory"]["offers"]
            except KeyError:
                try:
                    rebounds_page = action_network_rebounds.json()["eventGroup"]["offerCategories"][5]["offerSubcategoryDescriptors"][0]["offerSubcategory"]["offers"]
                except KeyError:
                    try:
                        rebounds_page = action_network_rebounds.json()["eventGroup"]["offerCategories"][6]["offerSubcategoryDescriptors"][0]["offerSubcategory"]["offers"]
                    except KeyError:
                        try:
                            rebounds_page = action_network_rebounds.json()["eventGroup"]["offerCategories"][7]["offerSubcategoryDescriptors"][0]["offerSubcategory"]["offers"]
                        except KeyError:
                            try:
                                rebounds_page = action_network_rebounds.json()["eventGroup"]["offerCategories"][8]["offerSubcategoryDescriptors"][0]["offerSubcategory"]["offers"]
                            except KeyError:
                                rebounds_page = action_network_rebounds.json()["eventGroup"]["offerCategories"][9]["offerSubcategoryDescriptors"][0]["offerSubcategory"]["offers"]


    try: 
        assists_page = action_network_assists.json()["eventGroup"]["offerCategories"][2]["offerSubcategoryDescriptors"][0]["offerSubcategory"]["offers"]
    except KeyError:
        try:
            assists_page = action_network_assists.json()["eventGroup"]["offerCategories"][3]["offerSubcategoryDescriptors"][0]["offerSubcategory"]["offers"]
        except KeyError:
            try:
                assists_page = action_network_assists.json()["eventGroup"]["offerCategories"][4]["offerSubcategoryDescriptors"][0]["offerSubcategory"]["offers"]
            except KeyError:
                try:
                    assists_page = action_network_assists.json()["eventGroup"]["offerCategories"][5]["offerSubcategoryDescriptors"][0]["offerSubcategory"]["offers"]
                except KeyError:
                    try:
                        assists_page = action_network_assists.json()["eventGroup"]["offerCategories"][6]["offerSubcategoryDescriptors"][0]["offerSubcategory"]["offers"]
                    except KeyError:
                        try:
                            assists_page = action_network_assists.json()["eventGroup"]["offerCategories"][7]["offerSubcategoryDescriptors"][0]["offerSubcategory"]["offers"]
                        except KeyError:
                            try:
                                assists_page = action_network_assists.json()["eventGroup"]["offerCategories"][8]["offerSubcategoryDescriptors"][0]["offerSubcategory"]["offers"]
                            except KeyError:
                                assists_page = action_network_assists.json()["eventGroup"]["offerCategories"][9]["offerSubcategoryDescriptors"][0]["offerSubcategory"]["offers"]
    
    for offer in points_page:
        for inside in offer:
            name = inside["outcomes"][0]["participant"]
            if name.endswith(" "):
                name = name.rstrip(name[-1])
            if name.startswith(" "):
                name = name[1:]
            line = inside["outcomes"][0]["line"]
            if name in odds_dict:
                odds_dict[name]["points"] = line
            else:
                odds_dict[name] = {}
                odds_dict[name]["points"] = line

    for offer in rebounds_page:
        for inside in offer:
            name = inside["outcomes"][0]["participant"]
            if name.endswith(" "):
                name = name.rstrip(name[-1])
            if name.startswith(" "):
                name = name[1:]
            line = inside["outcomes"][0]["line"]
            if name in odds_dict:
                odds_dict[name]["rebounds"] = line
            else:
                odds_dict[name] = {}
                odds_dict[name]["rebounds"] = line

    for offer in assists_page:
        for inside in offer:
            name = inside["outcomes"][0]["participant"]
            if name.endswith(" "):
                name = name.rstrip(name[-1])
            if name.startswith(" "):
                name = name[1:]
            line = inside["outcomes"][0]["line"]
            if name in odds_dict:
                odds_dict[name]["assists"] = line
            else:
                odds_dict[name] = {}
                odds_dict[name]["assists"] = line

    # odds_dict["Moritz Wagner"]["points"] = 13.5

    # assists = BeautifulSoup(action_network_assists.text, 'html.parser')
    # rebounds = BeautifulSoup(action_network_rebounds.text, 'html.parser')

    # action_network_pr_url = 'https://sportsbook.draftkings.com/leagues/basketball/nba?category=player-combos&subcategory=pts-+-reb'
    # action_network_pa_url = 'https://sportsbook.draftkings.com/leagues/basketball/nba?category=player-combos&subcategory=pts-+-ast'
    # action_network_ra_url = 'https://sportsbook.draftkings.com/leagues/basketball/nba?category=player-combos&subcategory=ast-+-reb'
   
    # action_network_pr = requests.get(action_network_pr_url, headers={'User-Agent':"Mozilla/5.0"})
    # action_network_pa = requests.get(action_network_pa_url, headers={'User-Agent':"Mozilla/5.0"})
    # action_network_ra = requests.get(action_network_ra_url, headers={'User-Agent':"Mozilla/5.0"})
    
    # pr = BeautifulSoup(action_network_pr.text, 'html.parser')
    # pa = BeautifulSoup(action_network_pa.text, 'html.parser')
    # ra = BeautifulSoup(action_network_ra.text, 'html.parser')



    #action network data collection

    # points_page = points.select('tbody')[0]
    # game_points = points_page.find_all('tr')
    # for row in game_points:
    #     name = row.select('td')[0].select('.total-prop-row__player-name')[0].text
    #     if name in odds_dict:
    #         line_num = row.select('td')[1].select('.css-1qynun2')[0].text[1:]
    #         line = float(line_num)
    #         odds_dict[name]["points"] = line
    #     else:
    #         odds_dict[name] = {}
    #         odds_dict[name]["points"] = line

    # assists_page = assists.select('tbody')[0]
    # game_assists = assists_page.find_all('tr')
    # for row in game_assists:
    #     name = row.select('td')[0].select('.total-prop-row__player-name')[0].text
    #     if name in odds_dict:
    #         line_num = row.select('td')[1].select('.css-1qynun2')[0].text[1:]
    #         line = float(line_num)
    #         odds_dict[name]["assists"] = line
    #     else:
    #         odds_dict[name] = {}
    #         odds_dict[name]["assists"] = line

    # rebounds_page = rebounds.select('tbody')[0]
    # game_rebounds = rebounds_page.find_all('tr')
    # for row in game_rebounds:
    #     name = row.select('td')[0].select('.total-prop-row__player-name')[0].text
    #     if name in odds_dict:
    #         line_num = row.select('td')[1].select('.css-1qynun2')[0].text[1:]
    #         line = float(line_num)
    #         odds_dict[name]["rebounds"] = line
    #     else:
    #         odds_dict[name] = {}
    #         odds_dict[name]["rebounds"] = line


    # if pra_switch:

    #     action_network_pra_url = 'https://sportsbook.draftkings.com/leagues/basketball/nba?category=player-combos&subcategory=pts-+-reb-+-ast'
    #     action_network_pra = requests.get(action_network_pra_url, headers={'User-Agent':"Mozilla/5.0"})
    #     pra = BeautifulSoup(action_network_pra.text, 'html.parser')


    #uncomment following for draftkings

    # game_points = points.select('tbody')

    # for match in game_points:
    #     points_rows = match.select('tr')
        
    #     for row in points_rows:
    #         name = row.select('.sportsbook-row-name')[0].text
    #         if name.endswith(" "):
    #             name = name.rstrip(name[-1])
    #         if name.startswith(" "):
    #             name = name[1:]
    #         if name in odds_dict:
    #             line = float(row.select('.sportsbook-outcome-cell__line')[0].text)[1:]
    #             odds_dict[name]["points"] = line
    #         else:
    #             odds_dict[name] = {}
    #             odds_dict[name]["points"] = line

    # ipdb.set_trace()

    # game_assists = assists.select('tbody')

    # for match in game_assists:
    #     assists_rows = match.select('tr')
        
    #     for row in assists_rows:
    #         name = row.select('.sportsbook-row-name')[0].text
    #         if name.endswith(" "):
    #             name = name.rstrip(name[-1])
    #         if name.startswith(" "):
    #             name = name[1:]
    #         if name in odds_dict:
    #             line = float(row.select('.sportsbook-outcome-cell__line')[0].text)
    #             odds_dict[name]["assists"] = line
    #         else:
    #             odds_dict[name] = {}
    #             odds_dict[name]["assists"] = line

    # game_rebounds = rebounds.select('tbody')

    # for match in game_rebounds:
    #     rebounds_rows = match.select('tr')
        
    #     for row in rebounds_rows:
    #         name = row.select('.sportsbook-row-name')[0].text
    #         if name.endswith(" "):
    #             name = name.rstrip(name[-1])
    #         if name.startswith(" "):
    #             name = name[1:]
    #         if name in odds_dict:
    #             line = float(row.select('.sportsbook-outcome-cell__line')[0].text)
    #             odds_dict[name]["rebounds"] = line
    #         else:
    #             odds_dict[name] = {}
    #             odds_dict[name]["rebounds"] = line

    # if pra_switch:
    #     game_pra = pra.select('tbody')

    #     for match in game_pra:
    #         pra_rows = match.select('tr')
            
    #         for row in pra_rows:
    #             name = row.select('.sportsbook-row-name')[0].text
    #             if name.endswith(" "):
    #                 name = name.rstrip(name[-1])
    #             if name.startswith(" "):
    #                 name = name[1:]
    #             if name in odds_dict:
    #                 line = float(row.select('.sportsbook-outcome-cell__line')[0].text)
    #                 odds_dict[name]["pra"] = line
    #             else:
    #                 odds_dict[name] = {}
    #                 odds_dict[name]["pra"] = line

    # game_pr = pr.select('tbody')

    # for match in game_pr:
    #     pr_rows = match.select('tr')
        
    #     for row in pr_rows:
    #         name = row.select('.sportsbook-row-name')[0].text
    #         if name.endswith(" "):
    #             name = name.rstrip(name[-1])
    #         if name.startswith(" "):
    #             name = name[1:]
    #         if name in odds_dict:
    #             line = float(row.select('.sportsbook-outcome-cell__line')[0].text)
    #             odds_dict[name]["pr"] = line
    #         else:
    #             odds_dict[name] = {}
    #             odds_dict[name]["pr"] = line


    # game_ra = ra.select('tbody')

    # for match in game_ra:
    #     ra_rows = match.select('tr')
        
    #     for row in ra_rows:
    #         name = row.select('.sportsbook-row-name')[0].text
    #         if name.endswith(" "):
    #             name = name.rstrip(name[-1])
    #         if name.startswith(" "):
    #             name = name[1:]
    #         if name in odds_dict:
    #             line = float(row.select('.sportsbook-outcome-cell__line')[0].text)
    #             odds_dict[name]["ra"] = line
    #         else:
    #             odds_dict[name] = {}
    #             odds_dict[name]["ra"] = line

    # game_pa = pa.select('tbody')

    # for match in game_pra:
    #     pa_rows = match.select('tr')
        
    #     for row in pa_rows:
    #         name = row.select('.sportsbook-row-name')[0].text
    #         if name.endswith(" "):
    #             name = name.rstrip(name[-1])
    #         if name.startswith(" "):
    #             name = name[1:]
    #         if name in odds_dict:
    #             line = float(row.select('.sportsbook-outcome-cell__line')[0].text)
    #             odds_dict[name]["pa"] = line
    #         else:
    #             odds_dict[name] = {}
    #             odds_dict[name]["pa"] = line

    new_odds_dict = odds_dict.copy()

    for item in odds_dict:
        if odds_dict[item] == {}:
            del(new_odds_dict[item])


    new_odds_dict = sorted(new_odds_dict.items(),key=lambda kv: kv)
    # new_odds_dict = dict(sorted(new_odds_dict.items()))

    #new_odds_dict is a dicitonary of all today's props

    bets = []
    double_doubles = []
    triple_doubles = []

    for player_and_odds in new_odds_dict:

        player_name = player_and_odds[0]

        
        
        #collect my own data about every game they've played in
        
        current_player = Player.query.filter(Player.name==player_name).first()

        latest_minutes_list = [game.minutes for game in current_player.games[-10:]]
        latest_minutes = mean(latest_minutes_list)

        if current_player:    
            games_to_use = current_player.games
            

            last_game = games_to_use[-1]

            if last_game.home:
                player_team = last_game.game.home
            else:
                player_team = last_game.game.visitor

            # if player_team=="Milwaukee Bucks" or player_team=="Portland Trail Blazers":
            #     continue


            if player_team in list_of_teams and ([game["time"] for game in todays_games if game["home"]==player_team or game["away"]==player_team][0] > format_time):

                print(f"{player_name} ({player_team})")

                #find list of starters

                starters_games = [game.game.players for game in games_to_use[-3:]]
                starter_list = (list(itertools.chain.from_iterable(starters_games)))
                team_starter_list = [game for game in starter_list if game.team==player_team]
                

                starter_names = [game.player.name for game in team_starter_list]
                starter_name_set = set(starter_names)
                uniq_starter_names = list(starter_name_set)
                different_players_list = [{game.player.name:game.minutes} for game in team_starter_list]

                starter_minutes = {}

                for player in uniq_starter_names:
                    minutes_array = []
                    for value in different_players_list:
                        for team_player,team_player_minutes in value.items():
                            if player==team_player:
                                minutes_array.append(team_player_minutes)
                    starter_minutes[player]=(mean(minutes_array))

                sorted_starter_minutes = sorted(starter_minutes.items(),key=lambda kv: (kv[1],kv[0]))
                sorted_starter_minutes.reverse()

                starters = []
                games=[]
                i=0

                while i<5:
                    starters.append(sorted_starter_minutes[i][0])
                    i+=1

                for game in games_to_use:
                    game_players = game.game.players
                    home_players = [game for game in game_players if game.team==player_team]
                    home_player_names = [player.player.name for player in home_players]

                    starters_in_lineups = []

                    for player in starters:
                        if player in home_player_names:
                            starters_in_lineups.append(player)


                    if ((len(starters_in_lineups)>3) and (latest_minutes*.65 <= game.minutes <= latest_minutes*1.45)):
                        games.append(game)

            

                if any(player_team in game.values() for game in todays_games):

                    game = [game for game in todays_games if game["home"]==player_team or game["away"]==player_team][0]

                    if game["home"] == player_team:
                        player_home_or_away = True
                        other_team = game["away"]
                    else:
                        player_home_or_away = False
                        other_team = game["home"]

                    game_time = game["time"]
                    

                    injury = False
                    opponent_injury = False
                    games_with_injury = []
                    games_with_opp_injury = []

                    

                

                   



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
                                if len(Player.query.filter(Player.name==injured_player).all())>0:
                                    injured_player_games = Player.query.filter(Player.name==injured_player).first().games[-3:]
                                    minutes = mean([game.minutes for game in injured_player_games])

                                    if minutes > 2000:
                                        if injured_player in team_player_names and this_current_player in games_with_injury:
                                            games_with_injury.remove(this_current_player)
                        games_to_add = []
                        for game in games_with_injury:
                            games_to_add.append(game)
                            games_to_add.append(game)
                        games_with_injury.extend(games_to_add)

                        if len(games_with_injury)>6:
                            games = games_with_injury

                    #we got the injuries. Time to check the roster
                        



                
                    #latest 5 games at time
                    games_at_time = [game for game in games if game.game.date.time()==game_time][-3:]

                    #last 3 games on specific day
                    current_day = current_date.weekday()
                    games_on_day = []
                    for game in games:
                        if game.game.date.weekday()==current_day:
                            games_on_day.append(game)

                    games_on_day = games_on_day[-3:]

                    #last 4 games with specified rest period
                    rest_days = []
                    last_game = games_to_use[-1]
                    day_of_last_game =last_game.game.date.weekday()
                    last_game_day_of_month = last_game.game.date.day
                    current_day_of_month = current_date.day
                    weekdays_between = current_day - day_of_last_game
                    if weekdays_between <0: 
                        weekdays_between +=7
                    days_between = current_day_of_month - last_game_day_of_month
                    if  -7 <= days_between <= 7:
                    
                        for index, game in enumerate(games_to_use):
                            if index>0:
                                prev_game = games_to_use[index-1]
                                prev_game_day_of_month = prev_game.game.date.day
                                prev_game_day_of_week = prev_game.game.date.weekday()
                                date_difference = game.game.date.day - prev_game_day_of_month
                                if date_difference < 0:
                                    date_difference += 7
                                day_difference = game.game.date.weekday() - prev_game_day_of_week
                                if day_difference == days_between or date_difference==weekdays_between:
                                    rest_days.append(game)
                                    rest_days.append(game)

                    rest_days = rest_days[-4:]

                    


                    #last 5 games
                    latest_games = [game for game in games][-3:]
                    #last 8 home/away games
                    latest_home_or_away_games = [game for game in games if game.home==player_home_or_away][-3:]

                    
                    #get latest matchups vs team
                    #check recent minutes
                    minutes_list = [game.minutes for game in latest_games]
                    minutes = mean(minutes_list)
                    
                    games_vs_opponent = [game for game in games if (game.game.home==other_team or game.game.visitor==other_team)][-3:]
                    games_to_add_opp = []
                    for game in games_vs_opponent:
                        games_to_add_opp.append(game)
                    games_vs_opponent.extend(games_to_add_opp)

                            
                
                    

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
                                    if len(Player.query.filter(Player.name==injured_player).all())>0:
                                        injured_player_games = Player.query.filter(Player.name==injured_player).first().games[-5:]
                                        minutes = mean([game.minutes for game in injured_player_games])
                                        if minutes > 2000:
                                            if injured_player in opponent_player_names and this_current_player in games_with_opp_injury:
                                                games_with_opp_injury.remove(this_current_player)
                

                    #opponent stat allowed to position

                    opponent_games = Game.query.filter(or_(Game.visitor==other_team,Game.home==other_team))[-12:]
                    team_games = Game.query.filter(or_(Game.visitor==player_team,Game.home==player_team))[-12:]
                    team_games_players = [game.players for game in team_games]
                    team_players = (list(itertools.chain.from_iterable(team_games_players)))
                    position_player_games = [game for game in team_players if (game.team==player_team and game.player.position==current_player.position)]
                    position_player_names = [game.player.name for game in position_player_games]
                    new_position_player_names = set(position_player_names)
                    uniq_position_player_names = list(new_position_player_names)
                    different_players = [{game.player.name:game.minutes} for game in position_player_games]

                    position_player_minutes = {}

                    for player in uniq_position_player_names:
                        minutes_array = []
                        for value in different_players:
                            for team_player,team_player_minutes in value.items():
                                if player==team_player:
                                    minutes_array.append(team_player_minutes)
                        position_player_minutes[player]=(mean(minutes_array))

                

                    sorted_position_minutes = sorted(position_player_minutes.items(),key=lambda kv: (kv[1],kv[0]))
                    sorted_position_minutes.reverse()

                    current_player_depth = 0

                    for index,value in enumerate(sorted_position_minutes):
                        if value[0]==player_name:
                            current_player_depth=index+1
                            break


                    
                    
                            
                    #check every team for the position and depth except for other_team
                        #loop through all their games against the other team to check for average stats
                        #loop through all their games against everyone but other_team
                        #compare the averages
                        #average the averages and get a multiplier that you will use at the end


                    team_list = ["Atlanta Hawks",
                    "Boston Celtics",
                    "Charlotte Hornets",
                    "Chicago Bulls",
                    "Cleveland Cavaliers",
                    "Dallas Mavericks",
                    "Denver Nuggets",
                    "Detroit Pistons",
                    "Golden State Warriors",
                    "Houston Rockets",
                    "Indiana Pacers",
                    "Los Angeles Clippers",
                    "Los Angeles Lakers",
                    "Memphis Grizzlies",
                    "Miami Heat",
                    "Milwaukee Bucks",
                    "Minnesota Timberwolves",
                    "New Orleans Pelicans",
                    "New York Knicks",
                    "Brooklyn Nets",
                    "Oklahoma City Thunder",
                    "Orlando Magic",
                    "Philadelphia 76ers",
                    "Phoenix Suns",
                    "Portland Trail Blazers",
                    "Sacramento Kings",
                    "Toronto Raptors",
                    "Utah Jazz",
                    "Washington Wizards",
                    "San Antonio Spurs"]

                    

                    team_list.remove(player_team)
                    team_list.remove(other_team)

                    points_modifier_array=[]
                    assists_modifier_array=[]
                    trb_modifier_array=[]

                

                    for team in team_list:

                        team_games = Game.query.filter(or_(Game.visitor==team,Game.home==team))[-12:]
                        team_games_players = [game.players for game in team_games]
                        team_players = (list(itertools.chain.from_iterable(team_games_players)))
                        position_player_games = [game for game in team_players if (game.team==team and game.player.position==current_player.position)]
                        position_player_names = [game.player.name for game in position_player_games]
                        new_position_player_names = set(position_player_names)
                        uniq_position_player_names = list(new_position_player_names)
                        different_players = [{game.player.name:game.minutes} for game in position_player_games]

                        position_player_minutes = {}

                        for player in uniq_position_player_names:
                            minutes_array = []
                            for value in different_players:
                                for team_player,team_player_minutes in value.items():
                                    if player==team_player:
                                        minutes_array.append(team_player_minutes)
                            position_player_minutes[player]=(mean(minutes_array))

                    

                        sorted_position_minutes = sorted(position_player_minutes.items(),key=lambda kv: (kv[1],kv[0]))
                        sorted_position_minutes.reverse()


                        if (len(sorted_position_minutes)>0 and len(sorted_position_minutes)>=current_player_depth):
                            same_position_player = sorted_position_minutes[current_player_depth-1][0]


                            player_object = Player.query.filter(Player.name==same_position_player).first()

                            if len([game for game in player_object.games if (game.game.home==other_team or game.game.visitor==other_team)])>0:

                                team_player_games_against_opp = [game for game in player_object.games if (game.game.home==other_team or game.game.visitor==other_team)][-4:]
                                team_player_games_the_rest = [game for game in player_object.games if (game.game.home!=other_team and game.game.visitor!=other_team)][-20:]

                                opponent_assists_mean = mean([game.assists for game in team_player_games_against_opp])
                                rest_assists_mean = mean([game.assists for game in team_player_games_the_rest]) if len(team_player_games_the_rest)>0 else 1

                                opponent_points_mean = mean([game.points for game in team_player_games_against_opp])
                                rest_points_mean = mean([game.points for game in team_player_games_the_rest]) if len(team_player_games_the_rest)>0 else 1

                                opponent_trb_mean = mean([game.trb for game in team_player_games_against_opp])
                                rest_trb_mean = mean([game.trb for game in team_player_games_the_rest]) if len(team_player_games_the_rest)>0 else 1

                                player_assists_modifier = opponent_assists_mean/rest_assists_mean if rest_assists_mean > 0 else 1
                                player_points_modifier = opponent_points_mean/rest_points_mean if rest_points_mean > 0 else 1
                                player_trb_modifier = opponent_trb_mean/rest_trb_mean if rest_trb_mean > 0 else 1

                                points_modifier_array.append(player_points_modifier)
                                assists_modifier_array.append(player_assists_modifier)
                                trb_modifier_array.append(player_trb_modifier)

                    
                    assists_modifier = mean(assists_modifier_array)
                    trb_modifier = mean(trb_modifier_array)
                    points_modifier = mean(points_modifier_array)





                    #make a big array of games
                    latest_home_or_away_games.extend(latest_games)
                    latest_home_or_away_games.extend(games_at_time)
                    latest_home_or_away_games.extend(games_vs_opponent)
                    if injury:
                        latest_home_or_away_games.extend(games_with_injury[-3:])
                    if opponent_injury:
                        latest_home_or_away_games.extend(games_with_opp_injury[-3:])
                    latest_home_or_away_games.extend(games_on_day)
                    latest_home_or_away_games.extend(rest_days)

                    latest_home_or_away_games.reverse()

                    #find most similar game
                    most_similar = mode(latest_home_or_away_games)
                    assists_similar = most_similar.assists
                    points_similar = most_similar.points
                    trb_similar = most_similar.trb


                    # new_game_list = set(latest_home_or_away_games)

                    # uniq_game_list = list(new_game_list)

                    # uniq_game_list = [game for game in uniq_game_list]

                    uniq_game_list = latest_home_or_away_games


                   


                    if len(uniq_game_list) > 0:

                        assists_list = [game.assists for game in uniq_game_list]
                        points_list = [game.points for game in uniq_game_list]
                        trb_list = [game.trb for game in uniq_game_list]

                        assists_factor = mean(assists_list)
                        points_factor = mean(points_list)
                        trb_factor = mean(trb_list)

                        assists_predict = round((0.75*assists_factor+0.25*assists_similar)*assists_modifier,2)
                        points_predict = round((0.75*points_factor+0.25*points_similar)*points_modifier,2)
                        trb_predict = round((0.75*trb_factor+0.25*trb_similar)*trb_modifier,2)

                        assist_bet = "none"
                        trb_bet = "none"
                        points_bet = "none"
                        pra_dict = []

                        if pra_switch:

                            if "pra" in player_and_odds[1]:
                                pra_predict = assists_predict + points_predict + trb_predict
                                pra_diff = round(pra_predict - player_and_odds[1]["pra"],2)
                                if pra_diff < 0:
                                    pra_bet = "Under"
                                else:
                                    pra_bet = "Over"
                                pra_diff_abs = abs(pra_diff)
                                pra_perc = round((abs(pra_predict-player_and_odds[1]["pra"])/player_and_odds[1]["pra"]),2)
                                pra_dict = {"name": player_name, 
                                            "prop":"pra",
                                            "line": player_and_odds[1]["pra"],
                                            "projected": round(pra_predict,2),
                                            "perc": pra_perc,
                                            "diff": pra_diff_abs,
                                            "bet": pra_bet}

                                if pra_dict["perc"] > .9 or pra_dict["diff"] > 10:
                                    bets.append(pra_dict)

                            if "points" in player_and_odds[1] and "rebounds" in player_and_odds[1]:
                                pr_predict = points_predict + trb_predict
                                pr_line = player_and_odds[1]["points"]+player_and_odds[1]["rebounds"]
                                pr_diff = round((pr_predict - pr_line),2)
                                if pr_diff < 0:
                                    pr_bet = "Under"
                                else:
                                    pr_bet = "Over"
                                pr_diff_abs = abs(pr_diff)
                                pr_perc = round((abs(pr_predict-pr_line)/pr_line),2)
                                pr_dict = {"name": player_name, 
                                            "prop":"pr",
                                            "line": pr_line,
                                            "projected": round(pr_predict,2),
                                            "perc": pr_perc,
                                            "diff": pr_diff_abs,
                                            "bet": pr_bet}

                                if pra_dict not in bets:

                                    if pr_dict["perc"] > .7 or pr_dict["diff"] > 9:
                                        bets.append(pr_dict)
                            

                            if "points" in player_and_odds[1] and "assists" in player_and_odds[1]:
                                pa_predict = points_predict + assists_predict
                                pa_line = player_and_odds[1]["points"]+player_and_odds[1]["assists"]
                                pa_diff = round((pa_predict - pa_line),2)
                                if pa_diff < 0:
                                    pa_bet = "Under"
                                else:
                                    pa_bet = "Over"
                                pa_diff_abs = abs(pa_diff)
                                pa_perc = round((abs(pa_predict-pa_line)/pa_line),2)
                                pa_dict = {"name": player_name, 
                                            "prop":"pa",
                                            "line": pa_line,
                                            "projected": round(pa_predict,2),
                                            "perc": pa_perc,
                                            "diff": pa_diff_abs,
                                            "bet": pa_bet}

                                if pra_dict not in bets:

                                    if pa_dict["perc"] > .7 or pa_dict["diff"] > 9:
                                        bets.append(pa_dict)


                            if "rebounds" in player_and_odds[1] and "assists" in player_and_odds[1]:
                                ra_predict = trb_predict + assists_predict
                                ra_line = player_and_odds[1]["rebounds"]+player_and_odds[1]["assists"]
                                ra_diff = round((ra_predict - ra_line),2)
                                if ra_diff < 0:
                                    ra_bet = "Under"
                                else:
                                    ra_bet = "Over"
                                ra_diff_abs = abs(ra_diff)
                                ra_perc = round((abs(ra_predict-ra_line)/ra_line),2)
                                ra_dict = {"name": player_name, 
                                            "prop":"ra",
                                            "line": ra_line,
                                            "projected": round(ra_predict,2),
                                            "perc": ra_perc,
                                            "diff": ra_diff_abs,
                                            "bet": ra_bet}


                                if pra_dict not in bets:

                                    if ra_dict["perc"] > .7 or ra_dict["diff"] > 9:
                                        bets.append(ra_dict)



                        if "assists" in player_and_odds[1]:
                            assist_diff = round((assists_predict - player_and_odds[1]["assists"]),2)
                            if assist_diff < 0:
                                assist_bet = "Under"
                            else:
                                assist_bet = "Over"
                            assist_diff_abs = abs(assist_diff)
                            assist_perc = round((abs(assists_predict-player_and_odds[1]["assists"])/player_and_odds[1]["assists"]),2)
                            assists_dict = {"name": player_name, 
                                        "prop":"assists",
                                        "line": player_and_odds[1]["assists"],
                                        "projected": assists_predict,
                                        "perc": assist_perc,
                                        "diff": assist_diff_abs,
                                        "bet": assist_bet}

                            if pra_switch:
                                if pra_dict not in bets and pa_dict not in bets and ra_dict not in bets:

                                    if ((assists_dict["perc"] > .55 or assists_dict["diff"] > 6) and ((assists_predict > 8.4) or (player_and_odds[1]["assists"] > 8.4))):
                                        bets.append(assists_dict)

                            else:
                                if ((assists_dict["perc"] > .55 or assists_dict["diff"] > 6) and ((assists_predict > 8.4) or (player_and_odds[1]["assists"] > 8.4))):
                                        bets.append(assists_dict)

                            print(assists_dict)


                            
                        if "rebounds" in player_and_odds[1]:
                            trb_diff = round((trb_predict - player_and_odds[1]["rebounds"]),2)
                            if trb_diff < 0:
                                trb_bet = "Under"
                            else:
                                trb_bet = "Over"
                            trb_diff_abs = abs(trb_diff)
                            trb_perc = round((abs(trb_predict-player_and_odds[1]["rebounds"])/player_and_odds[1]["rebounds"]),2)
                            trb_dict = {"name": player_name, 
                                        "prop": "rebounds",
                                        "line": player_and_odds[1]["rebounds"],
                                        "projected": trb_predict,
                                        "perc": trb_perc,
                                        "diff": trb_diff_abs,
                                        "bet": trb_bet}

                            if pra_switch:
                                if pra_dict not in bets and ra_dict not in bets and pr_dict not in bets:

                                    if ((trb_dict["perc"] > .55 or trb_dict["diff"] > 6) and ((trb_predict > 8.4) or (player_and_odds[1]["rebounds"] > 8.4))):
                                        bets.append(trb_dict)

                            else:
                                if ((trb_dict["perc"] > .55 or trb_dict["diff"] > 6) and ((trb_predict > 8.4) or (player_and_odds[1]["rebounds"] > 8.4))):
                                        bets.append(trb_dict)

                            print(trb_dict)


                        if "points" in player_and_odds[1]:
                            points_diff = round((points_predict - player_and_odds[1]["points"]),2)
                            if points_diff < 0:
                                points_bet = "Under"
                            else:
                                points_bet = "Over"


                            points_diff_abs = abs(points_diff)
                            points_perc = round((abs(points_predict-player_and_odds[1]["points"])/player_and_odds[1]["points"]),2)
                        
                            points_dict = {"name": player_name, 
                                        "prop": "points",
                                        "line": player_and_odds[1]["points"],
                                        "projected": points_predict,
                                        "perc": points_perc,
                                        "diff": points_diff_abs,
                                        "bet": points_bet}

                            if pra_switch:
                                if pra_dict not in bets and pa_dict not in bets and pr_dict not in bets:

                                    if points_dict["perc"] > .5 or points_dict["diff"] > 6.5:
                                        bets.append(points_dict)

                            else:
                                if points_dict["perc"] > .5 or points_dict["diff"] > 6.5:
                                        bets.append(points_dict)

                            print(points_dict)
                            
                # if player_name=="Zach Collins":
                #     ipdb.set_trace()        

                # if player_name=="P.J. Washington":
                #     ipdb.set_trace()
                print(f"Points Multipler: {round(points_modifier,2)}")
                print(f"Assists Multipler: {round(assists_modifier,2)}")
                print(f"Trb Multipler: {round(trb_modifier,2)}\n")
                if points_predict>9.8 and assists_predict>9.8 and trb_predict>9.8:
                    triple_doubles.append(player_name)
                if ((points_predict>9.8 and assists_predict>9.8) or (assists_predict>9.8 and trb_predict>9.8) or (points_predict>9.8 and trb_predict>9.8)):
                    double_doubles.append(player_name)

    sorted_bets = sorted(bets,key=itemgetter('perc'))
    sort_by_diff = sorted(bets,key=itemgetter('diff'))
        
    for item in sorted_bets:
        name = item["name"]
        prop = item["prop"]
        line = item["line"]
        projected = item["projected"]
        bet = item["bet"]
        print(f"{name} {bet} in {prop}. Projected: {projected}, Line: {line}\n")

    print("\nBets sorted by difference\n")

    for item in sort_by_diff:
        name = item["name"]
        prop = item["prop"]
        line = item["line"]
        projected = item["projected"]
        bet = item["bet"]
        print(f"{name} {bet} in {prop}. Projected: {projected}, Line: {line}\n")

    print(f"Double Doubles: {double_doubles}")
    print(f"Triple Doubles: {triple_doubles}\n")

    print("Injuries:")
    

    for team,injuries in injured_list.items():
        if team in list_of_teams:
            print(f"{team}: {injuries}")

    print("B")
            

