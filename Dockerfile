FROM python:3.12-slim-bullseye

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file from the parent directory into the container at /app
COPY ./requirements.txt /app/requirements.txt

# Update pip and Install any needed packages specified in requirements.txt
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt 

COPY ./ /app/

EXPOSE 8000

COPY ./entrypoint.sh /

RUN chmod +x /entrypoint.sh

CMD ["/entrypoint.sh"]