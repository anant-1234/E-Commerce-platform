import os
from flask import Flask,render_template,url_for,request,session,flash,redirect	
from flask_wtf import FlaskForm 
from flask_wtf.file import FileField, FileRequired
from wtforms.widgets import TextArea
from flask.ext.uploads import UploadSet,configure_uploads,IMAGES
from wtforms import StringField, PasswordField,IntegerField
from wtforms.validators import InputRequired,Length
from flask_sqlalchemy import SQLAlchemy
from werkzeug import secure_filename
from werkzeug.security import generate_password_hash, \
     check_password_hash
from flask_admin import Admin 
from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.sqla import ModelView
import re
from model import *

folder=os.path.join('static','img')
photos=UploadSet('photos',IMAGES)
admin=Admin(app)

app.config['UPLOAD_FOLDER']=folder
app.config['UPLOADED_PHOTOS_DEST']='static/img'

configure_uploads(app,photos)


admin.add_view(ModelView(Users, db.session))
admin.add_view(ModelView(sellers, db.session))
admin.add_view(ModelView(products, db.session))


class ProductFill(FlaskForm):
	seller_id=IntegerField('Seller-Id',validators=[InputRequired()])
	product_name=StringField('Product-Name',validators=[InputRequired()])
	product_category=StringField('Category',validators=[InputRequired()])
	product_description=StringField('Description',validators=[InputRequired()],widget=TextArea())
	product_price=IntegerField('Price',validators=[InputRequired()])
	product_image=FileField('Image',validators=[FileRequired()])
	product_quantity=IntegerField('Quantity',validators=[InputRequired()])

class ProductRemove(FlaskForm):
	seller_id=IntegerField('Seller-Id',validators=[InputRequired()])
	product_id=IntegerField('Product-Id',validators=[InputRequired()])

class SignupForm(FlaskForm):
	name=StringField('Name',validators=[InputRequired()])
	username=StringField('Username',validators=[InputRequired()])
	password=PasswordField('Password',validators=[InputRequired(),Length(min=6,max=100,message="Must contain greater than 6 characters")])
	contact=StringField('Contact Number',validators=[InputRequired()])

class LoginForm(FlaskForm):
	username=StringField('Username',validators=[InputRequired()])
	password=PasswordField('Password',validators=[InputRequired(),Length(min=6,max=100)])

class Applicationform(FlaskForm):
	key=IntegerField('Admin Security Key',validators=[InputRequired()])	

class SearchForm(FlaskForm):
	search=StringField('Search',validators=[InputRequired()])

class PayForm(FlaskForm):
	name=StringField('Name',validators=[InputRequired()])
	card_no=IntegerField('Price',validators=[InputRequired()])
	address=StringField('Name2',validators=[InputRequired()])
	cvc=IntegerField('Price2',validators=[InputRequired()])
	expiration_m=IntegerField('Name3',validators=[InputRequired()])
	expiration_y=IntegerField('Name4',validators=[InputRequired()])
								#  MAIN PAGE  #

electronics=products.query.filter_by(product_category='Electronics').all()
fashion=products.query.filter_by(product_category='Fashion').all()
perfumes=products.query.filter_by(product_category='Perfumes').all()

t=products.query.filter(products.product_price>200).all()
five=[]
for i in range(len(t)):
	if(t[i].product_price<=500):
		five.append(t[i])
q=products.query.filter(products.product_price>500).all()
thousand=[]
for i in range(len(q)):
	if(q[i].product_price<=1000):
		thousand.append(q[i])

z=products.query.filter(products.product_price>0).all()
two=[]
for i in range(len(z)):
	if(z[i].product_price<=200):
		two.append(z[i])

def hack(s):
	if re.findall('[^A-Za-z0-9_]',s):
		return 0
	return 1	

@app.route('/',methods=['GET','POST'])
def index():
	form=SearchForm()
	if form.validate_on_submit():
		if request.method=='POST':
			f=products.query.filter_by(product_name=form.search.data).scalar()
			f1=products.query.filter_by(product_name=form.search.data).first()
			if f==None:
				flash("Product Not Present","danger")
				return render_template('main.html',nform=SearchForm(),electronics=electronics,perfumes=perfumes,fashion=fashion,five=five,thousand=thousand,two=two)
			else:
				return redirect('/display_product/'+str(f1.product_id))
	return render_template('main.html',nform=SearchForm(),electronics=electronics,perfumes=perfumes,fashion=fashion,five=five,thousand=thousand,two=two)
	

@app.route('/decide')
def decide():
	form=SearchForm()
	if not 'username' in session:
		return render_template('main.html',nform=SearchForm(),electronics=electronics,perfumes=perfumes,fashion=fashion,five=five,thousand=thousand,two=two)
	else:
		return render_template('welcome2.html',electronics=electronics,perfumes=perfumes,fashion=fashion,five=five,thousand=thousand,two=two,nform=SearchForm(),idd=Users.query.filter_by(customer_username=session['username']).first().customer_id)

								#    ADMIN-PAGE  #
@app.route('/admincheck',methods=['GET','POST'])
def adminncheck():
	form=Applicationform()
	if form.validate_on_submit():
		if request.method=='POST':
			if not form.key.data==23415:
				return render_template("admincheck.html",form=form,ans=0,nform=SearchForm())
			else:
				return redirect('/admin')
	return render_template("admincheck.html",form=form,ans=1,nform=SearchForm())

								#  LOGIN AND LOGOUT FUNCTIONALITY  #


@app.route('/signup',methods=['GET','POST'])
def signup():
	form=SignupForm()
	if form.validate_on_submit():
		if request.method=='POST':
			entries=Users.query.all()
			for i in entries:
				if i.customer_username==form.username.data:
					return render_template('sign_up.html',form=form,exists=1,nform=SearchForm(),hacker=0)
				elif hack(form.username.data)==0:
					return render_template('sign_up.html',form=form,exists=0,nform=SearchForm(),hacker=1)	
			user=Users(form.name.data,form.username.data,generate_password_hash(form.password.data),form.contact.data)
			db.session.add(user)
			db.session.commit()
			form=SearchForm()
			return render_template('main.html',nform=form,electronics=electronics,perfumes=perfumes,fashion=fashion,five=five,thousand=thousand,two=two)
	
	return render_template('sign_up.html',form=form,exists=0,nform=SearchForm(),hacker=0)
						
@app.route('/logged_in')
def logged_in():
	if 'username' in session:
		a=Users.query.filter_by(customer_username=session['username']).first()
		return render_template('welcome2.html',nform=SearchForm(),electronics=electronics,perfumes=perfumes,fashion=fashion,five=five,thousand=thousand,two=two,id=a.customer_id,idd=Users.query.filter_by(customer_username=session['username']).first().customer_id)
	else:
		flash("You need to be logged in first","danger")
		form=SearchForm()
		return render_template('main.html',nform=form,electronics=electronics,perfumes=perfumes,fashion=fashion,five=five,thousand=thousand,two=two)

@app.route('/login',methods=['GET','POST'])
def login():
	error=None
	form=LoginForm()

	if request.method=='POST':

		entries=Users.query.all()
		for i in entries:
			if i.customer_username==form.username.data and check_password_hash(i.customer_password,form.password.data):
				session['username']=form.username.data
				return redirect(url_for('logged_in'))
			elif i.customer_username==form.username.data and not check_password_hash(i.customer_password,form.password.data):
				return render_template('login-form.html',form=form,found=1,wrong_password=1,hacker=0,nform=SearchForm())
			elif hack(form.username.data)==0 :
				return render_template('login-form.html',form=form,found=1,wrong_password=1,hacker=1,nform=SearchForm())			
	return render_template('login-form.html',form=form,found=0,wrong_password=0,hacker=0,nform=SearchForm())
@app.route('/login-page')
def login_page():
	form=LoginForm()
	return render_template('login-form.html',form=form,found=1,wrong_password=0,hacker=0,nform=SearchForm())

@app.route('/logout')
def logout():
	form=LoginForm()
	if 'username' in session:
		session.clear()
		return redirect(url_for('index'))
	else:
		return render_template('login-form.html',form=form,found=1,wrong_password=0,nform=SearchForm(),hacker=0)

							#   SELLERS PORTAL  #

@app.route('/authenticate_seller')
def authenticate_seller():
	nform=SearchForm()
	if 'username' in session:
		a=Users.query.filter_by(customer_username=session['username']).first()
		b=sellers.query.filter_by(customer_id=a.customer_id).scalar()
		if(b==None):
			return render_template('seller_reg.html',id=a.customer_id,nform=SearchForm(),idd=Users.query.filter_by(customer_username=session['username']).first().customer_id)
		else:
			return redirect(url_for('sale'))
	else:
		flash("You need to be logged in first","danger")
		return render_template('main.html',nform=SearchForm(),electronics=electronics,perfumes=perfumes,fashion=fashion,five=five,thousand=thousand,two=two)

@app.route('/add_seller/<int:customer_id>')
def add_seller(customer_id):
	b=Users.query.filter_by(customer_id=customer_id).first()
	seller=sellers(customer_id,b.customer_contact)
	db.session.add(seller)
	db.session.commit()
	return redirect(url_for('sale'))



@app.route('/seller')
def sale():
	a=Users.query.filter_by(customer_username=session['username']).first()
	b=sellers.query.filter_by(customer_id=a.customer_id).first()
	return render_template('new_sel.html',id=b.seller_id,nform=SearchForm(),idd=Users.query.filter_by(customer_username=session['username']).first().customer_id)

@app.route('/add',methods=['GET','POST'])
def add():
	error=None
	form=ProductFill()

	if form.validate_on_submit():
		if request.method=='POST':
			f=form.product_image.data
			filename=secure_filename(f.filename)
			f.save('static/img/'+filename)
			a=Users.query.filter_by(customer_username=session['username']).first()
			b=sellers.query.filter_by(customer_id=a.customer_id).first()
			if not b.seller_id == form.seller_id.data:
				return render_template('input.html',form=form,wrong=1,nform=SearchForm(),idd=Users.query.filter_by(customer_username=session['username']).first().customer_id)
			else: 
				product=products(form.seller_id.data,form.product_name.data,form.product_category.data,form.product_description.data,form.product_price.data,filename,form.product_quantity.data)
				db.session.add(product)
				db.session.commit()
				return redirect('/items/'+str(form.seller_id.data))
	return render_template('input.html',form=form,wrong=0,nform=SearchForm(),idd=Users.query.filter_by(customer_username=session['username']).first().customer_id)	
	
@app.route('/delete',methods=['GET','POST'])
def delete():
	form=ProductRemove()
	if form.validate_on_submit():
		if request.method=='POST':
			tr=products.query.filter_by(product_id=form.product_id.data)
			exists=tr.scalar()
			product=tr.first()
			a=Users.query.filter_by(customer_username=session['username']).first()
			b=sellers.query.filter_by(customer_id=a.customer_id).first()
			if exists==None:
				return render_template('input2.html',found=0,form=form,wrong=0,nform=SearchForm(),idd=Users.query.filter_by(customer_username=session['username']).first().customer_id)
			elif not b.seller_id == form.seller_id.data:
				return render_template('input2.html',wrong=1,found=1,form=form,nform=SearchForm(),idd=Users.query.filter_by(customer_username=session['username']).first().customer_id)
			elif not product.seller_id==form.seller_id.data:
				return render_template('input2.html',found=0,form=form,wrong=0,nform=SearchForm(),idd=Users.query.filter_by(customer_username=session['username']).first().customer_id)
			else:
				tr.delete()
				db.session.commit()
				return redirect('/items/'+str(form.seller_id.data)) 
				
	return render_template('input2.html',form=form,found=1,wrong=0,nform=SearchForm(),idd=Users.query.filter_by(customer_username=session['username']).first().customer_id)

@app.route('/items/<int:seller_id>')
def items(seller_id):
	q=products.query.filter_by(seller_id=seller_id).all()
	return render_template('my_products.html',product=q,id=seller_id,nform=SearchForm(),idd=Users.query.filter_by(customer_username=session['username']).first().customer_id)

					# SOLD ITEMS
@app.route('/pay_on_buy/<int:customer_id>/<int:sum>',methods=['GET','POST'])
def pay_on_buy(customer_id,sum):
	form=PayForm()
	if form.validate_on_submit():
		if request.method=='POST':
			return redirect('/buy_all/'+str(customer_id))
	return render_template('pay.html',nform=SearchForm(),idd=Users.query.filter_by(customer_username=session['username']).first().customer_id,form=form,sum=sum)

@app.route('/sold_items/<int:product_id>')
def sold_items(product_id):
	a=products.query.filter_by(product_id=product_id).first()
	b=Users.query.filter_by(customer_username=session['username']).first()
	tr=sales(a.product_id,a.seller_id,b.customer_id)
	db.session.add(tr)
	db.session.commit()
	return render_template('rating.html',nform=SearchForm(),idd=Users.query.filter_by(customer_username=session['username']).first().customer_id)



@app.route('/add_in_cart/<int:product_id>')
def add_in_cart(product_id):
	if 'username' in session:
		a=products.query.filter_by(product_id=product_id).first()
		b=Users.query.filter_by(customer_username=session['username']).first()
		tr=cart(product_id,b.customer_id,a.product_name,a.product_image)
		db.session.add(tr)
		db.session.commit()
		return redirect('/items_in_cart/'+str(b.customer_id))
	else:
		flash("You need to be logged in first","danger")
		return redirect('/display_product/'+str(product_id))


@app.route('/remove_from_cart/<int:serial_no>')
def remove_from_cart(serial_no):
	a=cart.query.filter_by(serial_no=serial_no).first()
	customer_id=a.customer_id
	cart.query.filter_by(serial_no=serial_no).delete()
	db.session.commit()
	return redirect('/items_in_cart/'+str(customer_id))


@app.route('/display_product/<int:product_id>')
def display_product(product_id):
	a=products.query.filter_by(product_id=product_id).first()
	full='img/'+str(a.product_image)
	tempans=Users.query.filter_by(customer_id=a.seller_id).first()
	c=sellers.query.filter_by(seller_id=a.seller_id).first()
	d=Users.query.filter_by(customer_id=c.customer_id).first()
	if 'username' in session:
		return render_template('tempprod.html',ans=a,orp=a.product_price*10/9,sans=tempans,full=full,name=d.customer_username,a=products.no_of_raters,nform=SearchForm(),idd=d.customer_id)
	else:
		return render_template('tempprod1.html',ans=a,orp=a.product_price*10/9,sans=tempans,full=full,name=d.customer_username,a=products.no_of_raters,nform=SearchForm(),idd=d.customer_id)

@app.route('/items_in_cart/<int:customer_id>')
def items_in_cart(customer_id):
	a=cart.query.filter_by(customer_id=customer_id).all()
	sum=0
	for prod in a:
		b=prod.product_id
		c=products.query.filter_by(product_id=b).first()
		if c:
			sum=sum+c.product_price
	return render_template('cart.html',items=a,id=customer_id,nform=SearchForm(),idd=Users.query.filter_by(customer_username=session['username']).first().customer_id,sum=sum)

@app.route('/sasa')
def sasa():
	return render_template('new_sel.html',nform=SearchForm(),idd=Users.query.filter_by(customer_username=session['username']).first().customer_id)

@app.route('/contactus',methods=['GET','POST'])
def contact():
	if 'username' in session:
		return render_template('contact.html',nform=SearchForm(),idd=Users.query.filter_by(customer_username=session['username']).first().customer_id)
	else:
		return render_template('contact2.html',nform=SearchForm())


@app.route('/buy_all/<int:customer_id>')
def buy_all(customer_id):
	items=cart.query.filter_by(customer_id=customer_id).all()
	for i in items:
		s=products.query.filter_by(product_id=i.product_id).first()
		item=sales(i.product_id,s.seller_id,customer_id)
		db.session.add(item)
		db.session.commit()
		cart.query.filter_by(customer_id=customer_id).delete()
		db.session.commit()
	return redirect('/bought_list/'+str(customer_id))

@app.route('/bought_list/<int:customer_id>')
def bought_list(customer_id):
	a=sales.query.filter_by(customer_id=customer_id).all()
	items=[]
	for i in a:	
		item=products.query.filter_by(product_id=i.product_id).first()
		if item:
			items.append(item)
	return render_template('bought_list.html',items=items,id=customer_id,nform=SearchForm())				


@app.route('/rate/<int:product_id>',methods=['GET','POST'])
def rate(product_id):
	nform=SearchForm()
	a1=Users.query.filter_by(customer_username=session['username']).first()
	exists=sales.query.filter_by(product_id=product_id).scalar()
	b1=sales.query.filter_by(product_id=product_id).first()
	c1=products.query.filter_by(product_id=product_id).first()
	if exists==None:
		flash('You have not bought this item, So U cannot rate this item','danger')
		return redirect('/display_product/'+str(product_id))
	elif not a1.customer_id == b1.customer_id:
		flash('You have not bought this item, So U cannot rate this item','danger')
		return redirect('/display_product/'+str(product_id))
	else:
		if request.method=='POST':
			if not request.form['stars']:

				return render_template('rating.html',flag=1,id=product_id,nform=nform)
			else:
				c1.product_rating=(c1.product_rating*c1.no_of_raters+float(request.form['stars']))*1.0/(c1.no_of_raters+1)
				c1.no_of_raters+=1
				db.session.add(c1)
				db.session.commit()
				return "Thanks for ur feedback"
		return render_template('rating.html',flag=0,id=product_id,nform=nform)


if __name__ == "__main__":
	db.create_all()
	app.run(debug=True)


