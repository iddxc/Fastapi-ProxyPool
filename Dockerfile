FROM python:3.8-slim
RUN mkdir -p /data
WORKDIR /data
COPY . .
RUN pip install --upgrade pip
RUN pip3 install -r requirements.txt
CMD ["python3", "main.py"]