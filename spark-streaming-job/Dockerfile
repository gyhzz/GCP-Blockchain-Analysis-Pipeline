FROM apache/spark:3.5.1

USER root

# RUN apt-get update && \
#     apt-get install -y python3-venv python3-pip

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# # Create a Python virtual environment and activate it
# RUN python3 -m venv venv
# ENV PATH="/app/venv/bin:$PATH"

# Install any needed packages specified in requirements.txt
RUN pip3 install --upgrade pip setuptools wheel
RUN pip3 install --no-cache-dir -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable
ENV NAME World

# Command to run your script
# CMD ["/opt/spark/bin/spark-submit", "/app/spark_test.py"]
CMD ["/bin/bash", "-c", "/opt/spark/bin/spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1 /app/spark_streamer.py"]