
# Facebook Marketplace Car Tracker

A web application to help track and manage vehicle listings from Facebook Marketplace. This tool allows you to save interesting car listings, monitor their status, and manage your car-buying journey.

## Features

- Save car listings from Facebook Marketplace
- Automatically extract key information:
  - Title
  - Price
  - Location
  - Mileage
  - Full description
- Track listing status:
  - Interested
  - Contacted
  - Viewed
  - Rejected
- View original listings directly on Facebook
- Manage all saved listings in one place

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd marketplace-scraper
```

2. Install required packages:
```bash
pip install flask sqlalchemy selenium webdriver-manager python-dotenv
```

## First-Time Setup

1. Run the application:
```bash
python app.py
```

2. When prompted, log into Facebook in the automated browser window
3. After successfully logging in, return to the terminal and press Enter
4. The application will save your login session for future use

## Usage

1. Start the application:
```bash
python app.py
```

2. Open your browser and navigate to: `http://localhost:5000`

3. To add a new listing:
   - Copy the URL of a Facebook Marketplace car listing
   - Paste it into the "Add New Car" input field
   - Click "Add Car"

4. Managing listings:
   - Update status using the dropdown menu
   - View full descriptions by clicking "Show Description"
   - Delete listings you're no longer interested in
   - Click "View on Facebook" to see the original listing

## Technical Details

- Backend: Flask and SQLAlchemy
- Database: SQLite (local storage)
- Web Scraping: Selenium with Chrome WebDriver
- Frontend: Bootstrap 5

## Future Improvements

- [ ] Price history tracking
- [ ] Email notifications for price changes
- [ ] Image saving
- [ ] Advanced filtering and sorting
- [ ] Notes and comments for each listing
- [ ] Multiple user support
- [ ] Automated availability checking

## Contributing

Feel free to fork the repository and submit pull requests for any improvements you'd like to add.

## License

[Your chosen license]

## Disclaimer

This tool is for personal use only. Please ensure you comply with Facebook's terms of service and respect website scraping guidelines.
```

