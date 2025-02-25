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
from sqlalchemy import Column, String, Float, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
import threading
import uuid
from flask import jsonify
Base = declarative_base()

class Car(Base):
    __tablename__ = 'cars'
    
    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    price = Column(String, nullable=False)
    location = Column(String, nullable=False)
    time_posted = Column(String, nullable=True)
    status = Column(String, nullable=False, default='Active')
    url = Column(String, nullable=False, unique=True)
    description = Column(Text, nullable=True)
    about = Column(JSON, nullable=True)
    images = Column(JSON, nullable=True)  # Add this new column
    created_at = Column(String, default=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    updated_at = Column(String, default=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    def __init__(self, id, title, price, location, status, url, mileage=None, description=None, about=None, 
                 images=None, created_at=None, updated_at=None, time_posted=None):  # Add images parameter
        self.id = id
        self.title = title
        self.price = price
        self.location = location
        self.status = status
        self.time_posted = time_posted
        self.url = url
        self.description = description
        self.about = about
        self.images = images or []  # Initialize as empty list if None
        self.created_at = created_at or datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.updated_at = updated_at or datetime.now().strftime('%Y-%m-%d %H:%M:%S')

#TODO Add AI functionality, pass the car data to the AI model, search for information about the car (e.g. mpg, reliability, etc.) and store it in the database, this can be referenced for cars added in the future with the same year, make, and model.

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
            'url': car.url,
            'description': car.description,
            'about': car.about,
            'images': car.images,
            'time_posted': car.time_posted,
        } for car in cars
    ]
    session.close()
    return jsonify({'cars': cars_list})
# Create a dictionary to store task statuses
task_statuses = {}

@app.route('/add_car', methods=['POST'])
def add_car():
    data = request.get_json()
    url = data.get('url') if data else None
    
    if not url:
        return jsonify({"error": "No URL provided"}), 400
    
    # Generate a task ID for this car addition
    task_id = str(uuid.uuid4())
    
    # Initialize the status
    task_statuses[task_id] = {
        "status": "initializing",
        "message": "Starting car addition process...",
        "car_data": None
    }
    
    # Start a background thread to process the car addition
    thread = threading.Thread(target=process_car_addition, args=(task_id, url))
    thread.start()
    
    # Return the task ID immediately
    return jsonify({"task_id": task_id}), 202

def process_car_addition(task_id, url):
    session = Session()
    try:
        # Update status: checking for duplicates
        task_statuses[task_id]["status"] = "checking"
        task_statuses[task_id]["message"] = "Checking if car already exists..."
        
        # Check if car already exists
        existing_car = session.query(Car).filter_by(url=url).first()
        if existing_car:
            task_statuses[task_id]["status"] = "error"
            task_statuses[task_id]["message"] = "This car is already in your list"
            return
        
        # Initialize car_data dictionary
        task_statuses[task_id]["car_data"] = {
            "url": url,
            "id": task_id,
            "title": "Loading...",
            "price": "",
            "location": "",
            "status": "New",
            "images": []
        }
        
        # Update status: initializing scraper
        task_statuses[task_id]["status"] = "scraper_init"
        task_statuses[task_id]["message"] = "Initializing web scraper..."
        
        # Initialize scraper
        scraper = FacebookMarketplaceScraper()
        
        # Update status: logging in
        task_statuses[task_id]["status"] = "logging_in"
        task_statuses[task_id]["message"] = "Logging in to Facebook..."
        
        if scraper.login_flow():
            # Update status: fetching data
            task_statuses[task_id]["status"] = "fetching"
            task_statuses[task_id]["message"] = "Fetching car data..."
            
            # Pass the task status to update as data is fetched
            car_data = scraper.get_marketplace_item(url, task_id, task_statuses)
            
            if car_data:
                # Update status: saving
                task_statuses[task_id]["status"] = "saving"
                task_statuses[task_id]["message"] = "Saving car to database..."
                
                car = Car(**car_data)
                session.add(car)
                session.commit()
                
                # Update status: complete
                task_statuses[task_id]["status"] = "complete"
                task_statuses[task_id]["message"] = "Car added successfully!"
            else:
                task_statuses[task_id]["status"] = "error"
                task_statuses[task_id]["message"] = "Failed to fetch car data"
        else:
            task_statuses[task_id]["status"] = "error"
            task_statuses[task_id]["message"] = "Failed to login to Facebook"
    except Exception as e:
        task_statuses[task_id]["status"] = "error"
        task_statuses[task_id]["message"] = f"Error: {str(e)}"
    finally:
        if 'scraper' in locals():
            scraper.cleanup()
        session.close()

@app.route('/task_status/<task_id>', methods=['GET'])
def get_task_status(task_id):
    if task_id in task_statuses:
        return jsonify(task_statuses[task_id])
    else:
        return jsonify({"error": "Task not found"}), 404

@app.route('/update_status/<car_id>', methods=['POST'])
def update_status(car_id):
    payload = request.get_json()
    new_status = payload.get('status')
    print(f'Received request to update status for car: {car_id} to: {new_status}')
    if not new_status:
        flash('Status cannot be empty!')
        return redirect(url_for('index'))
    
    session = Session()
    try:
        car = session.query(Car).get(car_id)
        if car:
            print(f'Updating status for car: {car_id} from {car.status} to {new_status}')
            car.status = new_status
            session.commit()
            flash('Status updated successfully!')
    finally:
        session.close()
    return redirect(url_for('index'))

@app.route('/delete_car/<car_id>', methods=['POST'])
def delete_car(car_id):
    print('Received request to delete car with ID:', car_id)
    session = Session()
    print(f'Deleting car: {car_id}')
    car = session.query(Car).get(car_id)
    print(f'Deleting car: {car_id}')
    if car:
        session.delete(car)
        session.commit()
        flash('Car deleted successfully!')
    session.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)