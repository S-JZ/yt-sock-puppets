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
COPY sockpuppet.py ./
COPY requirements.txt ./

# Install pre-dependencies
RUN apt update
RUN apt install -y wget g++ unzip xvfb firefox-esr

# install python dependencies
RUN pip install -r requirements.txt

# Install chrome
RUN wget https://storage.googleapis.com/chrome-for-testing-public/122.0.6261.69/linux64/chrome-linux64.zip
RUN unzip chrome-linux64

# Download youtube-dl
RUN wget https://github.com/ytdl-org/ytdl-nightly/releases/download/2024.01.23/youtube-dl
RUN chmod +x youtube-dl

# Download chromedriver
RUN wget https://storage.googleapis.com/chrome-for-testing-public/122.0.6261.69/linux64/chromedriver-linux64.zip
RUN unzip chromedriver-linux64.zip

#set display port to avoid crash
ENV DISPLAY=:99

# Install ffmpeg
RUN apt install -y ffmpeg
RUN apt-get install -y chromium
