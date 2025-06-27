FROM python:3.11

WORKDIR /app

RUN apt-get update && apt-get install -y build-essential git && rm -rf /var/lib/apt/lists/*

# copy in requirements file
COPY requirements.txt .

# install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# copy in application files
COPY app.py .

# expose port
EXPOSE ${UI_PORT}

CMD ["python", "app.py"]