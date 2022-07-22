FROM python:3.9.13

# Libs
RUN python -m pip install --upgrade pip
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Dev stage
RUN mkdir -p /opt/dap/datastore-api/app/
VOLUME [ "/opt/dap/datastore-api/app/" ]
WORKDIR /opt/dap/datastore-api/app/
ENV FLASK_APP=app.py
ENV FLASK_ENV=development
CMD [ "flask", "run", "--host=0.0.0.0"]

# Prod stage
# COPY app /opt/dap/datastore-api/app/