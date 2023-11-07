from app import *
from statistics import mean,mode
from bs4 import BeautifulSoup
from unidecode import unidecode
import datetime
import requests
import ipdb

with app.app_context():


    players = Player.query.all()
    for player in players:
        real_name = unidecode(player.name)
        player.name=real_name
        db.session.commit()
    print('Done')
