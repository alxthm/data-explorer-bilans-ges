FROM python:3.11

# Make the fr_FR locale available
RUN apt-get update && apt-get install -y locales && \
    sed -i -e 's/# fr_FR.UTF-8/fr_FR.UTF-8/' /etc/locale.gen && \
    dpkg-reconfigure --frontend=noninteractive locales

WORKDIR /code

COPY ./requirements.lock.txt .

RUN python3 -m pip install --no-cache-dir --upgrade pip
RUN python3 -m pip install --no-cache-dir -r /code/requirements.lock.txt

COPY ./data ./data
COPY ./src ./src
COPY ./setup.py .
COPY ./Makefile .

# hack: the '-e' option is here so that the data paths work (could be refactored)
RUN python3 -m pip install --no-cache-dir -e .

CMD [ "make", "serve" ]
