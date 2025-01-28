FROM python:slim

WORKDIR /app

# Add and install dependencies
ADD ./requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Add your scripts to the container
ADD ./add_language_tag.py add_language_tag.py
ADD ./clear_tags.py clear_tags.py

# Set the environment variable for the interval (default to 1 hour if not provided)
ENV INTERVAL_HOURS=1

# Add an entrypoint script to handle script execution
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Use the entrypoint script to start the container
ENTRYPOINT ["/entrypoint.sh"]
