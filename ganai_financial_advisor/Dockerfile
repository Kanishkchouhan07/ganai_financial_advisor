FROM python:3.9

WORKDIR /app

COPY backend/requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

COPY backend/ ./backend

CMD ["python", "backend/app.py"]