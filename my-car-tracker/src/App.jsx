import { useState, useEffect } from 'react'
import axios from 'axios'
import CarList from './components/CarList'
import AddCarForm from './components/AddCarForm'
import './App.css'

function App() {
  const [cars, setCars] = useState([])

  useEffect(() => {
    fetchCars()
  }, [])

  const fetchCars = async () => {
    try {
      const response = await axios.get('http://localhost:5000/')
      setCars(response.data.cars)
    } catch (error) {
      console.error('Error fetching cars:', error)
    }
  }

  const addCar = async (url) => {
    try {
      await axios.post('http://localhost:5000/add_car', { url }, {
        headers: { 'Content-Type': 'application/json' }
      })
      fetchCars()
    } catch (error) {
      console.error('Error adding car:', error)
    }
  }

  const updateStatus = async (carId, status) => {
    try {
      await axios.post(`http://localhost:5000/update_status/${carId}`, { status })
      fetchCars()
    } catch (error) {
      console.error('Error updating status:', error)
    }
  }

  const deleteCar = async (carId) => {
    try {
      await axios.post(`http://localhost:5000/delete_car/${carId}`)
      fetchCars()
    } catch (error) {
      console.error('Error deleting car:', error)
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
  )
}

export default App