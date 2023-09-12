#Create a ubuntu base image with python 3 installed.
FROM python:3.11-alpine
EXPOSE 8080

#Set the working directory
WORKDIR /

#copy all the files
COPY /app /app/
COPY *.py ./
COPY *.txt ./

RUN ls -la /app/*


#Install the dependencies
RUN python -m pip install --upgrade pip
RUN pip3 install -r requirements.txt

#Run the command
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "main:app"]
