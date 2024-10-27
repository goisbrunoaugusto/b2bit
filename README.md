# Twitter clone project for B2Bit

This a clone of twitter's back end for the B2Bit developer selection

![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white) ![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white) ![Redis](https://img.shields.io/badge/redis-%23DD0031.svg?style=for-the-badge&logo=redis&logoColor=white) ![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)

## Installation
Prerequisites:
* [Docker Installed](https://docs.docker.com/get-started/get-docker/)
* [Docker Compose Installed](https://docs.docker.com/compose/install/)

## Observations
1. In this project I'm using [MailDev](https://github.com/maildev/maildev) to simulate the asynchronously send of emails when a user is followed. It can be accessed by the http://localhost:1080/
2. Tests should be run individually with the command
```bash
 python manage.py test account && python manage.py test post
```
3. The caching system isn't 100%, don't try to use the feed enpoint without following anyone and don't try to use the current user posts without having posted anything
## Usage

```bash
docker compose up --build
```
## Diagram
![image](https://i.imgur.com/cflqmd0.png)

## Postman Documentation
The Postman collection can be found inside the Postman folder in this project
