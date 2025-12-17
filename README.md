# CineSync - Movie Booking Platform

A modern movie booking web application built with Flask and CockroachDB. CineSync allows users to browse movies, select showtimes, choose seats, and complete bookings seamlessly.

## Features

- **Browse Movies**: View all available movies with filters by type, language, and rating
- **Theater Listings**: Find theaters in different cities with detailed information
- **Showtime Selection**: Select from available showtimes for movies at specific theaters
- **Interactive Seat Selection**: Visual seat map showing available and booked seats
- **Booking Management**: Complete booking flow with confirmation and history
- **User Authentication**: Simple session-based login/registration system
- **Responsive Design**: Mobile-friendly interface built with Bootstrap 5

## Technology Stack

- **Backend**: Flask (Python)
- **Database**: CockroachDB (PostgreSQL-compatible)
- **ORM**: SQLAlchemy
- **Frontend**: Bootstrap 5, Vanilla JavaScript
- **Session Management**: Flask Sessions

## Project Structure

```
cinesync/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── config.py            # Configuration classes
│   ├── extensions.py        # Database extensions
│   ├── models/              # SQLAlchemy models
│   ├── routes/              # Blueprint routes
│   ├── services/            # Business logic layer
│   ├── templates/           # Jinja2 templates
│   └── static/              # CSS, JavaScript, images
├── requirements.txt         # Python dependencies
├── run.py                   # Application entry point
├── .env                     # Environment variables (create from .env.example)
└── README.md               # This file
```

## Prerequisites

- Python 3.8 or higher
- CockroachDB cluster (running and accessible)
- Existing database named `cinesync` with populated tables

## Installation

1. **Clone the repository** (or navigate to the project directory)

   ```bash
   cd cinesync
   ```

2. **Create a virtual environment**

   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**

   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

5. **Configure environment variables**

   Create a `.env` file in the root directory based on `.env.example`:

   ```bash
   cp .env.example .env
   ```

   Edit `.env` and update with your settings:

   ```
   SECRET_KEY=your-secret-key-here
   DATABASE_URL=cockroachdb://user:password@host:26257/cinesync?sslmode=verify-full
   FLASK_ENV=development
   ```

## Database Schema

The application expects the following tables to exist in your CockroachDB database:

- **events**: Movie/event information
- **theaters**: Theater locations and details
- **customers_local**: Customer accounts
- **auditoriums**: Theater auditoriums/screens
- **seats**: Seat information for auditoriums
- **shows**: Showtimes linking events to auditoriums
- **bookings**: Customer bookings
- **booking_seats**: Junction table for booking-seat relationships

**Note**: This application does NOT create or migrate tables. All tables must exist with data before running.

## Running the Application

1. **Ensure your CockroachDB cluster is running**

2. **Start the Flask development server**

   ```bash
   python run.py
   ```

   The application will start on `http://localhost:5000`

3. **Access the application**

   Open your web browser and navigate to:
   ```
   http://localhost:5000
   ```

## Usage

### For Customers

1. **Browse Movies**: Visit the homepage or click "Movies" to see all available movies
2. **Filter Movies**: Use filters to find movies by type, language, or rating
3. **View Movie Details**: Click on a movie to see details and available showtimes
4. **Select Showtime**: Choose a date and theater to see available showtimes
5. **Choose Seats**: Select your preferred seats from the interactive seat map
6. **Login/Register**: Create an account or login to complete booking
7. **Confirm Booking**: Review your selection and confirm the booking
8. **View History**: Check your profile to see all past bookings

### For Theaters

- Browse all theaters
- Filter by city
- View theater details including auditoriums
- See today's showtimes

## API Structure

### Routes

- **Main Routes** (`/`)
  - `GET /` - Homepage with featured movies
  - `GET /search` - Search movies and theaters

- **Event Routes** (`/events`)
  - `GET /events` - List all movies with filters
  - `GET /events/<event_id>` - Movie details

- **Theater Routes** (`/theaters`)
  - `GET /theaters` - List all theaters
  - `GET /theaters/<theater_id>` - Theater details

- **Show Routes** (`/shows`)
  - `GET /shows/select` - Select showtime

- **Booking Routes** (`/bookings`)
  - `GET /bookings/seats` - Seat selection
  - `POST /bookings/confirm` - Confirm booking
  - `POST /bookings/create` - Create booking
  - `GET /bookings/success/<booking_id>` - Booking confirmation

- **Customer Routes** (`/customers`)
  - `GET/POST /customers/login` - Login
  - `GET/POST /customers/register` - Register
  - `GET /customers/logout` - Logout
  - `GET /customers/profile` - Profile and booking history

## Service Layer

The application uses a service layer for business logic:

- **EventService**: Movie/event operations
- **TheaterService**: Theater and auditorium operations
- **ShowService**: Showtime queries and filtering
- **SeatService**: Seat availability and selection
- **BookingService**: Booking creation and management

## Database Connection

The application uses SQLAlchemy with the `psycopg2` driver for CockroachDB connectivity. Connection parameters are configured via the `DATABASE_URL` environment variable.

### Connection String Format

```
cockroachdb://username:password@host:port/database?sslmode=verify-full
```

For local development without SSL:
```
cockroachdb://root@localhost:26257/cinesync?sslmode=disable
```

## Important Notes

- **No Migrations**: This application does not create or modify database tables. All schema must exist before running.
- **Session-Based Auth**: Authentication uses Flask sessions, not password hashing (suitable for demo/development)
- **Geography Columns**: The `geog` columns in theaters and customers are stored as strings. Advanced geographic queries are not implemented.
- **Composite Primary Key**: The `shows` table uses a composite primary key (show_id, event_id)

## Development

### Adding New Features

1. **Models**: Add/modify models in `app/models/`
2. **Services**: Add business logic in `app/services/`
3. **Routes**: Add endpoints in `app/routes/`
4. **Templates**: Add HTML templates in `app/templates/`
5. **Static Files**: Add CSS/JS in `app/static/`

### Code Organization

- Keep business logic in service layer
- Use blueprints for route organization
- Follow Flask best practices
- Use Jinja2 template inheritance

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Verify CockroachDB is running
   - Check DATABASE_URL in `.env`
   - Ensure database exists and has data

2. **Import Errors**
   - Activate virtual environment
   - Install all requirements: `pip install -r requirements.txt`

3. **Template Not Found**
   - Verify template files exist in correct directories
   - Check template names in route handlers

4. **Session Issues**
   - Set a proper SECRET_KEY in `.env`
   - Clear browser cookies

## Security Considerations

⚠️ **This is a development/demo application. For production use:**

- Implement proper password hashing (bcrypt, argon2)
- Add CSRF protection
- Use HTTPS/SSL
- Implement rate limiting
- Add input validation and sanitization
- Use prepared statements (already done via SQLAlchemy)
- Add proper error handling
- Implement logging and monitoring

## License

This project is created for educational/demonstration purposes.

## Support

For issues or questions, please check:
- CockroachDB documentation: https://www.cockroachlabs.com/docs/
- Flask documentation: https://flask.palletsprojects.com/
- SQLAlchemy documentation: https://docs.sqlalchemy.org/

## Contributors

Built with Flask, CockroachDB, and Bootstrap 5.
