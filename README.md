# QuizOut
QuizOut is a server and client for a gameshow buzzer. The client will treat keyboard keys as individual buzzers for each user.

## Project layout
Both server and client are included in this repo with their respective directories and corresponding requirements.txt files. Use these to create separate venv's for each.

## Setup
First, create a .env file in the quizout-server directory. The contents should look like the following:

```
# .env file
SECRET_LOCATION=~/.quizoutserver/secrets/
DEBUG=True
```

`SECRET_LOCATION` should point to a directory where you store your keys as text files. Permissions for this location should be modified so that only the user running the server has access. (For dev purposes, this user account can be your account.) The secret directory should contain the following files:
 - api_key
 - api_secret
 - db_pass

These should each contain your desired secret.

## Docker
For running the server in production, the Dockerfile is set up to run the server with gunicorn. The quickest way to get it up and running is to use docker compose (i.e., navigate to the server directory and run `$ docker compose up -d`).