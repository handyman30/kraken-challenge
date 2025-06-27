# Kraken D0010 Flow File Importer

**Author:** Handy Hasan

## Overview

This service imports D0010 flow files (meter reading data) into a database and provides a web interface for support staff to search readings by MPAN or meter serial number.

Built with Django because it gives us a lot out of the box - admin interface, ORM, migrations, etc. Perfect for a 3-4 hour project.

## Architecture

Pretty straightforward:
- Django app with SQLite (keeping it simple for local dev)
- Management command for importing D0010 files
- Basic web UI for searching readings
- Models for meter points, meters, and readings

## Assumptions Made

- Using SQLite for simplicity (production would use Postgres)
- Not handling all edge cases in the D0010 spec - focusing on the main flow
- Assuming file format is consistent with the sample
- Not implementing file upload via web (as specified, CLI only for now)

## Trade-offs & Design Decisions

- **SQLite over Postgres**: Faster to get running locally, no setup required
- **Django over Flask/FastAPI**: More batteries included, less boilerplate
- **Simple search over full-text search**: Good enough for the use case
- **Minimal error handling**: Time constraint, would add more robust error handling in production

## Setup Instructions

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Import a D0010 file
python manage.py import_d0010 path/to/file.txt

# Run the development server
python manage.py runserver

# Access the web interface at http://localhost:8000
```

## Running Tests

```bash
python manage.py test
```

## Running the Application

After following the setup instructions:

1. **Run the development server:**
   ```bash
   python manage.py runserver
   ```

2. **Access the application:**
   - Web interface: http://localhost:8000
   - Admin interface: http://localhost:8000/admin (login: admin/admin)

3. **Import more D0010 files:**
   ```bash
   python manage.py import_d0010 path/to/your/file.txt
   ```

## Project Structure

```
kraken-challenge/
├── flowfile_importer/      # Django project settings
├── meter_readings/         # Main app
│   ├── models.py          # Data models
│   ├── views.py           # Web views
│   ├── admin.py           # Admin configuration
│   ├── tests.py           # Test suite
│   └── management/        # CLI commands
│       └── commands/
│           └── import_d0010.py
├── sample_d0010.txt       # Sample data file
└── requirements.txt       # Python dependencies
```

## TODO / Not Completed

- [ ] More comprehensive error handling for malformed files
- [ ] Full validation of all D0010 spec fields
- [ ] Bulk import optimization for large files
- [ ] REST API for file uploads
- [ ] Production deployment configuration
- [ ] More edge case test coverage 