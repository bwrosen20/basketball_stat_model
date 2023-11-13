from app import *
from statistics import mean,mode
from bs4 import BeautifulSoup
from datetime import datetime, date
from operator import itemgetter
import time
import requests
import ipdb

with app.app_context():

    # point_guard_url = "https://www.espn.com/nba/players/_/position/pg"
    # point_guard_page = requests.get(point_guard_url, headers = {'User-Agent':"Mozilla/5.0"})
    # point_guards = BeautifulSoup(point_guard_page.text, 'html.parser')

    # rows = point_guards.select('table')[0].select('.oddrow')
    # rows.extend(point_guards.select('table')[0].select('.evenrow'))

    # for row in rows:
    #     name = row.select('a')[0].text.replace(',','').split(' ')
    #     first_name = name.pop(-1)
    #     name.insert(0,first_name)
    #     name = (' ').join(name)

    #     if len(Player.query.filter(Player.name==name).all())>0:
    #         player = Player.query.filter(Player.name==name).first()
    #         player.position = 1
    #         db.session.add(player)
    #         db.session.commit()
    #         print(player.name)
    #         # ipdb.set_trace()



    shoot_guard_url = "https://www.espn.com/nba/players/_/position/sg"
    shoot_guard_page = requests.get(shoot_guard_url, headers = {'User-Agent':"Mozilla/5.0"})
    shoot_guards = BeautifulSoup(shoot_guard_page.text, 'html.parser')

    rows = shoot_guards.select('table')[0].select('.oddrow')
    rows.extend(shoot_guards.select('table')[0].select('.evenrow'))

    for row in rows:
        name = row.select('a')[0].text.replace(',','').split(' ')
        first_name = name.pop(-1)
        name.insert(0,first_name)
        name = (' ').join(name)

        if len(Player.query.filter(Player.name==name).all())>0:
            player = Player.query.filter(Player.name==name).first()
            player.position = 2
            db.session.add(player)
            db.session.commit()
            print(player.name)
            # ipdb.set_trace()

    small_forward_url = "https://www.espn.com/nba/players/_/position/sf"
    small_forward_page = requests.get(small_forward_url, headers = {'User-Agent':"Mozilla/5.0"})
    small_forwards = BeautifulSoup(small_forward_page.text, 'html.parser')

    rows = small_forwards.select('table')[0].select('.oddrow')
    rows.extend(small_forwards.select('table')[0].select('.evenrow'))

    for row in rows:
        name = row.select('a')[0].text.replace(',','').split(' ')
        first_name = name.pop(-1)
        name.insert(0,first_name)
        name = (' ').join(name)

        if len(Player.query.filter(Player.name==name).all())>0:
            player = Player.query.filter(Player.name==name).first()
            player.position = 3
            db.session.add(player)
            db.session.commit()
            print(player.name)
            # ipdb.set_trace()


    power_forward_url = "https://www.espn.com/nba/players/_/position/pf"
    power_forward_page = requests.get(power_forward_url, headers = {'User-Agent':"Mozilla/5.0"})
    power_forwards = BeautifulSoup(power_forward_page.text, 'html.parser')

    rows = power_forwards.select('table')[0].select('.oddrow')
    rows.extend(power_forwards.select('table')[0].select('.evenrow'))

    for row in rows:
        name = row.select('a')[0].text.replace(',','').split(' ')
        first_name = name.pop(-1)
        name.insert(0,first_name)
        name = (' ').join(name)

        if len(Player.query.filter(Player.name==name).all())>0:
            player = Player.query.filter(Player.name==name).first()
            player.position = 4
            db.session.add(player)
            db.session.commit()
            print(player.name)
            # ipdb.set_trace()


    center_url = "https://www.espn.com/nba/players/_/position/c"
    center_page = requests.get(center_url, headers = {'User-Agent':"Mozilla/5.0"})
    centers = BeautifulSoup(center_page.text, 'html.parser')

    rows = centers.select('table')[0].select('.oddrow')
    rows.extend(centers.select('table')[0].select('.evenrow'))

    for row in rows:
        name = row.select('a')[0].text.replace(',','').split(' ')
        first_name = name.pop(-1)
        name.insert(0,first_name)
        name = (' ').join(name)

        if len(Player.query.filter(Player.name==name).all())>0:
            player = Player.query.filter(Player.name==name).first()
            player.position = 5
            db.session.add(player)
            db.session.commit()
            print(player.name)
            # ipdb.set_trace()