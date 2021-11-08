import datetime
from typing import Any, Text, Iterable
from src import db, login_manager
from flask_login import UserMixin


class DatabaseMixin(object):
	__table_args__ = {'extend_existing': True}
	
	@classmethod
	def create(cls, **kwargs):
		objinstance = cls(**kwargs)
		return objinstance.save()
	
	def save(self, commit=True, **kwargs):
		if kwargs is not None:
			db.session.add(self)
			return self and db.session.commit()
		return NotImplementedError
		
	def update(self, commit=True, **kwargs):
		for key, value in kwargs:
			setattr(self, key, value)
		return self.save() and db.session.commit()
	
	def delete(self, commit=True, **kwargs):
		if kwargs is not None:
			db.session.delete(self)
			return self and db.session.commit()
		return NotImplementedError
		

class StaffMixin(object):
	__table_args__ = {'extend_existing': True}
	
	is_login = db.Column(db.Boolean, nullable=False, default=False)
	
	def __call__(self, classname, bases, attrs)->None:
		staff_id = attrs['staff_id']
		if staff_id is not None:
			print(staff_id)
	
	@classmethod
	def create(cls, **kwargs):
		objinstance = cls(**kwargs)
		return objinstance.save()
	
	def save(self, commit=True, **kwargs):
		if kwargs is not None:
			db.session.add(self)
			return self and db.session.commit()
		return NotImplementedError
		
	def update(self, commit=True, **kwargs):
		for key, value in kwargs.iteritems():
			setattr(self, key, value)
		return self.save() and db.session.commit()
	
	def delete(self, commit=True, **kwargs):
		if kwargs is not None:
			db.session.delete(self)
			return self and db.session.commit()
		return NotImplementedError    
        
class Expenses(DatabaseMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	expenses_name = db.Column(db.String(200), nullable=False)
	date_recorded = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
	amount = db.Column(db.Float, nullable=False)
	
	
	def __repr__(self):
		return '[%s : %.2f]'%(self.expenses_name, self.amount)


class FuelBaseClass(DatabaseMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_recorded = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    sales = db.Column(db.Float, nullable=False)
    dips = db.Column(db.Float, nullable=False)
    litres = db.Column(db.Float, nullable=False)
    manual = db.Column(db.Integer, nullable=False)
    photo = db.Column(db.String(200), nullable=False)
    open_stock = db.Column(db.Boolean, nullable=False, default=False)
    fuel_type = db.Column(db.Integer, db.ForeignKey('fueltypes.id'))
    staff_recorded = db.Column(db.Integer, db.ForeignKey('staff.id'))

    def __repr__(self):
        return '[sales : %d]'%self.sales
        
    def __lt__(self, other):
        if self.__class__ == other.__class__:
            return self.sales < other.sales
        raise NotImplementedError

    def __eq__(self, other):
        if self.__class__ == other.__class__:
            return self.sales == other.sales
        raise NotImplementedError

    def __gt__(self, other):
        if self.__class__ == other.__class__:
            return self.sales > other.sales
        raise NotImplementedError
    
    def to_json(self):
        return {
            'Sales': self.sales,
            'litres': self.litres,
            'manual': self.manual,
            'staff recorded': self.staff_recorded,
            'dips':self.dips,
            'fuel name':self.fuel.fuel_name
        }

class fueltypes(DatabaseMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fuel_name = db.Column(db.String(200), nullable=False)
    dips_refered = db.relationship('FuelBaseClass', lazy='dynamic', backref='fuel', cascade='all, delete')


    def _repr__(self):
        return '[fuel name : %s]'%self.fuel_name

    def to_json(self):
        return {
                "fuel name": self.fuel_name
                }

class Staff(StaffMixin, UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    staff_name = db.Column(db.String(200), nullable=False)
    staff_id = db.Column(db.Integer, nullable=False)
    password=db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    station_id = db.Column(db.Integer, db.ForeignKey('station.id'))
    return_filed = db.relationship('FuelBaseClass', lazy='dynamic', backref='records', overlaps="dips_refered,fuel")
    

    def __repr__(self):
        return '[staff id: %s]'%self.staff_id

    def to_json(self):
        return {
                "staff_id":self.staff_id,
                "is admin": self.is_admin
                }
   
    @login_manager.user_loader
    def load_user(id):
        return Staff.query.get(int(id))


class Station(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    station_name = db.Column(db.String(250), nullable=False)
    dips_refered = db.relationship('Staff', lazy='dynamic', backref='station', cascade='all, delete')

    def __repr__(self):
        return '[%s]'%self.station_name

