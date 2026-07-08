
FROM python:3.12-slim

WORKDIR /app

# System dependencies required for psycopg2
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Grant execute permissions to our startup manager script
RUN chmod +x start.sh

# Let Render bind to the port dynamically
EXPOSE 8000

# Execute the script that kicks off migrations, celery, and uvicorn
CMD ["./start.sh"]