FROM python:3.11

# Make the fr_FR locale available
RUN apt-get update && apt-get install -y locales && \
    sed -i -e 's/# fr_FR.UTF-8/fr_FR.UTF-8/' /etc/locale.gen && \
    dpkg-reconfigure --frontend=noninteractive locales

WORKDIR /code

COPY . .

RUN python3 -m pip install --no-cache-dir --upgrade pip
RUN python3 -m pip install --no-cache-dir --upgrade -r /code/requirements.txt

CMD ["panel", "serve", "/code/src/app.py", "--address", "0.0.0.0", "--port", "7860",  "--allow-websocket-origin", "*"]
