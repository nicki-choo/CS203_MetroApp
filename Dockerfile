FROM python:3.11.2
EXPOSE 5000
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV FLASK_APP=app.py
WORKDIR /app.py
RUN pip install flask
COPY . .
CMD ["flask", "run", "--host", "0.0.0.0"]