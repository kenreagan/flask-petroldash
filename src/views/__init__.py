from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, send_file, abort
from src.models import  Staff, fueltypes, FuelBaseClass, Station
from flask_login import login_required, login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
import sqlite3
from functools import wraps
from src import db
import datetime
from typing import Optional, Callable, Text

user = Blueprint('application', __name__, template_folder='../templates/', static_folder='../static/')


def admins_only(func):
    @wraps(func)
    def is_admin(*args, **kwargs):
        if current_user.is_authenticated and current_user.is_admin:
            return func(*args, **kwargs)
        return redirect(url_for('application.home'))
    return is_admin

@user.route('/add/record/', methods=['POST'])
def add_record():
	Fuel_type = request.form.get('name')
	fuel_name = fueltypes.query.filter_by(fuel_name=Fuel_type).first()
	assert fuel_name != None	
	cash = request.form.get('cash')
	litres = request.form.get('litres')
	manual = request.form.get('manual')
	dips = request.form.get('dips')
	pic = request.files['picture']
	pic.save(os.path.join(current_app.config['UPLOAD_FOLDER'], pic.filename))
	record = FuelBaseClass(sales=cash, dips=dips, litres=litres, manual=manual, photo=pic.filename, fuel_type=fuel_name.id, staff_recorded=current_user.id)
	record.save()
	flash('recorded success', 'danger')
	return redirect(url_for('application.home'))
	
@user.route('/get/records/<int:id>', methods=['GET'])
def get_staff_records(id):
    tod = datetime.datetime.today()
    staff_feed = FuelBaseClass.query.filter_by(staff_recorded=id).filter(FuelBaseClass.date_recorded > datetime.date(day=tod.day-1, month=tod.month, year=tod.year)).filter(FuelBaseClass.date_recorded <= datetime.date(day=tod.day, month=tod.month, year=tod.year)).all()
    rec = []
    for x in staff_feed:
        rec.append(x.to_json())
    return {
            'rec': rec
            }

@user.route('/get/details/<int:id>')
def get_detail(id):
    record = FuelBaseClass.query.filter_by(id=id).first()
    return record.to_json()

@user.route('/login/<stationid>', methods=['GET', 'POST'])
def login(stationid: int):
    if current_user.is_authenticated:
        return redirect(url_for('application.home'))
    if request.method == 'POST':
        staff_id = request.form.get('staffid')
        password = request.form.get('password')
        staff = Staff.query.filter_by(staff_id=staff_id).first()
        if staff:
            if staff.station_id == int(stationid):
                if check_password_hash(staff.password, password):
                    login_user(staff)
                    return redirect(url_for('application.home'))
                flash('wrong credential input the correct ones', 'danger')
                return redirect(url_for('application.login', stationid=stationid))
            flash('Staff Does not Belong to this station, Make sure you login to your Station', 'danger')
            return redirect(url_for('application.login', stationid=stationid))
        flash('user with this staff id does not exists does not exist', 'danger')
        return redirect(url_for('application.login', stationid=stationid))
    return render_template('auth/login.html')

@user.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('application.home'))
	
    if request.method == 'POST':
        staff_id = request.form.get('staffid')
        password = request.form.get('password')
        staff = Staff(staff_id=staff_id, password=generate_password_hash(password, method='sha256'))
        staff.save()
        flash('Account creation success now login', 'success')
        return redirect(url_for('application.login'))
    return render_template('auth/register.html')

@user.route('/logout')
@login_required
def logout():
    if current_user.is_authenticated:
        logout_user()
        return redirect(url_for('application.home'))
    return redirect(url_for('application.home'))

import base64
import pandas as pd
from sqlalchemy import func, and_

tod = datetime.datetime.today()
conn = sqlite3.connect('./main.sqlite')
dataframe: pd.DataFrame = pd.read_sql('SELECT * FROM fuel_base_class', conn)
dataframe['date_recorded'] = pd.to_datetime(dataframe['date_recorded'])
tdy: pd.DataFrame = dataframe.loc[dataframe['date_recorded'].dt.day == tod.day]
monthlysales: int = dataframe.loc[(dataframe['date_recorded'].dt.month == tod.month)&(dataframe['date_recorded'].dt.year == tod.year)]
yearsum:pd.DataFrame = dataframe.loc[dataframe['date_recorded'].dt.year == tod.year]

@user.route('/home', methods=['GET'])
def home():
    fuel = fueltypes.query.all()
    station = Station.query.all()
    return render_template('home.html', fuel=fuel, station=station, tdy=tdy, sales=tdy['sales'].sum(), monthly_sales=monthlysales['sales'].sum(), yearsum=yearsum['sales'].sum())

@user.route('/admin')
@admins_only
def admin_home(): 
    flbase = FuelBaseClass.query.filter(func.date(FuelBaseClass.date_recorded) == datetime.date.today()).all()
    return render_template('adminbase.html', flbase=flbase, tdy=tdy, sales=tdy['sales'].sum(), monthly_sales=monthlysales['sales'].sum(),yearsum=yearsum['sales'].sum())

@user.route('get/monthly/sales')
@admins_only
def monthly_sales():
    now = datetime.datetime.utcnow()
    one_month =now - datetime.timedelta(days=20)
    flbase = FuelBaseClass.query.filter(FuelBaseClass.date_recorded > one_month).all()
    return render_template('monthlysales.html', yeartot=yearsum, yearsum=yearsum['sales'].sum(), monthly_sales=monthlysales['sales'].sum(), flbase=flbase, sales=tdy['sales'].sum(), tdy=tdy)


@user.route('manage/staff')
@admins_only
def manage_staff():
    staff = Staff.query.all()
    station = Station.query.all()
    flbase = FuelBaseClass.query.order_by(FuelBaseClass.date_recorded.desc()).all()
    return render_template('staff.html', staff=staff, yeartot=yearsum, yearsum=yearsum['sales'].sum(), monthly_sales=monthlysales['sales'].sum(), flbase=flbase, sales=tdy['sales'].sum(), tdy=tdy, station=station)


@user.route('delete/staff/<staffid>', methods=['POST'])
@admins_only
def delete_user(staffid):
    staff = Staff.query.filter_by(staff_id=staffid).first()
    staff.delete()
    flash('user delete success', 'danger')
    return redirect(url_for('application.manage_staff'))

@user.route('add/user/', methods=['POST'])
@admins_only
def add_user():
    staff_name: str = request.form.get('staffname')
    password: str = request.form.get('password')
    staff_id: int = int(request.form.get('staffid'))
    station_id: int = int(request.form.get('stationid'))
    client = Staff(staff_name=staff_name, staff_id=staff_id, password=generate_password_hash(password, method='sha256'), station_id=station_id)
    client.save()
    flash('user created successfully', 'danger')
    return redirect(url_for('application.manage_staff'))

@user.route('delete/record/<int:id>')
@admins_only
def delete_record(id):
    fuel_class = FuelBaseClass.query.filter(FuelBaseClass.id==id).first()
    fuel_class.delete()
    flash('Record successfully deleted', 'success')
    return redirect(url_for('application.admin_home'))


@user.route('update/record/<int:id>', methods=['POST'])
@admins_only
def update_record(id):
    record = FuelBaseClass.query.filter_by(id=id).first()
    data = request.get_json()
    record.sales = data['sales']
    record.litres = data['litres']
    record.manual = data['manual']
    record.dips = data['dips']
    db.session.commit()
    return {
		"Status": 200
	}
	
@user.route('/analysis/section/', methods=['GET'])
@admins_only
def analysis():
    connection = sqlite3.connect('./main.sqlite')
    dataframe = pd.read_sql('SELECT * FROM fuel_base_class', connection, parse_dates=['date_recorded'], index_col=['date_recorded'])
    connection.close()
    flbase = FuelBaseClass.query.order_by(FuelBaseClass.date_recorded.desc()).all()
    y = dataframe.groupby([lambda x: x.year, lambda x: x.month]).sum()
    tod = datetime.datetime.today()
    return render_template('analysis.html', yeartot=yearsum, yearsum=yearsum['sales'].sum(), monthly_sales=monthlysales['sales'].sum(), flbase=flbase, sales=tdy['sales'].sum(), tdy=tdy['sales'], dataframe=dataframe, y=y)

@user.route('/get/report/')
@admins_only
def get_report():
    try:
        connection = sqlite3.connect('./main.sqlite')
        filename: Optional[str] = 'main.xlsx'
        filepath = os.path.join(os.getcwd(), filename)
        dataframe = pd.read_sql('SELECT * FROM fuel_base_class', connection, parse_dates=['date_recorded'])
        today = datetime.datetime.today()
        dataframe.loc[dataframe['date_recorded'].dt.day == today.day].to_excel(filepath)
    except:
        abort(500)
        flash('An error occured while fetching the file, please contact the developer.','danger')
    finally:
        connection.close()
        return send_file(filepath)
