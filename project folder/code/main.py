import os
import bcrypt
from werkzeug.exceptions import HTTPException
from datetime import datetime
from flask import make_response, url_for
import json
from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from flask_restful import fields, marshal_with
from flask import render_template, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from flask_cors import CORS
from flask_login import LoginManager,login_user, current_user, logout_user, login_required	
from flask_security import UserMixin ,RoleMixin, login_required
app = Flask(__name__)
current_dir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] ="sqlite:///"+os.path.join(current_dir, "project.sqlite3")
app.config["SECRET_KEY"] = "sedfrtgh@@@yyh!!"
db=SQLAlchemy()
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'home'
CORS(app)
db.init_app(app)
app.app_context().push()
api=Api(app)

user_role=db.Table('user_role', db.Column('ur_user_id',
          db.Integer(), db.ForeignKey('user.user_id')),db.Column('ur_role_id',db.Integer(), 
          db.ForeignKey('role.role_id')))


class User(db.Model, UserMixin):
  __tablename__='user'
  user_id= db.Column(db.Integer, autoincrement=True,primary_key=True)
  name= db.Column(db.String,unique=False, nullable=False)
  username= db.Column(db.String, unique=True, nullable=False)
  email= db.Column(db.String, unique= True, nullable=False)
  password=db.Column(db.String, unique= True, nullable=False)
  address=db.Column(db.String,unique=False,nullable=False)
  role = db.relationship('Role',secondary=user_role, backref= db.backref('users', lazy='dynamic'))
  product=db.relationship('Cart',back_populates='user')
  
  
  def __init__(self, name,username,email, password,address):
        self.name = name
        self.username = username
        self.email=email
        self.password=password
        self.address=address
        
  def is_active(self):
      return True

  def get_id(self):
      return self.user_id

  def is_authenticated(self):
     return self.authenticated

  def is_anonymous(self):
      return False
        
  def __repr__(self):
      return f'<User:{self.username}>'

class Role(db.Model, RoleMixin):
    __tablename__= 'role'
    role_id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)
  
    
    def __init__(self, name):
        self.name = name
    
    def __repr__(self):
      return f'<Role:{self.name}>'
      

class Category(db.Model):
  __tablename__='category'
  category_id= db.Column(db.Integer, autoincrement=True,primary_key=True)
  name= db.Column(db.String,unique=True, nullable=False)

  def __init__(self, name):
        self.name = name
        
  def __repr__(self):
      return f'<Product:{self.name}>'
  
      
class Product(db.Model):
  __tablename__='product'
  product_id= db.Column(db.Integer, autoincrement=True, primary_key=True)
  name= db.Column(db.String, nullable=False)
  manufacture_date=db.Column(db.String,unique=False, nullable=False)
  expiry_date= db.Column(db.String,unique=False, nullable=False)
  rate = db.Column(db.Integer, unique=False, nullable=False)
  unit= db.Column(db.String, unique=False, nullable=False)
  quantity=db.Column(db.Integer, unique=False, nullable=False)
  image=db.Column(db.String, unique=False, nullable=False)
  category_id=db.Column(db.Integer,db.ForeignKey("category.category_id"), primary_key=True, nullable=False)
  user=db.relationship('Cart',back_populates='product')
  
  def __init__(self, name,manufacture_date,expiry_date,rate,unit,quantity,category_id,image):
        self.name = name
        self.manufacture_date= manufacture_date
        self.expiry_date=expiry_date
        self.rate = rate
        self.unit= unit
        self.quantity=quantity
        self.category_id=category_id
        self.image=image
        
        
  def __repr__(self):
      return f'<Product:{self.name}>'
      
class Cart(db.Model):
  __tablename__='cart'
  cart_id= db.Column(db.Integer, autoincrement=True,primary_key=True)
  c_user_id= db.Column(db.Integer,db.ForeignKey("user.user_id"), primary_key= True, nullable=False)
  c_product_id= db.Column(db.Integer, db.ForeignKey("product.product_id"),primary_key=True, nullable=False)
  c_category_id=db.Column(db.Integer, db.ForeignKey("category.category_id"),primary_key=True, nullable=False)
  quantity= db.Column(db.Integer)
  total=db.Column(db.Integer)
  price=db.Column(db.Integer)
  
  user= db.relationship('User', back_populates='product')
  product= db.relationship('Product' , back_populates='user')
  
  def __init__(self,c_user_id,c_product_id,c_category_id,quantity,total,price):
     self.c_user_id=c_user_id
     self.c_product_id=c_product_id
     self.c_category_id=c_category_id
     self.quantity= quantity
     self.total=total 
     self.price=price
     
class Order(db.Model):
  __tablename__='order'
  order_id= db.Column(db.Integer, autoincrement=True,primary_key=True)
  o_user_id= db.Column(db.Integer,db.ForeignKey("user.user_id"), primary_key= True, nullable=False)
  name= db.Column(db.String)
  quantity=db.Column(db.Integer)
  price=db.Column(db.Integer)
  total=db.Column(db.Integer)
  order_time=db.Column(db.String)
 
  def __init__(self,o_user_id,name,quantity,price,total,order_time):
     self.o_user_id=o_user_id
     self.name=name
     self.quantity= quantity
     self.price=price 
     self.total=total
     self.order_time=order_time
     
class List(db.Model):
  __tablename__='list'
  list_id= db.Column(db.Integer, autoincrement=True,primary_key=True)
  l_user_id= db.Column(db.Integer,db.ForeignKey("user.user_id"), primary_key= True, nullable=False)
  name= db.Column(db.String)
  quantity=db.Column(db.Integer)
  price=db.Column(db.Integer)
  total=db.Column(db.Integer)
  order_date=db.Column(db.String)
  order_time=db.Column(db.String)
 
  def __init__(self,l_user_id,name,quantity,price,total,order_date,order_time):
     self.l_user_id=l_user_id
     self.name=name
     self.quantity= quantity
     self.price=price 
     self.total=total
     self.order_date=order_date
     self.order_time=order_time
         
if not User.query.filter(User.username=='admin_01').first():
  pas="admin_01_2023"
  pas1=pas.encode('utf-8')
  salt = bcrypt.gensalt()
  password=bcrypt.hashpw(pas1, salt)
  ad1 = User(name ="administrator", username='admin_01', email='admin@gs.com',
        password=bcrypt.hashpw(pas1,salt),address="store")
  ad1.role.append(Role(name='Admin'))
  db.session.add(ad1)
  db.session.commit()
  
if not User.query.filter(User.username=='admin_02').first():
  pas="admin_02_2023"
  pas1=pas.encode('utf-8')
  salt = bcrypt.gensalt()
  password=bcrypt.hashpw(pas1, salt)
  ad2 = User(name ="administrator_2", username='admin_02', email='admin_02@gs.com',
        password=bcrypt.hashpw(pas1,salt),address="store")
  role= Role.query.filter(Role.role_id=="9").first()
  ad2.role.append(role)
  db.session.add(ad2)
  db.session.commit()
  

 
@login_manager.user_loader
def loader_user(user_id):
    return User.query.get(int(user_id))

      
@app.route("/", methods=["GET","POST"])
def home():
  return render_template('home.html')
    
@app.route("/login", methods=["GET","POST"])
def login():
  c=Category.query.all()
  p=Product.query.all()
  if request.method=="POST":
     username=request.form["username"]
     pa=request.form["password"]
     pa1=pa.encode('utf-8')
     u= User.query.filter(User.username==username).first()
     if u:
         ur=db.session.query(user_role).filter(user_role.c.ur_user_id == u.user_id).first()
         r= Role.query.filter(Role.role_id==ur.ur_role_id).first()
         if r.name =="User":
            if bcrypt.checkpw(pa1,u.password)==True:
                login_user(u)
                user_id=u.user_id
                return redirect(url_for("userpage",user_id=user_id))
                
            else:
                return ("invalid password")
         else:
            return ("No access")
     else:
         return ("invalid username")
  return render_template('login.html')
     
@app.route("/login/user/<int:user_id>", methods=["GET","POST"])
def userpage(user_id):
  u=User.query.filter(User.user_id==user_id).first()
  c=Category.query.all()
  p=Product.query.all()
  return render_template("userpage.html", username=u.name, u=u, category=c, product=p,user_id=user_id)
  

@app.route("/login/register", methods=["GET","POST"])
def register():
   if request.method=="GET":
      return render_template('register.html')
   elif request.method=="POST":
      name=request.form["name"] 
      username=request.form["username"]
      email=request.form["email"]
      pas=request.form["password"]
      pas1=pas.encode('utf-8')
      salt = bcrypt.gensalt()
      password=bcrypt.hashpw(pas1, salt)
      address=request.form["address"] 
      roles=request.form["role"]
      p1=User(name,username,email,password,address)
      role= Role.query.filter(Role.role_id==roles).first()
      p1.role.append(role)
      if not User.query.filter(User.email == email).first():
         db.session.add(p1)
         db.session.commit()
         return login()
      else:
          return ("User already exists")
          
@app.route("/admin", methods=["GET","POST"])      
def admin_login():
     c=Category.query.all()
     p=Product.query.all()  
     if request.method=="POST":    
        un=request.form["username"]
        pa=request.form["password"]
        pa1=pa.encode('utf-8')
        u=User.query.filter(User.username==un).first()
        if u:
          ur=db.session.query(user_role).filter(user_role.c.ur_user_id == u.user_id).first()
          r= Role.query.filter(Role.role_id==ur.ur_role_id).first()
          if r.name=="Admin":
             if bcrypt.checkpw(pa1,u.password)==True:
                login_user(u)
                user_id=u.user_id
                return redirect(url_for("admin",user_id=user_id, r=r))
             else: 
                return("invalid password")
          else:
             return ("No access")
        else:
           return ("Invalid username")
     return render_template("admin_login.html")

@app.route("/admin/user/<int:user_id>", methods=["GET","POST"])  
def admin(user_id):  
   c=Category.query.all()
   p=Product.query.all()  
   u=User.query.filter(User.user_id==user_id).first()
   return render_template("admin.html", username=u.username, category=c, product=p,user_id=user_id)
 
 
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))   

@app.route("/login/user/<int:user_id>/search", methods=["GET","POST"])
@login_required
def search(user_id):
   p =Product.query.all()
   c= Category.query.all()
   u= User.query.filter(User.user_id==user_id).first()
   username= u.name
   s_name= request.form.get('q')
   
   cat=Category.query.filter(Category.name.like(s_name +'%'))
   prod=Product.query.filter(Product.name.like(s_name +'%'))
   if request.method=='POST':   
      return render_template('c_search.html',p=p, cat=cat, c=c, prod=prod, user_id=user_id, username=username)
   return ('No category product match found')
   
@app.route("/login/user/<int:user_id>/search/product", methods=["GET","POST"])
@login_required
def search_product(user_id):
   p =Product.query.all()
   c= Category.query.all()
   u= User.query.filter(User.user_id==user_id).first()
   username= u.name
   a_name= request.form.get('a')
   b_name=request.form.get('b')
   c_name= request.form.get('c')
   if request.method=='POST':   
     if a_name:
       if not b_name:
          if not c_name:
             prod=db.session.query(Product).filter(Product.rate<=a_name)
             return render_template('p_search.html',p=p,c=c, prod=prod, user_id=user_id, username=username)
     if a_name:
       if b_name:
          if not c_name:
             prod=db.session.query(Product).filter(Product.rate<=a_name,Product.manufacture_date<=b_name)
             return render_template('p_search.html',p=p,c=c, prod=prod, user_id=user_id, username=username)
      
     if a_name:
       if not b_name:
          if c_name:
             prod=db.session.query(Product).filter(Product.rate<=a_name,Product.expiry_date>=c_name)
             return render_template('p_search.html',p=p,c=c, prod=prod, user_id=user_id, username=username)  
             
     if not a_name:
       if b_name:
          if c_name:
             prod=db.session.query(Product).filter(Product.manufacture_date<=b_name,Product.expiry_date>=c_name)
             return render_template('p_search.html',p=p,c=c, prod=prod, user_id=user_id, username=username)       
     if b_name:
        prod=db.session.query(Product).filter(Product.manufacture_date<=b_name)
        return render_template('p_search.html',p=p,c=c, prod=prod, user_id=user_id, username=username)
     if c_name:
        prod=db.session.query(Product).filter(Product.expiry_date>=c_name)
        return render_template('p_search.html',p=p,c=c, prod=prod, user_id=user_id, username=username) 
   return ('No product match found')

@app.route("/login/user/<int:user_id>/profile", methods=["GET","POST"]) 
@login_required
def profile(user_id):
   u=User.query.filter(User.user_id==user_id).first()
   c=Category.query.all()
   p=Product.query.all()
   if request.method=="POST":
      u.username=request.form.get("username")
      un=u.name
      u.name=request.form.get("name")
      u.email=request.form.get("email")
      u.address=request.form.get("address")
      db.session.add(u)
      db.session.commit()
      return redirect(url_for("userpage",user_id=user_id))
   return render_template('profile.html',u=u,user_id=user_id)
   
@app.route("/login/user/<int:user_id>/profile/cp", methods=["GET","POST"]) 
@login_required  
def change_password(user_id):
    u=User.query.filter(User.user_id==user_id).first()
    c=Category.query.all()
    p=Product.query.all()   
    if request.method=="POST":
       pas=request.form.get("password")
       pas1=pas.encode('utf-8')
       salt =bcrypt.gensalt()
       u.password=bcrypt.hashpw(pas1, salt)
       db.session.add(u)
       db.session.commit()
       return redirect(url_for("userpage",user_id=user_id))
    return render_template("password.html",u=u,user_id=user_id)
      
   
 
@app.route("/admin/user/<int:user_id>/category", methods=["GET","POST"])
@login_required
def category(user_id):
    c=Category.query.filter()
    p=Product.query.all()
    return render_template('admin.html',category=c, product=p,user_id=user_id)

@app.route("/admin/user/<int:user_id>/category/add", methods=["GET","POST"])
@login_required
def add_category(user_id):
    if request.method=="GET":
       return render_template('category.html',user_id=user_id) 
    elif request.method=="POST":
       name= request.form["name"]
       c1=Category(name)
       if not Category.query.filter(Category.name == name).first():
         db.session.add(c1)
         db.session.commit()
       else:
           return ("Category already exists")
    return category(user_id)
    
@app.route("/admin/user/<int:user_id>/category/<int:category_id>/edit", methods=["GET","POST"])
@login_required
def edit_category(user_id,category_id):
    c= Category.query.filter(Category.category_id==category_id).first() 
    if request.method=="POST":
       c.name= request.form["name"]
       db.session.add(c)
       db.session.commit()
       return category(user_id)
    return render_template('update.html', c=c, user_id=user_id)
    
    
@app.route("/admin/user/<int:user_id>/category/<int:category_id>/delete", methods=["GET","POST"])
@login_required
def delete_category(user_id,category_id):
    c= Category.query.filter(Category.category_id==category_id).first()
    p= Product.query.filter(Product.category_id==category_id).all()
    if request.method=="POST":
       if p:
            for i in p:
                db.session.delete(i)
                db.session.commit()
       if c:
          db.session.delete(c)
          db.session.commit()
       return category(user_id)
    return render_template('delete.html')
   
@app.route("/admin/user/<int:user_id>/category/<int:category_id>/product/add", methods=["GET","POST"])
@login_required
def add_product(user_id,category_id):
    c= Category.query.all()
    if request.method=="GET":
       return render_template('product.html',c=c, category_id=category_id,user_id=user_id) 
    elif request.method=="POST":
       product_name=request.form.get("name")
       mfg_date= request.form.get("m_date")
       exp_date=request.form.get("e_date")
       rate= request.form.get("rate")
       unit= request.form.get("unit")
       quantity=request.form.get("quantity")
       image= request.form.get("image")
       p1=Product(product_name,mfg_date,exp_date,rate,unit,quantity,category_id,image)
       if not Product.query.filter(Product.name == product_name).first():
          db.session.add(p1)
          db.session.commit()
       else:
          return ("Product already Exists")
    return category(user_id)
          
    
@app.route("/admin/user/<int:user_id>/category/<int:category_id>/product/<int:product_id>/edit",methods=["GET","POST"])
@login_required
def edit_product(user_id,category_id,product_id):
    c= Category.query.filter(Category.category_id==category_id).first()
    p=Product.query.filter(Product.category_id==category_id).filter(Product.product_id==product_id).first()
    if request.method=="POST":
       p.name=request.form.get("p_name")
       p.manufacture_date= request.form.get("m_date")
       p.expiry_date=request.form.get("e_date")
       p.rate= request.form.get("rate")
       p.unit= request.form.get("unit")
       p.quantity=request.form.get("quantity")
       p.image= request.form.get("image")
       db.session.add(p)
       db.session.commit()
       return category(user_id)
    return render_template('product_update.html',c=c, p=p,category_id=category_id, product_id=product_id,user_id=user_id)
    
@app.route("/admin/user/<int:user_id>/category/<int:category_id>/product/<int:product_id>/delete", methods=["GET","POST"])
@login_required
def delete_product(user_id,category_id,product_id):
    p=Product.query.filter(Product.product_id==product_id).first()
    if request.method=="POST":
       if p:
          db.session.delete(p)
          db.session.commit()
       return category(user_id)
    return render_template('p_delete.html')


@app.route( "/login/user/<int:user_id>/cart", methods=["GET","POST"])
@login_required
def cart(user_id):
    u=User.query.all()
    p=Product.query.all()
    c=Cart.query.all()
    cat=Category.query.all()
    return render_template('cart.html',c=c,p=p,u=u,user_id=user_id,cat=cat)
   
@app.route("/login/user/<int:user_id>/cart/<int:product_id>/edit",methods=["GET","POST"])
@login_required
def edit_cart(user_id,product_id):
    c= Cart.query.filter(Cart.c_user_id==user_id).filter(Cart.c_product_id==product_id).first()
    p= Product.query.filter(Product.product_id==product_id).first()
    name=p.name
    o=Order.query.filter(Order.o_user_id==user_id).filter(Order.name==p.name).first()
    if request.method=="POST":
       quantity=request.form.get("quantity")
       if float(quantity)> c.quantity:
          p.quantity=p.quantity-(float(quantity)-c.quantity)
       else:
          p.quantity= p.quantity+(c.quantity-float(quantity))
       db.session.add(p)
       db.session.commit()
       c.quantity= quantity
       c.price=request.form.get("price")
       c.total= request.form.get("total")
       o.quantity=quantity
       o.order_time=datetime.now()
       o.price=request.form.get("price")
       o.total=request.form.get("total")
       db.session.add(c)
       db.session.add(o)
       db.session.commit()
       return cart(user_id)
    return render_template('edit_cart.html', c=c,p=p,user_id=user_id, product_id=product_id)
              
@app.route("/login/user/<int:user_id>/cart/<int:product_id>/delete",methods=["GET","POST"])
@login_required
def delete_cart(user_id,product_id):
    c= Cart.query.filter(Cart.c_user_id==user_id).filter(Cart.c_product_id==product_id).first()
    p= Product.query.filter(Product.product_id==product_id).first()
    name=p.name
    o=Order.query.filter(Order.o_user_id==user_id).filter(Order.name==p.name).first()
    if request.method=="POST":
       quantity=c.quantity
       if c:
         db.session.delete(c)
         db.session.delete(o)
         db.session.commit() 
         p.quantity=p.quantity + quantity
         db.session.add(p)
         db.session.commit()
         return cart(user_id)   
    return render_template('delete_cart.html')      
              
@app.route("/login/user/<int:user_id>/category/<int:category_id>/product/<int:product_id>/buy", methods=["GET","POST"])
@login_required
def buy_product(user_id,category_id,product_id):
    u= User.query.filter(User.user_id==user_id).first()
    c= Category.query.filter(Category.category_id==category_id).first()
    p=Product.query.filter(Product.product_id==product_id).first()
    if request.method=="GET":
       return render_template('buy.html', category_id=category_id, product_id=product_id,user_id=user_id,p=p,c=c)
    elif request.method=="POST":
       quantity= request.form.get("quantity")
       price= request.form.get("price")
       total= request.form.get("total")
       order_time=datetime.now()
       name=p.name
       ca=Cart(user_id, product_id,category_id, quantity,total,price)
       o=Order(user_id,name,quantity,price,total,order_time)
       db.session.add(ca)
       db.session.add(o)
       db.session.commit()
       a=p.quantity
       b=quantity
       p.quantity=a-float(b)
       db.session.add(p)
       db.session.commit()
       return cart(user_id)

@app.route("/login/user/<int:user_id>/order", methods=["GET","POST"])    
@login_required
def order(user_id):
   o= Order.query.filter(Order.o_user_id==user_id).all()
   d=datetime.now().strftime("%Y-%m-%d")
   t=datetime.now().strftime("%H:%M")
   total=0
   l=[]
   for i in o:
       li=List(user_id,i.name,i.quantity,i.price,i.total,d,t)
       db.session.add(li)
       db.session.commit()
       l.append((i.name,i.quantity,i.total))
       total+=i.total
       db.session.delete(i)
       db.session.commit()
   return render_template('order.html', user_id=user_id,o=o,d=d,t=t,total=total,l=l)
   
@app.route("/login/user/<int:user_id>/order/list", methods=["GET","POST"])    
@login_required
def list(user_id):
   l= List.query.filter(List.l_user_id==user_id).all()
   k=[]
   total=0
   if request.method=="POST":
      date=request.form.get("date")
      date=datetime.strptime(date,'%Y-%m-%d')  
      for i in l:
         i.order_date=datetime.strptime(i.order_date,'%Y-%m-%d')
         if i.order_date==date:
            k.append((i.name,i.quantity,i.total))
            total+=i.total
      date=date.strftime("%Y-%m-%d")
      return render_template("list.html", l=l,k=k, user_id=user_id,total=total,date=date)
   return render_template("list_form.html", user_id= user_id)
   
@app.route("/login/user/<int:user_id>/final", methods=["GET","POST"])
@login_required
def buy_all(user_id):
    c= Cart.query.filter(Cart.c_user_id==user_id).all()
    p=Product.query.all()
    for i in c:
       db.session.delete(i)
       db.session.commit()
    return order(user_id)
    return render_template('buy_all.html', user_id=user_id)
    

          
class NotFoundError(HTTPException):
    def __init__(self,status_code):
      self.response= make_response('', status_code)
      
class BusinessValidationError(HTTPException):
    def __init__(self, status_code, error_code, error_message):
      message={"error_code": error_code, "error_message":error_message}
      self.response= make_response(json.dumps(message),status_code)
      

output_field2={
    "category_id":fields.Integer,
    "name":fields.String,
   }
   
create_category_parser= reqparse.RequestParser()
create_category_parser.add_argument("name")

create_update_c_parser= reqparse.RequestParser()
create_update_c_parser.add_argument("name")

  
class CategoryAPI(Resource):
   @marshal_with(output_field2)
   def get(self,user_id,category_id):
      u=User.query.filter(User.user_id==user_id).first() 
      cat= db.session.query(Category).filter(Category.category_id==category_id).first()
      if u: 
         ur=db.session.query(user_role).filter(user_role.c.ur_user_id == user_id).first()
         r= Role.query.filter(Role.role_id==ur.ur_role_id).first()
         if r.name=="Admin":
           if cat:
              return cat
           else:
              raise BusinessValidationError(status_code= 404,error_code="CATEGORY002",error_message="Category not found") 
         return ("Not authorized", 401)
      raise BusinessValidationError(status_code= 404,error_code="USER001",error_message="User not found")
        
   @marshal_with(output_field2)  
   def put(self,user_id,category_id):
      u=User.query.filter(User.user_id==user_id).first()
      args=create_update_c_parser.parse_args()
      name=args.get("name", None)
      
      if  not name:
          raise BusinessValidationError(status_code= 400,error_code="CATEGORY001",error_message="name required")
          
      cat= db.session.query(Category).filter(Category.category_id==category_id).first()
      if u:
         ur=db.session.query(user_role).filter(user_role.c.ur_user_id == user_id).first()
         r= Role.query.filter(Role.role_id==ur.ur_role_id).first()
         if r.name=="Admin":
           if cat:
              cat.name=name
              db.session.add(cat)
              db.session.commit()
              return cat
           if cat is None:
              raise BusinessValidationError(status_code= 404,error_code="CATEGORY002",error_message="Category not found") 
         return ("Not authorized", 401)
      raise BusinessValidationError(status_code= 404,error_code="USER001",error_message="User not found")
       
   @marshal_with(output_field2)      
   def post(self, user_id):
      u=User.query.filter(User.user_id==user_id).first()
      args=create_category_parser.parse_args()
      name=args.get("name",None)
      if not name :
          raise BusinessValidationError(status_code= 400,error_code="CATEGORY001",error_message="name required")
      if u:
         ur=db.session.query(user_role).filter(user_role.c.ur_user_id == user_id).first()
         r= Role.query.filter(Role.role_id==ur.ur_role_id).first()
         a= db.session.query(Category).filter(Category.name==name).first()
         if r.name=="Admin":
            if a is None:
               pass
            elif a.name== name :
               raise BusinessValidationError(status_code= 409,error_code="Category003",error_message="Category already exists")
            pass
         
            new_cat= Category(name)
            db.session.add(new_cat)
            db.session.commit()
            c= db.session.query(Category).filter(Category.name==name).first()
            category_id= c.category_id
            print(category_id)
            return new_cat , 201
         return ("Not authorized", 401)
      raise BusinessValidationError(status_code= 404,error_code="USER001",error_message="User not found")
   
   @marshal_with(output_field2) 
   def delete(self,user_id,category_id):
      u=User.query.filter(User.user_id==user_id).first()
      cat= db.session.query(Category).filter(Category.category_id==category_id).first()
      if u:
        ur=db.session.query(user_role).filter(user_role.c.ur_user_id == user_id).first()
        r= Role.query.filter(Role.role_id==ur.ur_role_id).first()
        if r.name=="Admin":
           if cat:
              pass
           else:
              raise BusinessValidationError(status_code= 404,error_code="CATEGORY002",error_message="Category not found")
           product=db.session.query(Product).filter(Product.category_id==category_id).all() 
           if product:
             for i in product:
                 db.session.delete(i)
             db.session.commit()
             db.session.delete(cat)
             db.session.commit()
           else:
             db.session.delete(cat)
             db.session.commit()
             return ('Successfully Deleted', 200) 
        return ('Not authorized',401)
      raise BusinessValidationError(status_code= 404,error_code="USER001",error_message="User not found")
      
api.add_resource(CategoryAPI, "/api/admin/user/<int:user_id>/category", "/api/admin/user/<int:user_id>/category/<int:category_id>")  

output_field3={
    "product_id":fields.Integer,
    "name":fields.String,
    "manufacture_date":fields.String,
    "expiry_date" : fields.String,
    "rate": fields.Integer,
    "unit":fields.String,
    "quantity":fields.Integer,
    "category_id":fields.Integer,
    "image":fields.String
   }
   
create_product_parser= reqparse.RequestParser()
create_product_parser.add_argument("name")
create_product_parser.add_argument("manufacture_date")
create_product_parser.add_argument("expiry_date")
create_product_parser.add_argument("unit")
create_product_parser.add_argument("rate")
create_product_parser.add_argument("quantity")
create_product_parser.add_argument("category_id")
create_product_parser.add_argument("image")


create_update_p_parser= reqparse.RequestParser()
create_update_p_parser.add_argument("name")
create_update_p_parser.add_argument("manufacture_date")
create_update_p_parser.add_argument("expiry_date")
create_update_p_parser.add_argument("rate")
create_update_p_parser.add_argument("unit")
create_update_p_parser.add_argument("quantity")
create_update_p_parser.add_argument("category_id")
create_update_p_parser.add_argument("image")
  
class ProductAPI(Resource):
   @marshal_with(output_field3)
   def get(self,user_id, category_id,product_id):
      u=User.query.filter(User.user_id==user_id).first()
      cat= Category.query.filter(Category.category_id==category_id).first()
      if u:
       if cat:
         ur=db.session.query(user_role).filter(user_role.c.ur_user_id == user_id).first()
         r= Role.query.filter(Role.role_id==ur.ur_role_id).first()
         p= db.session.query(Product).filter(Product.category_id==category_id).filter(Product.product_id==product_id).first()
         if r.name=="Admin":
            if p:
               return p
            else:
              raise BusinessValidationError(status_code= 404,error_code="PRODUCT010",error_message="Product not found") 
         return ("Not authorized", 401) 
       raise BusinessValidationError(status_code= 404,error_code="CATEGORY002",error_message="Category not found")  
      raise BusinessValidationError(status_code= 404,error_code="USER001",error_message="User not found")
      
   @marshal_with(output_field3)  
   def put(self,user_id,category_id,product_id):
      u=User.query.filter(User.user_id==user_id).first()
      cat= Category.query.filter(Category.category_id==category_id).first()
      args=create_update_p_parser.parse_args()
      name=args.get("name",None)
      manufacture_date=args.get("manufacture_date",None)
      expiry_date=args.get("expiry_date",None)
      rate=args.get("rate",None)
      unit=args.get("unit",None)
      quantity=args.get("quantity",None)
      category_id=args.get("category_id",None)
      image=args.get("image",None)
      
      if not name :
          raise BusinessValidationError(status_code= 400,error_code="PRODUCT001",error_message="Product name required")
          
      if not manufacture_date :
          raise BusinessValidationError(status_code= 400,error_code="PRODUCT002",error_message="Manufacture date required")
          
      if not expiry_date:
          raise BusinessValidationError(status_code= 400,error_code="PRODUCT003",error_message="EXpiry date required")
          
      if not rate :
          raise BusinessValidationError(status_code= 400,error_code="PRODUCT004",error_message="Rate required")
          
      if not quantity :
          raise BusinessValidationError(status_code= 400,error_code="PRODUCT005",error_message="Quantity required")
         
      
      if not unit :
          raise BusinessValidationError(status_code= 400,error_code="PRODUCT006",error_message="Unit is required")
          
      if not category_id :
          raise BusinessValidationError(status_code= 400,error_code="PRODUCT007",error_message="Category_id required")
      
      if not image :
          raise BusinessValidationError(status_code= 400,error_code="PRODUCT008",error_message="Image required")
          
      if u:
       if cat:
         ur=db.session.query(user_role).filter(user_role.c.ur_user_id == user_id).first()
         r= Role.query.filter(Role.role_id==ur.ur_role_id).first()
         if r.name=="Admin":
            p= db.session.query(Product).filter(Product.product_id==product_id).first()
            if p:
               p.name=name
               p.manufacture_date=manufacture_date
               p.expiry_date=expiry_date
               p.rate=rate
               p.unit=unit
               p.quantity=quantity
               p.category_id=category_id
               p.image=image
               db.session.add(p)
               db.session.commit()
               return p
            if p is None:
               raise BusinessValidationError(status_code= 404,error_code="PRODUCT010",error_message="Product not found") 
         return ("Not authorized", 401)
       raise BusinessValidationError(status_code= 404,error_code="CATEGORY002",error_message="Category not found")   
      raise BusinessValidationError(status_code= 404,error_code="USER001",error_message="User not found")
       
   @marshal_with(output_field3)      
   def post(self, user_id, category_id):
      u=User.query.filter(User.user_id==user_id).first()
      cat= Category.query.filter(Category.category_id==category_id).first()
      args=create_product_parser.parse_args()
      name=args.get("name",None)
      manufacture_date=args.get("manufacture_date",None)
      expiry_date=args.get("expiry_date",None)
      rate=args.get("rate",None)
      unit= args.get("unit", None)
      quantity=args.get("quantity",None)
      category_id=args.get("category_id",None)
      image=args.get("image",None)
    
      if  not name :
          raise BusinessValidationError(status_code= 400,error_code="PRODUCT001",error_message="product name required")
          
      if not manufacture_date :
          raise BusinessValidationError(status_code= 400,error_code="PRODUCT002",error_message="Manufacture date required")
          
      if not expiry_date:
          raise BusinessValidationError(status_code= 400,error_code="PRODUCT003",error_message="Expiry date required")
          
      if not rate :
          raise BusinessValidationError(status_code= 400,error_code="PRODUCT004",error_message="Rate required")
          
      if not quantity :
          raise BusinessValidationError(status_code= 400,error_code="PRODUCT005",error_message="Quantity required")
          
         
      if not unit :
          raise BusinessValidationError(status_code= 400,error_code="PRODUCT006",error_message="Unit is required")
          
      if not category_id :
          raise BusinessValidationError(status_code= 400,error_code="PRODUCT007",error_message="Category_id required")
      
      if not image :
          raise BusinessValidationError(status_code= 400,error_code="PRODUCT008",error_message="Image required")
      
      if u:
       if cat:
         ur=db.session.query(user_role).filter(user_role.c.ur_user_id == user_id).first()
         r= Role.query.filter(Role.role_id==ur.ur_role_id).first()
         if r.name=="Admin":    
            a= db.session.query(Product).filter(Product.name==name).first()
            if a is None:
                  pass
            elif a.name== name :
                 raise BusinessValidationError(status_code= 409,error_code="PRODUCT009",error_message="Product already exists")
            pass
 
            new_p= Product(name,manufacture_date,expiry_date,rate,unit,quantity,category_id,image)
            db.session.add(new_p)
            db.session.commit() 
            return new_p, 201
         return ("Not authorized", 401)
       raise BusinessValidationError(status_code= 404,error_code="CATEGORY002",error_message="Category not found")   
      raise BusinessValidationError(status_code= 404,error_code="USER001",error_message="User not found") 
       
   @marshal_with(output_field3)  
   def delete(self,user_id,category_id,product_id):
      u=User.query.filter(User.user_id==user_id).first()   
      cat= Category.query.filter(Category.category_id==category_id).first()
      if u: 
       if cat:
        ur=db.session.query(user_role).filter(user_role.c.ur_user_id == user_id).first()
        r= Role.query.filter(Role.role_id==ur.ur_role_id).first()
        if r.name=="Admin":
           p= db.session.query(Product).filter(Product.category_id==category_id).filter(Product.product_id==product_id).first()
           if p:
              db.session.delete(p)
              db.session.commit()
           else:
              raise BusinessValidationError(status_code= 404,error_code="PRODUCT010",error_message="Product not found") 
           return ('Successfully Deleted', 200) 
        return ('Not authorized', 401)
       raise BusinessValidationError(status_code= 404,error_code="CATEGORY002",error_message="Category not found")   
      raise BusinessValidationError(status_code= 404,error_code="USER001",error_message="User not found")
      
api.add_resource(ProductAPI,"/api/admin/user/<int:user_id>/category/<int:category_id>/product","/api/admin/user/<int:user_id>/category/<int:category_id>/product/<int:product_id>")

output_field4={
    "product_id":fields.Integer,
    "name":fields.String,
    "manufacture_date":fields.String,
    "expiry_date" : fields.String,
    "rate": fields.Integer,
    "unit":fields.String,
    "quantity":fields.Integer,
    "category_id":fields.Integer,
    "image":fields.String
   }


create_user_parser= reqparse.RequestParser()
create_user_parser.add_argument("name")
create_user_parser.add_argument("manufacture_date")
create_user_parser.add_argument("expiry_date")
create_user_parser.add_argument("rate")
create_user_parser.add_argument("unit")
create_user_parser.add_argument("quantity")
create_user_parser.add_argument("category_id")
create_user_parser.add_argument("image")


create_update_u_parser= reqparse.RequestParser()
create_update_u_parser.add_argument("name")
create_update_u_parser.add_argument("manufacture_date")
create_update_u_parser.add_argument("expiry_date")
create_update_u_parser.add_argument("rate")
create_update_u_parser.add_argument("unit")
create_update_u_parser.add_argument("quantity")
create_update_u_parser.add_argument("category_id")
create_update_u_parser.add_argument("image")

class P_ProductAPI(Resource):
   @marshal_with(output_field4)
   def get(self,user_id, category_id):
      u=User.query.filter(User.user_id==user_id).first()
      cat =Category.query.filter(Category.category_id==category_id).first()
      p= db.session.query(Product).filter(Product.category_id==category_id).all()
      if u :
        if cat:
         ur=db.session.query(user_role).filter(user_role.c.ur_user_id == user_id).first()
         r= Role.query.filter(Role.role_id==ur.ur_role_id).first()
         if r.name=="User":
           if p:
              return p
           else:
              raise BusinessValidationError(status_code= 404,error_code="PRODUCT010",error_message="Product not found") 
         return ("Not authorized", 401) 
        raise BusinessValidationError(status_code= 404,error_code="CATEGORY002",error_message="Category not found") 
      raise BusinessValidationError(status_code= 404, error_code="USER001",error_message="User not found")
     

api.add_resource(P_ProductAPI,"/api/login/user/<int:user_id>/category/<int:category_id>/product")

output_field5={
    "category_id":fields.Integer,
    "name":fields.String,
   }
   
create_user_c_parser= reqparse.RequestParser()
create_user_c_parser.add_argument("name")

create_update_uc_parser= reqparse.RequestParser()
create_update_uc_parser.add_argument("name")

  
class C_CategoryAPI(Resource):
   @marshal_with(output_field2)
   def get(self,user_id):    
      u=User.query.filter(User.user_id==user_id).first()
      cat=Category.query.all()
      if u:
         ur=db.session.query(user_role).filter(user_role.c.ur_user_id == user_id).first()
         r= Role.query.filter(Role.role_id==ur.ur_role_id).first()
         if r.name=="User":
            if cat:
               return cat
            else:
               raise BusinessValidationError(status_code= 404,error_code="CATEGORY002",error_message="Category not found")
         return ("Not authorized", 401)    
      raise BusinessValidationError(status_code= 404,error_code="USER001",error_message="User not found")
      
api.add_resource(C_CategoryAPI,"/api/login/user/<int:user_id>/category")

      
if __name__ == '__main__':
  app.run(host='0.0.0.0', port =5000)
   

