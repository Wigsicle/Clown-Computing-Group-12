# Use the official Python 3.12 image
FROM python:3.12

# Set the working directory
WORKDIR /app

# Copy only the requirements file to leverage Docker cache for dependencies
COPY requirements.txt .

# Install the dependencies
RUN pip install -r requirements.txt

# Copy the .env file
COPY .env .

# Copy the rest of the application code
COPY . .

# Copy the entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Set the entrypoint
ENTRYPOINT ["/entrypoint.sh"]

# Set the default command to run the application
CMD ["python", "app.py"]
