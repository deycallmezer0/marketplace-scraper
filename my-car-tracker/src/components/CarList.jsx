function CarList({ cars, onUpdateStatus, onDelete }) {
    if (!cars) {
      return <div>Loading...</div>
    }
  
    return (
      <div className="car-list">
        {cars.length === 0 ? (
          <p>No cars found</p>
        ) : (
          cars.map(car => (
            <div key={car.id} className="car-item">
              <h3>{car.title}</h3>
              <p>Price: ${car.price}</p>
              <p>Location: {car.location}</p>
              <select
                value={car.status}
                onChange={(e) => onUpdateStatus(car.id, e.target.value)}
              >
                <option value="new">New</option>
                <option value="contacted">Contacted</option>
                <option value="viewed">Viewed</option>
                <option value="negotiating">Negotiating</option>
                <option value="completed">Completed</option>
              </select>
              <button onClick={() => onDelete(car.id)}>Delete</button>
            </div>
          ))
        )}
      </div>
    )
  }
  
  export default CarList