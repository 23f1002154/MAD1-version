from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    contact = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    address = db.Column(db.String(300), nullable=False)
    is_block = db.Column(db.Boolean, default=False)
    service_requests = db.relationship("Service_Request", cascade="all, delete", backref="user", lazy=True)

class Professional(db.Model):
    __tablename__ = 'professional'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    
    contact = db.Column(db.Integer, nullable=False)
    experience = db.Column(db.Integer, nullable=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False, unique=False)
    address = db.Column(db.String(300), nullable=False)
    is_block = db.Column(db.Boolean, default=False)
    is_approved = db.Column(db.Boolean, default=False)
    profession_id = db.Column(db.Integer, db.ForeignKey("services.service_id"), nullable=True)
    service_requests = db.relationship("Service_Request", back_populates="professional")

class Service_Request(db.Model):
    __tablename__ = "service_request"
    id = db.Column(db.Integer, primary_key=True)
    assigned = db.Column(db.Boolean, default=False)
    request_for_service_id = db.Column(db.Integer, db.ForeignKey("services.service_id"), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey("professional.id"), nullable=True) 
    date_of_service = db.Column(db.String(50), unique=False, nullable=False)
    description = db.Column(db.String(100), unique=False, nullable=False)
    offered_Price = db.Column(db.String(20),unique=False, nullable=False)
    status = db.Column(Enum('accepted','rejected','completed','N/A','closed'),default='N/A')
    professional = db.relationship("Professional", back_populates="service_requests")

class Services(db.Model):
    __tablename__ = "services"
    service_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    date_created = db.Column(db.String(50),nullable=False)
    description = db.Column(db.String(400), nullable=False)
    time_required = db.Column(db.String(50), nullable=False)
    base_price = db.Column(db.String(50), nullable = False)
    professionals = db.relationship("Professional", cascade="all, delete", backref="service", lazy=True)