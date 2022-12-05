''' 
这个文件主要是Controlers,以及app的实现
'''
import json
import dateutil.parser
from datetime import datetime
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for,jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func,inspect
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import db,Venue, Show, Artist
from flask_migrate import Migrate


#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
app.config.from_object('config')
moment = Moment(app)
db.init_app(app)

# TODO: connect to a local postgresql database
migrate = Migrate(app, db)
# ctx = app.app_context()
# ctx.push()  # 这两句话解决没有content push 导致的报错
# db.create_all()  

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  '''转换到使用者的当地时间

  * Input: 
      - <string> value
      - <string> format
  * Output: 
      - <datetime> 当地时区的datetime

  Source: http://babel.pocoo.org/en/latest/api/dates.html

  Only used for flask filter register.
  '''
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
      # format="yyyy.MM.dd G 'at' HH:mm:ss zzz"
  return babel.dates.format_datetime(date, format, locale='zh')

app.jinja_env.filters['datetime'] = format_datetime

# -----------------------------------------------------------------
#  一些功能函数
# -----------------------------------------------------------------
def get_dict_list_from_result(result):
  '''Converts SQLALchemy Collections Results to Dict

  * Input: sqlalchemy.util._collections.result
  * Output: list

  资源: https://stackoverflow.com/questions/48232222/how-to-deal-with-sqlalchemy-util-collections-result

  在下面的视图中使用到了这个函数:
    - /venues
  
  * 实例演示：
    p = Point(x=11, y=22)
    p._asdict()
    >>> {'x': 11, 'y': 22}
  '''
  list_dict = []
  for i in result:
      i_dict = i._asdict()  
      list_dict.append(i_dict)
  return list_dict

def object_as_dict(obj):
  '''将SQLALchemy Query结果转换为Dict

  *Input: ORM Object
  *Output: Single Object as Dict

  Makes use of the SQLAlchemy inspection system (https://docs.sqlalchemy.org/en/13/core/inspection.html)

  下面的视图中使用到了这个函数:
    - /venues
  '''
  return {c.key: getattr(obj, c.key)
        for c in inspect(obj).mapper.column_attrs}


#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():  
  '''Homepage of the app.
  
  * Input: None

  包括的元素:
    - 创建新的 Artist、Venues 、Shows
    - 搜索Artist and Venues
    - 列表展示最新的Artists和Shows

  响应的HTML:
    - templates/pages/home.html
  '''
  recent_artists = Artist.query.order_by(Artist.id.desc()).limit(10).all()
  recent_venues = Venue.query.order_by(Venue.id.desc()).limit(10).all()
  return render_template('pages/home.html', 
  recent_artists = recent_artists, 
  recent_venues = recent_venues)

  
#  ----------------------------------------------------------------
#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  '''
  展示所有的venues
      * Input: None
      页面内容：
      - 查看列出的所有场地
      - 按城市和州分组
      - 查看即将上映的节目数量
      - 点击场地链接到“/venues/<int:venue_id>”下的详细信息页面
    
    响应的HTML:
      - templates/pages/venues.html
    ''' 
  #  演示样例
  #  data=[{
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "venues": [{
  #     "id": 1,
  #     "name": "The Musical Hop",
  #     "num_upcoming_shows": 0,
  #   }, {
  #     "id": 3,
  #     "name": "Park Square Live Music & Coffee",
  #     "num_upcoming_shows": 1,
  #   }]
  # }, {
  #   "city": "New York",
  #   "state": "NY",
  #   "venues": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }]
  
  # 第 1 步:获取包含城市和州名称的字典列表
  groupby_venues_result = (db.session.query(Venue.city,Venue.state).group_by(Venue.city,Venue.state))
  data=get_dict_list_from_result(groupby_venues_result)
 # 第 2 步：遍历区域并附加场地数据 
  for area in data:
    # 向字典中添加一个名为 “venues”的新键
    # 它的值为同一城市的场地列表
    area['venues'] = [object_as_dict(ven) for ven in Venue.query.filter_by(city = area['city']).all()]
    # Step 3: 添加 num_shows
    for ven in area['venues']:
      # 向venues的值的字典中添加一个名为 “num_shows”的新键
      # 这个键记录场地即将举行的演出数量。
      ven['num_shows'] = db.session.query(func.count(Show.c.Venue_id)).filter(Show.c.Venue_id == ven['id']).filter(Show.c.start_time > datetime.now()).all()[0][0]

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  '''
  - 使用搜索词搜索场地并获取结果列表
  - 查看有多少数据库条目与搜索词匹配
  - 点击结果链接到“/venues/<int:venue_id>”下的详细信息页面
  '''
  # results示例：
  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }
  search_term=request.form.get('search_term', '')  # 从resquest中获取搜索词

  search_venues_count = db.session.query(func.count(Venue.id)).filter(Venue.name.contains(search_term)).all()
  # TODO 这里有问题 似乎搜索不出来
  search_venues_result = Venue.query.filter(Venue.name.contains(search_term)).all()
  response={
    "count": search_venues_count[0][0],
    "data": search_venues_result
  }

  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  '''venues详情页
  
  * Input: <int> venue_id

    - Venue的各种信息
    - upcoming和过期的show的列表
  
  响应的HTML:
    - templates/pages/show_venues.html

  '''
  # 传入数据示例
  # data1={
  #   "id": 1,
  #   "name": "The Musical Hop",
  #   "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
  #   "address": "1015 Folsom Street",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "123-123-1234",
  #   "website_link": "https://www.themusicalhop.com",
  #   "facebook_link": "https://www.facebook.com/TheMusicalHop",
  #   "seeking_talent": True,
  #   "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
  #   "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #   "past_shows": [{
  #     "artist_id": 4,
  #     "artist_name": "Guns N Petals",
  #     "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #     "start_time": "2019-05-21T21:30:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data2={
  #   "id": 2,
  #   "name": "The Dueling Pianos Bar",
  #   "genres": ["Classical", "R&B", "Hip-Hop"],
  #   "address": "335 Delancey Street",
  #   "city": "New York",
  #   "state": "NY",
  #   "phone": "914-003-1132",
  #   "website_link": "https://www.theduelingpianos.com",
  #   "facebook_link": "https://www.facebook.com/theduelingpianos",
  #   "seeking_talent": False,
  #   "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
  #   "past_shows": [],
  #   "upcoming_shows": [],
  #   "past_shows_count": 0,
  #   "upcoming_shows_count": 0,
  # }
  # data3={
  #   "id": 3,
  #   "name": "Park Square Live Music & Coffee",
  #   "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
  #   "address": "34 Whiskey Moore Ave",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "415-000-1234",
  #   "website_link": "https://www.parksquarelivemusicandcoffee.com",
  #   "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
  #   "seeking_talent": False,
  #   "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #   "past_shows": [{
  #     "artist_id": 5,
  #     "artist_name": "Matt Quevedo",
  #     "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #     "start_time": "2019-06-15T23:00:00.000Z"
  #   }],
  #   "upcoming_shows": [{
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-01T20:00:00.000Z"
  #   }, {
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-08T20:00:00.000Z"
  #   }, {
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-15T20:00:00.000Z"
  #   }],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 3,
  # }
  # 找到对应id的venue
  data = Venue.query.get(venue_id)

  # Past Shows
  data.past_shows = (db.session.query(
    Artist.id.label("artist_id"), 
    Artist.name.label("artist_name"), 
    Artist.image_link.label("artist_image_link"), 
    Show)
    .filter(Show.c.Venue_id == venue_id)
    .filter(Show.c.Artist_id == Artist.id)
    .filter(Show.c.start_time <= datetime.now())
    .all())
  
  # Upcomming Shows
  data.upcoming_shows = (db.session.query(
    Artist.id.label("artist_id"), 
    Artist.name.label("artist_name"), 
    Artist.image_link.label("artist_image_link"), 
    Show)
    .filter(Show.c.Venue_id == venue_id)
    .filter(Show.c.Artist_id == Artist.id)
    .filter(Show.c.start_time > datetime.now())
    .all())

  #  past Shows 的数量
  data.past_shows_count = (db.session.query(
    func.count(Show.c.Venue_id))
    .filter(Show.c.Venue_id == venue_id)
    .filter(Show.c.start_time < datetime.now())
    .all())[0][0]

  # Upcoming Shows的数量
  data.upcoming_shows_count = (db.session.query(
    func.count(Show.c.Venue_id))
    .filter(Show.c.Venue_id == venue_id)
    .filter(Show.c.start_time > datetime.now())
    .all())[0][0]

  # data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  return render_template('pages/show_venue.html', venue=data)

  
#  ----------------------------------------------------------------
#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  '''
  get方法下: 渲染空白的表单
  '''
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = VenueForm(request.form)  # 初始化一个表单
  flashType = 'danger' 
  if form.validate():
    try:
      newVenue = Venue(
        name = request.form['name'],
        city = request.form['city'],
        state = request.form['state'],
        address = request.form['address'],
        phone = request.form['phone'],
        genres = request.form.getlist('genres'),
        facebook_link = request.form['facebook_link'],
        website_link = request.form['website_link'],
        image_link = request.form['website_link'],
        seeking_talent = request.form['seeking_talent'],
        seeking_description = request.form['seeking_description'],
      )
      db.session.add(newVenue)
      db.session.commit()
      flashType = 'success'
  # 数据库成功插入, flash success
      flash('音乐场馆' + request.form['name'] + '被成功创建!')
    except:
  # TODO: 数据库插入失败, flash an error instead.
      flash('数据库插入过程中发生错误，' + request.form['name'] + '创建失败!')
  # falsh参考链接: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    finally:
      db.session.close()
  else:
    flash(form.errors)
    flash('表单有错误，'+ request.form['name'] + '创建失败!')
  return render_template('pages/home.html', flashType = flashType)

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  '''删除现存的Venue
  Input: <int> venue_id
    - 当点击 "/venues/<int:venue_id>"路由页面的红色删除按钮时 删除对应venue
    - Ajax获取路由,Javascript对应代码在templates/layouts/main.html
    - 显示成功或失败
  响应HTML: (这里由main.html中的js代码完成页面跳转操作)
      - templates/pages/show_venue.html
  '''
  try:
    delete_venue = Venue.query.filter_by(id = venue_id)
    db.session.delete(delete_venue)
    db.session.commit()
  except:
    db.session.rollback()
    return jsonify({'success':False})
  finally:
    db.session.close()
  return jsonify({'success':True})

# ----------------------------------------------------------------
#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = Artist.query.all()
  # 示例数据
  # data=[{
  #   "id": 4,
  #   "name": "Guns N Petals",
  # }, {
  #   "id": 5,
  #   "name": "Matt Quevedo",
  # }, {
  #   "id": 6,
  #   "name": "The Wild Sax Band",
  # }]
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():

  # 示例数据
  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 4,
  #     "name": "Guns N Petals",
  #     "num_upcoming_shows": 0,
  #   }]
  # }
  search_term=request.form.get('search_term', '')
  search_artist_count = db.session.query(func.count(Artist.id)).filter(Artist.name.contains(search_term)).all()
  search_artist_result = Artist.query.filter(Artist.name.contains(search_term)).all()

  response = {
    "count":search_artist_count[0][0],
    "data": search_artist_result,
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  single_artist = Artist.query.get(artist_id)

  # 获取Past Shows
  single_artist.past_shows = (db.session.query(
    Venue.id.label("venue_id"), 
    Venue.name.label("venue_name"), 
    Venue.image_link.label("venue_image_link"), 
    Show)
    .filter(Show.c.Artist_id == artist_id)
    .filter(Show.c.Venue_id == Venue.id)
    .filter(Show.c.start_time <= datetime.now())
    .all())
  
  # 获取Upcomming Shows
  single_artist.upcoming_shows = (db.session.query(
    Venue.id.label("venue_id"), 
    Venue.name.label("venue_name"), 
    Venue.image_link.label("venue_image_link"), 
    Show)
    .filter(Show.c.Artist_id == artist_id)
    .filter(Show.c.Venue_id == Venue.id)
    .filter(Show.c.start_time > datetime.now())
    .all())

  # 计算 past Shows 数量
  single_artist.past_shows_count = (db.session.query(
    func.count(Show.c.Artist_id))
    .filter(Show.c.Artist_id == artist_id)
    .filter(Show.c.start_time < datetime.now())
    .all())[0][0]
  
  # 计算  Upcoming Shows  数量
  single_artist.upcoming_shows_count = (db.session.query(
    func.count(Show.c.Artist_id))
    .filter(Show.c.Artist_id == artist_id)
    .filter(Show.c.start_time > datetime.now())
    .all())[0][0]
  # data1={
  #   "id": 6,
  #   "name": "The Wild Sax Band",
  #   "genres": ["Jazz", "Classical"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "432-325-5432",
  #   "seeking_venue": False,
  #   "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "past_shows": [],
  #   "upcoming_shows": [{
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-01T20:00:00.000Z"
  #   }, {
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-08T20:00:00.000Z"
  #   }, {
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-15T20:00:00.000Z"
  #   }],
  #   "past_shows_count": 0,
  #   "upcoming_shows_count": 3,
  # }
  # single_artist = list(filter(lambda d: d['id'] == artist_id, [data1]))[0]
  return render_template('pages/show_artist.html', artist=single_artist)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  # 预填充
  form.name.data = artist.name
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.genres.data = artist.genres
  form.facebook_link.data = artist.facebook_link
  form.website_link.data = artist.website_link
  form.image_link.data = artist.image_link
  form.seeking_venue.data = artist.seeking_venue
  form.seeking_description.data = artist.seeking_description
  # artist={
  #   "id": 4,
  #   "name": "Guns N Petals",
  #   "genres": ["Rock n Roll"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "326-123-5000",
  #   "website": "https://www.gunsnpetalsband.com",
  #   "facebook_link": "https://www.facebook.com/GunsNPetals",
  #   "seeking_venue": True,
  #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  # }
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: 更新新的信息  这里有问题 实现不了
  artist = Venue.query.get(artist_id)
  artist.name = request.form['name']
  artist.city = request.form['city']
  artist.state = request.form['state']
  artist.phone = request.form['phone']
  artist.genres = request.form['genres']
  artist.facebook_link = request.form['facebook_link']
  artist.website_link = request.form['website_link']
  artist.image_link = request.form['image_link']
  artist.seeking_description = request.form['seeking_description']
  artist.seeking_venue = request.form['seeking_venue']
  db.session.add(artist)
  db.session.commit()
  db.session.close()
  # 重定向到音乐家详情页面
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
    # 预填充
  form.name.data = venue.name
  form.city.data = venue.city
  form.state.data = venue.state
  form.address.data = venue.address
  form.phone.data = venue.phone
  form.genres.data = venue.genres
  form.facebook_link.data = venue.facebook_link
  form.website_link.data = venue.website_link
  form.image_link.data = venue.image_link
  form.seeking_talent.data = venue.seeking_talent
  form.seeking_description.data = venue.seeking_description
  # venue={
  #   "id": 1,
  #   "name": "The Musical Hop",
  #   "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
  #   "address": "1015 Folsom Street",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "123-123-1234",
  #   "website": "https://www.themusicalhop.com",
  #   "facebook_link": "https://www.facebook.com/TheMusicalHop",
  #   "seeking_talent": True,
  #   "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
  #   "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  # }
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id): # 提交表单
  # TODO: 提交修改内容
  venue = Venue.query.get(venue_id)
  venue.name = request.form['name']
  venue.city = request.form['city']
  venue.state = request.form['state']
  venue.address = request.form['address']
  venue.phone = request.form['phone']
  venue.genres = request.form.getlist('genres')
  venue.facebook_link = request.form['facebook_link']
  venue.website_link = request.form['website_link']
  venue.image_link = request.form['image_link']
  venue.seeking_description = request.form['seeking_description']
  venue.seeking_talent = request.form['seeking_talent']  # TODO 这个键有问题 可能与数据库有关
  db.session.add(venue)
  db.session.commit()
  db.session.close()

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  form = ArtistForm(request.form)
  flashType = 'danger'
  if form.validate():
    try:
      newArtist = Artist(
        name = request.form['name'],
        city = request.form['city'],
        state = request.form['state'],
        phone = request.form['phone'],
        facebook_link = request.form['facebook_link'],
        genres = request.form.getlist('genres'),
        website_link = request.form['website_link'],
        image_link = request.form['image_link'],
        seeking_description = request.form['seeking_description'],
        seeking_venue = request.form['seeking_venue'],  # TODO
      )
      db.session.add(newArtist)
      db.session.commit()
      flashType = 'success'
      flash('音乐人 ' + request.form['name'] + ' 被成功创建!')
    except:
      flash('数据库插入过程发生错误， ' + request.form['name'] + ' 创建失败')
    finally:
      db.session.close()
  else:
    flash(form.errors)
    flash('表单不符合要求， ' + request.form['name'] + ' 创建失败')

    # TODO 出现错误：数据库插入过程发生错误， 冀禹乔 创建失败
  return render_template('pages/home.html',flashType = flashType)


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # 展示 shows
  # 查询所有的shows并且对查询结果的列名重命名以便前端可以正确显示
  data = (db.session.query(
    Venue.id.label("venue_id"), 
    Venue.name.label("venue_name"),
    Artist.id.label("artist_id"), 
    Artist.name.label("artist_name"), 
    Artist.image_link.label("artist_image_link"), 
    Show)
    .filter(Show.c.Venue_id == Venue.id)
    .filter(Show.c.Artist_id == Artist.id)
    .all())  
  # data=[{
  #   "venue_id": 1,
  #   "venue_name": "The Musical Hop",
  #   "artist_id": 4,
  #   "artist_name": "Guns N Petals",
  #   "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "start_time": "2019-05-21T21:30:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 5,
  #   "artist_name": "Matt Quevedo",
  #   "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #   "start_time": "2019-06-15T23:00:00.000Z"
  # }]
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  form = ShowForm(request.form) # Initialize form instance with values from the request
  flashType = 'danger' 
  if form.validate():
    # NOTE: 出现错误：表单不合格，原因是missing csrf-token.
    # 解决：在 forms/new_show.html 里 加 "{{ form.csrf_token() }}"
    try:
      #  关系表只能用insert插入  关系表本质是一个class
      newShow = Show.insert().values(
        Venue_id = request.form['venue_id'],
        Artist_id = request.form['artist_id'],
        start_time = str(request.form['start_time'])
      )
      db.session.execute(newShow)  # execute
      db.session.commit()
      flashType = 'success'
      flash('成功创建演出Show!')
    except : 
      flash('数据库插入过程发生错误, 演出show创建失败')    
    finally:
      # Always close session
      db.session.close()
  else:
    flash(form.errors) # Flashes reason, why form is unsuccessful (not really pretty)
    flash('提交的表单不合格. Show创建失败.')
  
  return render_template('pages/home.html', flashType = flashType)


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run(debug=True)

