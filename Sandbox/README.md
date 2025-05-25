# Print MIS - Management Information System for Commercial Printing

A comprehensive system to manage the operations of a commercial printing company, including:
- Order Entry and Customer Management
- Production Planning and Tracking
- Job Scheduling and Workflow Management
- Inventory Management
- Invoicing and Financial Reporting

## Features

### Order Entry
- Customer information management
- Quote generation
- Order specification and requirements
- File upload and management
- Job approval workflow

### Production Management
- Job scheduling
- Production workflow tracking
- Resource allocation
- Machine scheduling
- Quality control checkpoints

### Invoicing
- Quote to invoice conversion
- Partial and final invoicing
- Payment tracking
- Financial reporting

## Technical Stack
- Backend: Python with Flask
- Database: SQLite (development) / PostgreSQL (production)
- Frontend: HTML, CSS, JavaScript with Bootstrap

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git
- PostgreSQL (for production)

## Installation

### Quick Setup

#### For Unix/Linux/MacOS:
```bash
# Clone the repository
git clone https://github.com/yourusername/print-mis.git
cd print-mis

# Run setup script
chmod +x setup.sh
./setup.sh
```

#### For Windows:
```batch
# Clone the repository
git clone https://github.com/yourusername/print-mis.git
cd print-mis

# Run setup script
setup.bat
```

### Manual Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/print-mis.git
   cd print-mis
   ```

2. Create and activate virtual environment:
   ```bash
   # Unix/Linux/MacOS
   python3 -m venv venv
   source venv/bin/activate

   # Windows
   python -m venv venv
   venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. Initialize the database:
   ```bash
   flask init_db
   ```

6. (Optional) Create demo data:
   ```bash
   flask demo_data
   ```

## Configuration

### Development
- Uses SQLite database by default
- Debug mode enabled
- File uploads stored locally

### Production
- Configure PostgreSQL database
- Set secure SECRET_KEY
- Configure email settings
- Set up proper SSL/TLS
- Configure proper file storage

## Running the Application

### Development Server
```bash
flask run
```

### Production Server
```bash
# Using Gunicorn (Unix/Linux)
gunicorn -w 4 "manage:app"

# Using Waitress (Windows)
waitress-serve --call 'manage:app'
```

## Default Admin Account
- Username: `admin`
- Password: `admin`
- **Important:** Change these credentials immediately after first login

## Project Structure
```
print-mis/
├── app/                    # Application package
│   ├── auth/              # Authentication module
│   ├── main/              # Main views and dashboard
│   ├── orders/            # Order management
│   ├── production/        # Production management
│   ├── invoicing/         # Invoicing and financial
│   ├── static/            # Static files
│   └── templates/         # HTML templates
├── instance/              # Instance-specific files
├── migrations/            # Database migrations
├── tests/                 # Test suite
├── venv/                  # Virtual environment
├── .env                   # Environment variables
├── config.py              # Configuration settings
├── manage.py             # Application entry point
└── requirements.txt      # Python dependencies
```

## Development

### Running Tests
```bash
pytest
```

### Database Migrations
```bash
flask db migrate -m "Migration message"
flask db upgrade
```

### Code Style
- Follow PEP 8 guidelines
- Use type hints where possible
- Document functions and classes

## Contributing
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Security Considerations
- Change default admin credentials
- Use strong passwords
- Keep dependencies updated
- Configure proper CORS settings
- Set up proper SSL/TLS in production
- Regularly backup database

## License
This project is licensed under the MIT License - see the LICENSE file for details

## Support
For support, please open an issue in the GitHub repository.
