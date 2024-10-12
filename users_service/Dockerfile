FROM docker.arvancloud.ir/python:3.11-slim 
COPY . .
RUN pip install -r requirements.txt
RUN python3 manage.py makemigrations
CMD sh -c "python3 manage.py migrate && python3 manage.py runserver 0.0.0.0:8000"