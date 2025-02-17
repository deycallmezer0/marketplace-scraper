# app.py
from flask import Flask, render_template, request, redirect, url_for, flash
import os
import selenium
from selenium import webdriver
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Car
from scraper import FacebookMarketplaceScraper
import threading

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Change this in production

# Database setup
engine = create_engine('sqlite:///cars.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

@app.route('/')
def index():
    session = Session()
    cars = session.query(Car).order_by(Car.created_at.desc()).all()
    session.close()
    return render_template('index.html', cars=cars)

@app.route('/add_car', methods=['POST'])
def add_car():
    url = request.form.get('url')
    if not url:
        flash('Please provide a URL')
        return redirect(url_for('index'))
    
    session = Session()
    
    # Check if car already exists
    existing_car = session.query(Car).filter_by(url=url).first()
    if existing_car:
        flash('This car is already in your list')
        return redirect(url_for('index'))
    
    # Initialize scraper and get car data
    scraper = FacebookMarketplaceScraper()
    try:
        if scraper.login_flow():
            car_data = scraper.get_marketplace_item(url)
            if car_data:
                car = Car(**car_data)
                session.add(car)
                session.commit()
                flash('Car added successfully!')
            else:
                flash('Failed to fetch car data')
        else:
            flash('Failed to login to Facebook')
    except Exception as e:
        flash(f'Error: {str(e)}')
    finally:
        scraper.cleanup()
        session.close()
    
    return redirect(url_for('index'))

@app.route('/update_status/<int:car_id>', methods=['POST'])
def update_status(car_id):
    new_status = request.form.get('status')
    session = Session()
    car = session.query(Car).get(car_id)
    if car:
        car.status = new_status
        session.commit()
        flash('Status updated successfully!')
    session.close()
    return redirect(url_for('index'))

@app.route('/delete_car/<int:car_id>', methods=['POST'])
def delete_car(car_id):
    session = Session()
    car = session.query(Car).get(car_id)
    if car:
        session.delete(car)
        session.commit()
        flash('Car deleted successfully!')
    session.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)