import { useState, useEffect } from 'react'
import axios from 'axios'
import CarList from './components/CarList'
import AddCarForm from './components/AddCarForm'
import './App.css'

interface Car {
  id: string;
  title: string;
  price: number;
  location: string;
  status: string;
}
function App() {
  // State for cars, typed with an array of Car objects
  const [cars, setCars] = useState<Car[]>([]);

  useEffect(() => {
    fetchCars();
  }, []);

  // Function to fetch cars from the API
  const fetchCars = async () => {
    try {
      const response = await axios.get<{ cars: Car[]} >('http://localhost:5000/');
      setCars(response.data.cars);
    } catch (error) {
      console.error('Error fetching cars', error);
    }
    };

    // Function to add a car to the API
    const addCar = async (url: string) => {
      try {
        await axios.post('http://localhost:5000/add_car', { url},{
          headers: { 'Content-Type': 'application/json'}
        });
        fetchCars();
      } catch (error) {
        console.error('Error adding car', error);
      }
    };

    const updateStatus = async (carId: string, status: string) => {
      try {
        await axios.post('http://localhost:5000/update_status/${carId}', { status });
        fetchCars();
      } catch (error) {
        console.error('Error updating status', error);
      }
    };

    const deleteCar = async (carId: string) => {
      try {
        await axios.post('http://localhost:5000/delete_car/${carId}');
        fetchCars();
      } catch (error) {
        console.error('Error deleting car', error);
      }
    }

    return (
      <div className="App">
        <h1>Car Tracker</h1>
        <AddCarForm onAdd={addCar} />
        <CarList 
          cars={cars} 
          onUpdateStatus={updateStatus}
          onDelete={deleteCar}
        />
      </div>
    );
  }
  
  export default App;