FROM python:3.12-alpine

RUN apk update && apk add --no-cache postgresql-dev gcc python3-dev musl-dev

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["sh", "-c", "sleep 10\
 && python manage.py makemigrations\
 && python manage.py migrate\
 && python manage.py runserver 0.0.0.0:8000"]
