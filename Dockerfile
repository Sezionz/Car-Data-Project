# 1. The Base Image: A lightweight version of Python 3.12
FROM python:3.12-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Copy only the backend requirements first (for caching efficiency)
COPY requirements.txt .

# 4. Install the backend dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy your logic and data into the container
COPY src/ ./src/
COPY database/ ./database/

# 6. Expose the port so the Kivy frontend can talk to it
EXPOSE 8000

# 7. The Boot Command: Launch the FastAPI server
CMD ["uvicorn", "src.car_API:app", "--host", "0.0.0.0", "--port", "8000"]