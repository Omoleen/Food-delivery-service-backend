# Use an official Ubuntu as the base image
FROM ubuntu:latest

# Set the working directory in the container
WORKDIR /app

# Update the package lists and install dependencies
RUN apt-get update && \
    apt-get install -y python3 python3-pip

# Copy the requirements.txt file to the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

RUN apt install gdal-bin libgdal-dev
RUN apt install python3-gdal
RUN apt install binutils libproj-dev

# Copy the Django project code to the container
COPY . .


# Expose the Django development server port (optional)
EXPOSE 8000

