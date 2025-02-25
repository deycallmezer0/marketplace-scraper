import { Car } from '../types';

// Extend the Car type to include loading state properties
interface LoadingCar extends Car {
  _loading_status?: string;
  _loading_message?: string;
}

interface CarListProps {
  cars: (Car | LoadingCar)[];
  onUpdateStatus: (carId: string, status: string) => void;
  onDelete: (carId: string) => void;
  onViewDetails: (car: Car) => void;
}

const CarList: React.FC<CarListProps> = ({ cars, onUpdateStatus, onDelete, onViewDetails }) => {
  if (!cars) {
    return <div className="flex justify-center p-8"><div className="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-blue-500"></div></div>;
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {cars.length === 0 ? (
        <p className="col-span-full text-center text-gray-500 py-8">No cars found</p>
      ) : (
        cars.map((car) => {
          // Check if this is a loading car
          const isLoading = '_loading_status' in car;
          
          if (isLoading) {
            const loadingCar = car as LoadingCar;
            
            return (
              <div key={car.id} className="bg-white rounded-lg shadow overflow-hidden hover:shadow-md transition-shadow">
                <div className="h-48 bg-gray-200 flex items-center justify-center">
                  {loadingCar.images && loadingCar.images.length > 0 ? (
                    <img 
                      src={loadingCar.images[0]} 
                      alt="Car preview" 
                      className="w-full h-full object-cover opacity-70"
                    />
                  ) : (
                    <div className="animate-pulse flex space-x-2">
                      <svg className="w-10 h-10 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 8l-7 7-7-7"></path>
                      </svg>
                      <span className="text-gray-400 text-lg">Loading image...</span>
                    </div>
                  )}
                </div>
                
                <div className="p-4">
                  <div className="flex justify-between items-start">
                    <h3 className="text-lg font-semibold text-gray-900 truncate">
                      {loadingCar.title || 'Adding new car...'}
                    </h3>
                    <span className="px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800 animate-pulse">
                      {loadingCar._loading_status || 'Processing...'}
                    </span>
                  </div>
                  
                  {loadingCar.price ? (
                    <p className="text-xl font-bold text-gray-900 mt-2">{loadingCar.price}</p>
                  ) : (
                    <div className="h-7 bg-gray-200 rounded mt-2 w-24 animate-pulse"></div>
                  )}
                  
                  {loadingCar.location ? (
                    <p className="text-sm text-gray-500">{loadingCar.location}</p>
                  ) : (
                    <div className="h-4 bg-gray-200 rounded mt-2 w-32 animate-pulse"></div>
                  )}
                  
                  <div className="mt-4 pt-4 border-t border-gray-100">
                    <div className="text-sm text-gray-600">
                      {loadingCar._loading_message || 'Fetching car details...'}
                    </div>
                    
                    <div className="w-full bg-gray-200 rounded-full h-2.5 mt-2">
                      <div 
                        className="bg-blue-600 h-2.5 rounded-full animate-pulse" 
                        style={{ 
                          width: loadingCar._loading_status === 'complete' ? '100%' : '60%' 
                        }}
                      ></div>
                    </div>
                  </div>
                </div>
              </div>
            );
          }
          
          // Regular car card (your existing code)
          return (
            <div key={car.id} className="bg-white rounded-lg shadow overflow-hidden hover:shadow-md transition-shadow">
              {car.images && car.images.length > 0 && (
                <div 
                  className="h-48 bg-gray-200 overflow-hidden cursor-pointer"
                  onClick={() => onViewDetails(car)}
                >
                  <img 
                    src={car.images[0]} 
                    alt={car.title} 
                    className="w-full h-full object-cover"
                  />
                </div>
              )}
              <div className="p-4">
                <div className="flex justify-between items-start">
                  <h3 
                    className="text-lg font-semibold text-gray-900 truncate cursor-pointer"
                    onClick={() => onViewDetails(car)}
                  >
                    {car.title}
                  </h3>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(car.status)}`}>
                    {car.status}
                  </span>
                </div>
                <p className="text-xl font-bold text-gray-900 mt-2">{car.price}</p>
                <p className="text-sm text-gray-500">{car.location}</p>
                
                {car.about?.mileage && (
                  <p className="text-sm text-gray-700 mt-2">{car.about.mileage}</p>
                )}
                
                <div className="mt-4 pt-4 border-t border-gray-100 flex justify-between">
                  <select
                    className="rounded-md border-gray-300 shadow-sm text-sm"
                    value={car.status}
                    onChange={(e) => onUpdateStatus(car.id, e.target.value)}
                  >
                    <option value="new">New</option>
                    <option value="contacted">Contacted</option>
                    <option value="viewed">Viewed</option>
                    <option value="negotiating">Negotiating</option>
                    <option value="completed">Completed</option>
                  </select>
                  <div className="flex gap-2">
                    <button 
                      className="text-sm px-3 py-1 bg-blue-50 text-blue-600 rounded hover:bg-blue-100"
                      onClick={() => onViewDetails(car)}
                    >
                      Details
                    </button>
                    <button 
                      className="text-sm px-3 py-1 bg-blue-50 text-blue-600 rounded hover:bg-blue-100"
                      onClick={() => window.open(car.url, '_blank')}
                    >
                      View
                    </button>
                    <button 
                      className="text-sm px-3 py-1 bg-red-50 text-red-600 rounded hover:bg-red-100"
                      onClick={() => confirmDelete(car.id)}
                    >
                      Delete
                    </button>
                  </div>
                </div>
              </div>
            </div>
          );
        })
      )}
    </div>
  );
  
  // Helper functions
  function getStatusColor(status: string) {
    switch(status) {
      case 'new': return 'bg-blue-100 text-blue-800';
      case 'contacted': return 'bg-yellow-100 text-yellow-800';
      case 'viewed': return 'bg-purple-100 text-purple-800';
      case 'negotiating': return 'bg-green-100 text-green-800';
      case 'completed': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  }
  
  function confirmDelete(carId: string) {
    if (window.confirm('Are you sure you want to delete this car?')) {
      onDelete(carId);
    }
  }
};

export default CarList;