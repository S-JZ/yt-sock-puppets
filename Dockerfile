# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.7-slim-buster

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Set current directory as ENV
ENV PATH=/app:$PATH

# Needed for tzdata
ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=America/Los_Angeles

# copy items
WORKDIR /app
copy YTDriver.py ./
copy helpers.py ./
COPY arguments/ ./arguments/puppets/
COPY sockpuppet.py ./
COPY requirements.txt ./

# Install pre-dependencies
RUN apt update
RUN apt install -y wget g++ unzip xvfb firefox-esr

# install python dependencies
RUN pip install -r requirements.txt

# Install chrome
RUN wget http://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_121.0.6167.139-1_amd64.deb
RUN apt install -y ./google-chrome-stable_121.0.6167.139-1_amd64.deb

# Download youtube-dl
RUN wget https://github.com/ytdl-org/ytdl-nightly/releases/download/2024.01.23/youtube-dl
RUN chmod +x youtube-dl

# Download chromedriver
RUN wget https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/121.0.6167.85/linux64/chromedriver-linux64.zip
RUN unzip chromedriver-linux64.zip -d chromedriver-linux64

RUN mv chromedriver-linux64/chromedriver-linux64/chromedriver /app/chromedriver


#set display port to avoid crash
ENV DISPLAY=:99

# Install ffmpeg
RUN apt install -y ffmpeg
RUN apt-get install -y chromium
# run chrome to test
RUN google-chrome-stable --version
RUN chromedriver --version
RUN youtube-dl --version

