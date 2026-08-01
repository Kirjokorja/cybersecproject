# Cyber Security Base 2025 Project I

This project demonstrates a web site with five security flaws.

## How to use

### Preparations

1. Make sure that `Python version 3.14` has been installed on your computer.
2. Make sure that `Poetry version 2.3.2` has been installed on your computer.
3. Download the project or clone the repository to your computer.

### Installation

1. Inside the directory `cybersecproject` install dependencies by running the command:

```bash
poetry install
```

2. In the same directory create the database:

```bash
potery run python3 manage.py migrate
```

3. Activate database models:

```bash
poetry run python3 manage.py makemigrations polls
```

4. Create tables to the database from the models:

```bash
poetry run python3 manage.py migrate
```

5. Create the admin:

```bash
poetry run python3 manage.py createsuperuser
```
	a. Enter a username of you choice.
	b. Enter an e-mail of your choice. (I suggest a moc e-mail.)
	c. Enter a password of your choice.

### Start the web site

1. Start the server:

```bash
poetry run python3 manage.py runserver
```

2. Open the site in a browser by using URL  `http://127.0.0.1:8000/polls/`.
