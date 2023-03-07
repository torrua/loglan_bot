#Create a ubuntu base image with python 3 installed.
FROM python:3.11-alpine
EXPOSE 8080

#Set the working directory
WORKDIR /

#copy all the files
COPY /app /app/
COPY /bot /bot/
COPY /config /config/
COPY *.py ./
COPY *.txt ./

RUN ls -la /app/*
RUN ls -la /bot/*
RUN ls -la /config/*

#Install the dependencies
RUN pip3 install -r requirements.txt

#Run the command
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "main:app"]
