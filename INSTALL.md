# Installation Guide

## Quick Install

Run the installation script:

```bash
./install.sh
```

Or manually:

## Manual Installation

### 1. Create Virtual Environment

```bash
python3 -m venv venv
```

### 2. Activate Virtual Environment

**On macOS/Linux:**
```bash
source venv/bin/activate
```

**On Windows:**
```bash
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Verify Installation

```bash
python3 -m pytest --version
```

## Troubleshooting

### "command not found: pytest"

If you get this error, it means pytest is not installed or not in your PATH.

**Solution 1: Use python3 -m pytest**
```bash
python3 -m pytest tests/
```

**Solution 2: Install in virtual environment**
```bash
# Make sure virtual environment is activated
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows

# Then install
pip install pytest pytest-cov
```

**Solution 3: Install globally (not recommended)**
```bash
pip3 install --user pytest pytest-cov
```

### Permission Errors

If you get permission errors, use a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Python Version

This project requires Python 3.10+. Check your version:

```bash
python3 --version
```

If you have an older version, install Python 3.10+ from [python.org](https://www.python.org/downloads/)

## Running Tests

After installation, run tests:

```bash
# Activate virtual environment first
source venv/bin/activate

# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test file
pytest tests/test_state.py
```

## Running the Application

```bash
# Activate virtual environment
source venv/bin/activate

# Run main application
python -m src.main
```
