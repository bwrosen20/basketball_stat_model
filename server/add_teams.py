from app import *
from statistics import mean,mode
from bs4 import BeautifulSoup
from datetime import datetime, date
from operator import itemgetter
import time
import requests
import ipdb

with app.app_context():

    games = PlayerGame.query.all()

    for game in games:
        if game.home:
            game.team = game.game.home
        else:
            game.team = game.game.visitor

        # ipdb.set_trace()
        print(game)
        db.session.add(game)
        db.session.commit()
    print("Done")
