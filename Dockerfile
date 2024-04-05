FROM python:3.11

WORKDIR /code

COPY . .

RUN python3 -m pip install --no-cache-dir --upgrade pip
RUN python3 -m pip install --no-cache-dir --upgrade -r /code/requirements.txt

CMD ["panel", "serve", "/code/src/app.py", "--address", "0.0.0.0", "--port", "7860",  "--allow-websocket-origin", "*"]
