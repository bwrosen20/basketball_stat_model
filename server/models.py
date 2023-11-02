from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy_serializer import SerializerMixin
# from sqlalchemy.ext.associationproxy import association_proxy

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)


class Game(db.Model, SerializerMixin):
    # __tablename__ = 'games'

    # serialize_rules = ('-players.game',)

    id = db.Column(db.Integer, primary_key=True)
    visitor = db.Column(db.String)
    home = db.Column(db.String)
    location = db.Column(db.String)
    home_score = db.Column(db.Integer)
    away_score = db.Column(db.Integer)
    date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    players = db.relationship('PlayerGame', back_populates="game")
    # teams = db.relationship('Team', backref=backref('game'))

    def __repr__(self):
        return f'<{self.visitor} at {self.home} {self.date}>'

class Player(db.Model, SerializerMixin):
    # __tablename__ = 'players'

    # serialize_rules = ('-game.players', '-team.players',)
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    games = db.relationship('PlayerGame', back_populates='player')

    

    def __repr__(self):
        return f'<{self.name}>'


class PlayerGame(db.Model, SerializerMixin):
    # __tablename__ = 'player_games'

    id = db.Column(db.Integer, primary_key=True)
    team = db.Column(db.String)
    # minutes = db.Column(db.Float)
    # fg = db.Column(db.Integer)
    # fga = db.Column(db.Integer)
    # fg_pct = db.Column(db.Float)
    three_pt = db.Column(db.Integer)
    # three_pt_perc = db.Column(db.Float)
    # ft = db.Column(db.Integer)
    # fta = db.Column(db.Integer)
    # ft_perc = db.Column(db.Float)
    # orb = db.Column(db.Integer)
    # drb = db.Column(db.Integer)
    trb = db.Column(db.Integer)
    assists = db.Column(db.Integer)
    steals = db.Column(db.Integer)
    blocks = db.Column(db.Integer)
    # to = db.Column(db.Integer)
    # fouls = db.Column(db.Integer)
    points = db.Column(db.Integer)
    # plus_minus = db.Column(db.Integer)
    # tsp = db.Column(db.Float)
    # eft = db.Colunn(db.Float)
    # tPAr = db.Colunn(db.Float)
    # FTr = db.Colunn(db.Float)
    # ORBP = db.Colunn(db.Float)
    # DRBP = db.Colunn(db.Float)
    # TRBP = db.Colunn(db.Float)
    # ASTP = db.Colunn(db.Float)
    # STLP = db.Colunn(db.Float)
    # BLKP = db.Colunn(db.Float)
    # TOVP = db.Colunn(db.Float)
    # USGP = db.Colunn(db.Float)
    # ORtg = db.Colunn(db.Integer)
    # DRTg = db.Colunn(db.Integer)
    # BPM = db.Colunn(db.Float)
    home = db.Column(db.Boolean)

    player_id = db.Column('player_id',db.Integer, db.ForeignKey('player.id'))
    game_id = db.Column('game_id',db.Integer, db.ForeignKey('game.id'))

    player = db.relationship('Player', back_populates='games')
    game = db.relationship('Game', back_populates='players')


    def __repr__(self):
        return f"<{self.player.name} on {self.game.date}>"

# class Team(db.Model, SerializerMixin):
#     __tablename__ = 'teams'

#     serialize_rules = ('-.user',)

#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String)
    
#     created_at = db.Column(db.DateTime, server_default=db.func.now())
#     updated_at = db.Column(db.DateTime, onupdate=db.func.now())

#     players = db.relationship('Players', backref='team')
#     games = db.relationship('Games', backref='team')
