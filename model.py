import os
from flask import Flask,render_template,url_for,request,session,flash,redirect	
from flask_sqlalchemy import SQLAlchemy
app=Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SECRET_KEY']='ewr7yjdfj02319irweiuhyfbdo02e9rejkkqpo2984w0ou9201opkqwlsjnacjkhdiewuop'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=True


db = SQLAlchemy(app)

class Users(db.Model):
	customer_id=db.Column(db.Integer,primary_key=True)
	customer_name=db.Column(db.String(50))
	customer_username=db.Column(db.String(50),unique=True)
	customer_password=db.Column(db.String(50))
	customer_contact=db.Column(db.String(50))
	def __init__(self,customer_name,customer_username,customer_password,customer_contact):
		self.customer_name=customer_name
		self.customer_username=customer_username
		self.customer_password=customer_password
		self.customer_contact=customer_contact

class sellers(db.Model):
	seller_id=db.Column(db.Integer,primary_key=True)
	customer_id=db.Column(db.Integer,unique=True)
	seller_contact=db.Column(db.String(50))
	def __init__(self,customer_id,seller_contact):
		self.customer_id=customer_id
		self.seller_contact=seller_contact

class products(db.Model):
	product_id=db.Column(db.Integer,primary_key=True)
	product_name=db.Column(db.String(50))
	seller_id=db.Column(db.Integer)
	product_category=db.Column(db.String(50))
	product_description=db.Column(db.String(150))
	product_price=db.Column(db.Integer)
	product_image=db.Column(db.String(50))
	product_quantity=db.Column(db.Integer)
	no_of_raters=db.Column(db.Integer)
	product_rating=db.Column(db.Integer)
	def __init__(self,seller_id,product_name,product_category,product_description,product_price,product_image,product_quantity,no_of_raters=0,product_rating=0):
		self.product_name=product_name
		self.seller_id=seller_id
		self.product_category=product_category
		self.product_description=product_description
		self.product_price=product_price
		self.product_image=product_image
		self.product_quantity=product_quantity
		self.no_of_raters=no_of_raters
		self.product_rating=product_rating

class sales(db.Model):
	serial_no=db.Column(db.Integer,primary_key=True)
	product_id=db.Column(db.Integer)
	seller_id=db.Column(db.Integer)
	customer_id=db.Column(db.Integer)
	def __init__(self,product_id,seller_id,customer_id):
		self.product_id=product_id
		self.seller_id=seller_id
		self.customer_id=customer_id

class cart(db.Model):
	serial_no=db.Column(db.Integer,primary_key=True)
	product_id=db.Column(db.Integer)
	customer_id=db.Column(db.Integer)
	product_name=db.Column(db.String(50))
	product_image=db.Column(db.String(50))
	def __init__(self,product_id,customer_id,product_name,product_image):
		self.product_id=product_id
		self.customer_id=customer_id
		self.product_name=product_name
		self.product_image=product_image