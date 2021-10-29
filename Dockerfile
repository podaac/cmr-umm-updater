# Container image that runs your code
FROM python:3.9-slim

RUN apt-get update \
    && apt-get install -y jq \
    && rm -rf /var/lib/apt/lists/*

# Copies your code file from your action repository to the filesystem path `/` of the container
COPY entrypoint.sh /entrypoint.sh

# Copy source into container
RUN mkdir /podaac-umm-publisher
COPY . .

# Install umm updater tool
RUN python -m pip install --upgrade pip && pip install . 

# Code file to execute when the docker container starts up (`entrypoint.sh`)
ENTRYPOINT ["/entrypoint.sh"]
