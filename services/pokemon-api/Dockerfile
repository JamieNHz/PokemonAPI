# 1. Use the official lightweight Python 3.11 image (Debian 12 / Bookworm)
FROM python:3.11-slim

# 2. Prevent Python from buffering stdout/stderr (crucial for Docker logs)
ENV PYTHONUNBUFFERED=1

# 3. Install the Microsoft ODBC Driver 18 for SQL Server
# (This is required for SQLAlchemy to communicate with Azure SQL)
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    build-essential \
    unixodbc-dev \
    && curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg \
    && curl -fsSL https://packages.microsoft.com/config/debian/12/prod.list | tee /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql18 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 4. Set the working directory inside the container
WORKDIR /app

# 5. Copy the requirements file and install dependencies
# (Doing this before copying the code leverages Docker's caching layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy the rest of the application code
COPY ./app ./app

# 7. Expose the port Uvicorn will run on
EXPOSE 8000

# 8. Define the startup command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]