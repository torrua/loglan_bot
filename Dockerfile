# Create a ubuntu base image with python 3 installed.
FROM python:3.12-alpine

# Set the working directory
WORKDIR /

# Create and activate a virtual environment
RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"

# Copy requirements.txt and install dependencies
COPY requirements.txt .

# Copy all the files
COPY /app /app/
COPY *.py ./

# Clean up
RUN rm -rf /var/cache/apk/* && \
rm -rf /root/.cache

RUN ls -la /app/*

EXPOSE 8080

# Install the dependencies
RUN /venv/bin/python -m pip install --upgrade pip
RUN /venv/bin/pip install --no-cache-dir -r requirements.txt

# Run the command
CMD ["hypercorn", "-b", "0.0.0.0:8000", "main:app"]