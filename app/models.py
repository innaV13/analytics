from app import db
from datetime import datetime

class Imports(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    date = db.Column(db.DateTime(),nullable=False, default=datetime.now())

class Citizens(db.Model):
    import_id = db.Column(db.Integer, db.ForeignKey('imports.id'), primary_key=True, nullable=False)
    citizen_id = db.Column(db.Integer, primary_key=True, nullable=False)
    town = db.Column(db.String(), nullable=False)
    street = db.Column(db.String(), nullable=False)
    building = db.Column(db.String(), nullable=False)
    apartment = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(), nullable=False)
    birth_date = db.Column(db.DateTime(),nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    relatives = db.Column(db.ARRAY(db.Integer), nullable=False)
    imports = db.relationship("Imports", backref="citizens")

