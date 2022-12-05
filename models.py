"""
这个文件包括所有的模型Models。
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

# 多对多关系需要定义一个用于关系的辅助表。
# 对于这个辅助表，强烈建议 不 使用模型，而是采用一个实际的表:
Show = db.Table('Show', db.Model.metadata,
    db.Column('Venue_id', db.Integer, db.ForeignKey('Venue.id')),
    db.Column('Artist_id', db.Integer, db.ForeignKey('Artist.id')),
    db.Column('start_time', db.DateTime))

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    genres = db.Column(db.ARRAY(db.String())) # 为了存储多个genres，我决定创建一个以字符串作为数据类型的数组列
    seeking_description = db.Column(db.Text) # descriptions有些长,可以使用文本类型
    venues = db.relationship('Artist', secondary=Show, backref=db.backref('shows', lazy='joined'))
    def __repr__(self):
        return 'Venue Id:{} | Name: {}'.format(self.id, self.name)
    

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
    genres = db.Column(db.ARRAY(db.String())) # 为了存储多个genres，我决定创建一个以字符串作为数据类型的数组列
    seeking_description = db.Column(db.Text) # descriptions有些长,可以使用文本类型
    
    def __repr__(self):
        return 'Artist Id:{} | Name: {}'.format(self.id, self.name)  




