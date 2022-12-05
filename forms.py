from datetime import datetime
from flask_wtf import Form
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField, BooleanField
from wtforms.validators import DataRequired, AnyOf, URL

class ShowForm(Form):
    artist_id = StringField(
        'artist_id'
    )
    venue_id = StringField(
        'venue_id'
    )
    start_time = DateTimeField(
        'start_time',
        validators=[DataRequired()],
        default= datetime.today()
    )

class VenueForm(Form):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired()],
        choices=[
            ('山西', '山西'),
            ('北京', '北京'),
            ('天津', '天津'),
            ('重庆', '重庆'),
            ('上海', '上海'),
            ('河北', '河北'),
            ('甘肃', '甘肃'),
            ('黑龙江', '黑龙江'),
            ('吉林', '吉林'),
            ('辽宁', '辽宁'),
            ('河北', '河北'),
            ('河南', '河南'),
            ('陕西', '陕西'),
            ('宁夏', '宁夏'),
            ('青海', '青海'),
            ('江苏', '江苏'),
            ('浙江', '浙江'),
            ('福建', '福建'),
            ('江西', '江西'),
            ('广东', '广东'),
            ('海南', '海南'),
            ('广西', '广西'),
            ('江西', '江西'),
            ('安徽', '安徽'),
            ('湖南', '湖南'),
            ('四川', '四川'),
            ('云南', '云南'),
            ('西藏', '西藏'),
            ('台湾', '台湾'),
            ('澳门', '澳门'),
            ('香港', '香港'),
            ('湖北', '湖北'),
            ('贵州', '贵州'),
        ]
    )
    address = StringField(
        'address', validators=[DataRequired()]
    )
    phone = StringField(
        'phone'
    )
    image_link = StringField(
        'image_link'
    )
    genres = SelectMultipleField(
        # TODO implement enum restriction
        'genres', validators=[DataRequired()],
        choices=[
            ('蓝调', '蓝调'),
            ('古典', '古典'),
            ('乡村', '乡村'),
            ('电子', '电子'),
            ('民俗', '民俗'),
            ('放克', '放克'),
            ('嘻哈', '嘻哈'),
            ('重金属', '重金属'),
            ('爵士', '爵士'),
            ('音乐剧', '音乐剧'),
            ('流行', '流行'),
            ('R&B', 'R&B'),
            ('摇滚', '摇滚'),
            ('灵魂', '灵魂'),
            ('其他', '其他'),
        ]
    )
    facebook_link = StringField(
        'facebook_link', validators=[URL()]
    )
    website_link = StringField(
        'website_link'
    )

    seeking_talent = BooleanField( 'seeking_talent' )

    seeking_description = StringField(
        'seeking_description'
    )



class ArtistForm(Form):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired()],
        choices=[
            ('山西', '山西'),
            ('北京', '北京'),
            ('天津', '天津'),
            ('重庆', '重庆'),
            ('上海', '上海'),
            ('河北', '河北'),
            ('甘肃', '甘肃'),
            ('黑龙江', '黑龙江'),
            ('吉林', '吉林'),
            ('辽宁', '辽宁'),
            ('河北', '河北'),
            ('河南', '河南'),
            ('陕西', '陕西'),
            ('宁夏', '宁夏'),
            ('青海', '青海'),
            ('江苏', '江苏'),
            ('浙江', '浙江'),
            ('福建', '福建'),
            ('江西', '江西'),
            ('广东', '广东'),
            ('海南', '海南'),
            ('广西', '广西'),
            ('江西', '江西'),
            ('安徽', '安徽'),
            ('湖南', '湖南'),
            ('四川', '四川'),
            ('云南', '云南'),
            ('西藏', '西藏'),
            ('台湾', '台湾'),
            ('澳门', '澳门'),
            ('香港', '香港'),
            ('湖北', '湖北'),
            ('贵州', '贵州'),
        ]
    )
    phone = StringField(
        # TODO implement validation logic for phone 
        'phone'
    )
    image_link = StringField(
        'image_link'
    )
    genres = SelectMultipleField(
        'genres', validators=[DataRequired()],
        choices=[
            ('蓝调', '蓝调'),
            ('古典', '古典'),
            ('乡村', '乡村'),
            ('电子', '电子'),
            ('民俗', '民俗'),
            ('放克', '放克'),
            ('嘻哈', '嘻哈'),
            ('重金属', '重金属'),
            ('爵士', '爵士'),
            ('音乐剧', '音乐剧'),
            ('流行', '流行'),
            ('R&B', 'R&B'),
            ('摇滚', '摇滚'),
            ('灵魂', '灵魂'),
            ('其他', '其他'),
        ]
     )
    facebook_link = StringField(
        # TODO implement enum restriction
        'facebook_link', validators=[URL()]
     )

    website_link = StringField(
        'website_link'
     )

    seeking_venue = BooleanField( 'seeking_venue' )

    seeking_description = StringField(
            'seeking_description'
     )

