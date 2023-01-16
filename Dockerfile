FROM python:3-slim

WORKDIR /usr/src/app

RUN apt-get update && apt-get install -y libusb-1.0-0-dev udev libudev-dev
RUN pip install --no-cache-dir hidapi co2meter python-decouple paho-mqtt

COPY main.py main.py

CMD ["python", "main.py"]
