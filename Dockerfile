FROM python:3.10.11-slim-buster

# Upgrade pip
RUN pip install --upgrade pip

# Permissions and nonroot user for tightened security
RUN adduser --gecos "" --disabled-password --no-create-home nonroot
RUN mkdir /home/app/
RUN mkdir /home/app/instance
RUN chown -R nonroot:nonroot /home/app
RUN mkdir -p /var/log/flask-app && touch /var/log/flask-app/flask-app.err.log && touch /var/log/flask-app/flask-app.out.log
RUN chown -R nonroot:nonroot /var/log/flask-app
WORKDIR /home/app
USER nonroot

# Copy all the files to the container
COPY --chown=nonroot:nonroot solidarityzone solidarityzone
COPY --chown=nonroot:nonroot requirements.txt .

# Virtual environment
ENV VIRTUAL_ENV=/home/app/venv

# Python Setup
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN pip install -r requirements.txt

# Run database migrations
RUN flask --app solidarityzone init-db
