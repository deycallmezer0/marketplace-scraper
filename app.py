# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_cors import CORS
import os
import selenium
from selenium import webdriver
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Car
from scraper import FacebookMarketplaceScraper
import threading
import os
import json
import random
import time
from datetime import datetime
from dotenv import load_dotenv
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

load_dotenv()

app = Flask(__name__)
CORS(app)  # Add this line after creating the Flask app
app.secret_key = 'your-secret-key'  # Change this in production

# Database setup
engine = create_engine('sqlite:///cars.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

@app.route('/')
def index():
    session = Session()
    cars = session.query(Car).order_by(Car.created_at.desc()).all()
    cars_list = [
        {
            'id': car.id,
            'title': car.title,
            'price': car.price,
            'location': car.location,
            'status': car.status,
            'url': car.url
        } for car in cars
    ]
    session.close()
    return jsonify({'cars': cars_list})
@app.route('/add_car', methods=['POST'])
def add_car():
    data = request.get_json()  # Change this line
    url = data.get('url') if data else None  # And this line
    print(f'Received URL: {url}')
    
    if not url:
        print('No URL provided')
        flash('Please provide a URL')
        return redirect(url_for('index'))
    
    session = Session()
    print('Adding car...')
    
    # Check if car already exists
    existing_car = session.query(Car).filter_by(url=url).first()
    if existing_car:
        print(f'Car already exists: {url}')  # Add this
        flash('This car is already in your list')
        return redirect(url_for('index'))
    
    # Initialize scraper and get car data
    print('Initializing scraper...')
    scraper = FacebookMarketplaceScraper()
    try:
        print('Starting login flow...')  # Add this
        if scraper.login_flow():
            print('Logged in successfully!')
            print(f'Fetching car data for URL: {url}')  # Add this
            car_data = scraper.get_marketplace_item(url)
            if car_data:
                print(f'Successfully retrieved car data: {car_data}')  # Add this
                car = Car(**car_data)
                session.add(car)
                session.commit()
                flash('Car added successfully!')
            else:
                print('Failed to fetch car data')  # Add this
                flash('Failed to fetch car data')
        else:
            print('Failed to login to Facebook')  # Add this
            flash('Failed to login to Facebook')
    except Exception as e:
        print(f'Error occurred: {str(e)}')  # Add this
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