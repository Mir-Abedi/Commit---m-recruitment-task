FROM docker.arvancloud.ir/python:3.11-slim 
COPY . .
RUN pip install -r requirements.txt
CMD sh -c "python3 server.py"