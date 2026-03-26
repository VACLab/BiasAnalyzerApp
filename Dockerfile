FROM python:3.11

WORKDIR /app

RUN apt-get update && apt-get install -y build-essential git && rm -rf /var/lib/apt/lists/*

# copy in requirements file
COPY requirements.txt .

# install dependencies
RUN pip install --no-cache-dir -r requirements.txt

COPY src /app/src
COPY assets /app/assets
COPY app.py /app/app.py

EXPOSE 8050

CMD ["python", "/app/app.py"]
