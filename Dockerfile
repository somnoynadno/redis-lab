FROM python:3

WORKDIR /services/redis-lab

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "./main.py" ]

EXPOSE 8888