# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.10-slim

# Install pip requirements
COPY requirements.txt .
RUN python -m pip install -r requirements.txt

ENV ACCOUNT1="100844397,R89ltoFpEo31ori4TBGSFC9gn2hz13K4PhSylFhW"
ENV SERVER="en-us"
ENV TIME="00:00"
ENV TZ="Asia/Jakarta"

WORKDIR /app
COPY . /app

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD ["python", "main.py"]
