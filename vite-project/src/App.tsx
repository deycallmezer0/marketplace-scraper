import { useState, useEffect } from 'react'
import axios from 'axios'
import CarList from './components/CarList'
import AddCarForm from './components/AddCarForm'
import CarDetailModal from './components/CarDetailModal'
import './App.css'
import { Car } from './types'
import { Input } from "@/components/ui/input"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

function App() {
  // State for cars, typed with an array of Car objects
  const [cars, setCars] = useState<Car[]>([]);
  const [selectedCar, setSelectedCar] = useState<Car | null>(null);
  const [isAddingCar, setIsAddingCar] = useState<boolean>(false);
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

// In App.tsx
// Modified addCar function
// Modified addCar function
const addCar = async (url: string) => {
  try {
    // Start the car addition process
    const response = await axios.post('http://localhost:5000/add_car', { url }, {
      headers: { 'Content-Type': 'application/json' }
    });
    
    const taskId = response.data.task_id;
    
    // Create a temporary loading car using the task ID
    const loadingCar = {
      id: taskId,
      url: url,
      title: 'Starting car addition...',
      price: '',
      status: 'loading',
      images: [],
      _loading_status: 'initializing',
      _loading_message: 'Starting car addition process...'
    };
    
    // Add the loading car to the list immediately
    setCars(prevCars => [loadingCar, ...prevCars]);
    
    // Start polling for updates
    pollTaskStatus(taskId);
  } catch (error) {
    console.error('Error adding car', error);
  }
};

// Improved polling function
const pollTaskStatus = async (taskId: string) => {
  const pollInterval = setInterval(async () => {
    try {
      const response = await axios.get(`http://localhost:5000/task_status/${taskId}`);
      const taskData = response.data;
      
      // Update the loading car in the cars list
      setCars(prevCars => prevCars.map(car => {
        if (car.id === taskId) {
          // Create a merged car object with the latest data from the server
          return {
            ...car,
            _loading_status: taskData.status,
            _loading_message: taskData.message,
            // Add any car_data fields that were returned
            ...(taskData.car_data || {})
          };
        }
        return car;
      }));
      
      // If the task is complete or errored, stop polling
      if (taskData.status === "complete" || taskData.status === "error") {
        clearInterval(pollInterval);
        
        // If complete, refresh the car list after a delay
        if (taskData.status === "complete") {
          setTimeout(() => {
            fetchCars();
          }, 2000);
        }
      }
    } catch (error) {
      console.error('Error polling task status', error);
      clearInterval(pollInterval);
    }
  }, 1000); // Poll every second
};
  const loadingCar: Car = {
    id: 'loading',
    url: '',
    location: '',
    images: [],
    title: 'Adding new car...',
    price: 0,
    status: 'loading',
  };
  const updateStatus = async (carId: string, status: string) => {
    try {
      await axios.post(`http://localhost:5000/update_status/${carId}`, { status });
      fetchCars();
    } catch (error) {
      console.error('Error updating status', error);
    }
  };

  const deleteCar = async (carId: string) => {
    try {
      console.log('Requesting to delete car with ID:', carId);
      await axios.post(`http://localhost:5000/delete_car/${carId}`);
      fetchCars();
    } catch (error) {
      console.error('Error deleting car', error);
    }
  };

  // Functions for handling the car detail modal
  const openCarDetail = (car: Car) => setSelectedCar(car);
  const closeCarDetail = () => setSelectedCar(null);

  return (
    
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <h1 className="text-2xl font-bold text-gray-900">Marketplace Car Helper</h1>
            <div className="flex">
              {/* Navigation items could go here */}
            </div>
          </div>
        </div>
      </header>
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="mb-8">
          <AddCarForm onAdd={addCar} />
        </div>
        
        {/* Filters and sorting options */}
        <div className="mb-6 flex justify-between items-center">
          <div className="flex gap-4">
           <Select className="w-48">
            <SelectTrigger>
              <SelectValue placeholder="Sort by" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="price">Price</SelectItem>
              <SelectItem value="location">Location</SelectItem>
              <SelectItem value="time_posted">Time Posted</SelectItem>
            </SelectContent>
          </Select>
          
          </div>
          <Input 
            type="search" 
            placeholder="Search cars..." 
            className="w-96"
            aria-label="Search cars"
          />
        </div>
        
        <CarList 
        cars={isAddingCar ? [loadingCar, ...cars] : cars} 
        onUpdateStatus={updateStatus}
        onDelete={deleteCar}
        onViewDetails={openCarDetail}
      />

        {/* Car Detail Modal */}
        {selectedCar && (
          <CarDetailModal 
            car={selectedCar} 
            onClose={closeCarDetail} 
          />
        )}
      </main>
    </div>
  );
}

export default App;