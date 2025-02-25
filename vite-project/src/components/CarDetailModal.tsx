import React from 'react';
import { Car } from '../types';

interface CarDetailModalProps {
  car: Car | null;
  onClose: () => void;
}

const CarDetailModal: React.FC<CarDetailModalProps> = ({ car, onClose }) => {
  if (!car) return null;
  
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-4 border-b sticky top-0 bg-white z-10 flex justify-between items-center">
          <h2 className="text-xl font-bold">{car.title}</h2>
          <button 
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700"
          >
            ✕
          </button>
        </div>
        
        {/* Car images gallery */}
        {car.images && car.images.length > 0 ? (
          <div className="relative h-64 bg-gray-100">
            <div className="flex overflow-x-auto h-full">
              {car.images.map((img, index) => (
            <img 
              key={index}
              src={img} 
              alt={`${car.title} - image ${index + 1}`}
              className="h-full w-auto object-cover"
            />
              ))}
            </div>
          </div>
        ) : (
          <div className="relative h-64 bg-gray-100 flex items-center justify-center">
            <p className="text-gray-500">No images available</p>
          </div>
        )}
        
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="text-lg font-semibold mb-4">Details</h3>
              <div className="space-y-2">
                <p><span className="font-medium">Price:</span> {car.price}</p>
                <p><span className="font-medium">Location:</span> {car.location}</p>
                <p><span className="font-medium">Status:</span> {car.status}</p>
                {car.time_posted && (
                  <p><span className="font-medium">Listed:</span> {car.time_posted}</p>
                )}
              </div>
            </div>
            
            <div>
              <h3 className="text-lg font-semibold mb-4">Vehicle Information</h3>
              <div className="space-y-2">
                {car.about?.mileage && (
                  <p><span className="font-medium">Mileage:</span> {car.about.mileage}</p>
                )}
                {car.about?.transmission && (
                  <p><span className="font-medium">Transmission:</span> {car.about.transmission}</p>
                )}
                {car.about?.color && (
                  <p><span className="font-medium">Color:</span> {car.about.color}</p>
                )}
                {car.about?.fuel_type && (
                  <p><span className="font-medium">Fuel Type:</span> {car.about.fuel_type}</p>
                )}
                {car.about?.mpg && (
                  <p><span className="font-medium">MPG:</span> {car.about.mpg}</p>
                )}
              </div>
            </div>
          </div>
          
          <div className="mt-6">
            <h3 className="text-lg font-semibold mb-2">Description</h3>
            <p className="text-gray-700">{car.description || "No description available."}</p>
          </div>
          
          <div className="mt-8 pt-4 border-t flex justify-end gap-3">
            <button
              onClick={() => window.open(car.url, '_blank')}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              View on Facebook
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CarDetailModal;