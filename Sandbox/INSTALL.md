# Print MIS Installation Guide

This guide provides instructions for setting up and running the Print MIS system, a comprehensive Management Information System for commercial printing companies.

## System Requirements

- Python 3.8 or higher
- pip (Python package manager)
- SQLite (development) or PostgreSQL (production)
- Virtual environment (recommended)

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/print-mis.git
cd print-mis
```

### 2. Set Up a Virtual Environment

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# For Windows:
venv\Scripts\activate
# For macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root with the following variables (example values shown):

```
# Flask application configuration
SECRET_KEY=your-secure-secret-key
FLASK_APP=manage.py
FLASK_ENV=development

# Database configuration
# SQLite for development (default)
# For PostgreSQL in production:
# DATABASE_URL=postgresql://username:password@localhost/printmis

# Email configuration (optional)
# MAIL_SERVER=smtp.example.com
# MAIL_PORT=587
# MAIL_USE_TLS=1
# MAIL_USERNAME=your-email@example.com
# MAIL_PASSWORD=your-email-password
```

### 5. Initialize the Database

```bash
# Create database tables and initialize with default data
flask init_db
```

This command:
- Creates all database tables
- Creates an admin user (username: admin, password: admin)
- Adds default products
- Adds default materials

### 6. Create Demo Data (Optional)

```bash
# Add sample data for testing
flask demo_data
```

### 7. Run the Application

```bash
# Start the development server
flask run
```

The application will be available at http://127.0.0.1:5000

## First Login

After initialization, you can log in with the default admin credentials:

- Username: `admin`
- Password: `admin`

**Important:** Change the default password immediately after first login.

## Production Deployment

For production deployment:

1. Use a production WSGI server like Gunicorn or uWSGI
2. Configure a reverse proxy with Nginx or Apache
3. Use PostgreSQL instead of SQLite
4. Set up environment variables appropriately
5. Ensure appropriate security measures are in place

Example Gunicorn deployment:

```bash
pip install gunicorn
gunicorn -w 4 "manage:app"
```

## System Organization

The MIS consists of the following main modules:

- **Order Entry:** Customer management, quotes, and order creation
- **Production Management:** Job scheduling, workflow tracking, and materials management
- **Invoicing:** Invoice generation, payment tracking, and financial reporting

## Development

### Project Structure

- `app/` - Application package
  - `auth/` - Authentication module
  - `main/` - Main views and dashboard
  - `orders/` - Order entry system
  - `production/` - Production management
  - `invoicing/` - Invoicing and financial
  - `templates/` - HTML templates
  - `static/` - Static assets
  - `models.py` - Database models
- `migrations/` - Database migrations
- `manage.py` - Application entry point
- `config.py` - Configuration settings

### Running Tests

```bash
# Run tests (when implemented)
pytest
```

## Troubleshooting

If you encounter issues:

1. Check the application logs
2. Verify database connection settings
3. Ensure all requirements are installed
4. Confirm that environment variables are set correctly

## Support

For additional help, please open an issue on the project's GitHub repository.
