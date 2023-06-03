# Sports Web Application (Distributed Software)

## Project Description
The project implements a web app using FastAPI and Vue.js technologies. Its primary goal is to provide users with the ability to purchase tickets for sports events.

The web application allows users to perform the following actions: sign up, log in, log out, view the list of available matches along with their information, add tickets to the shopping cart, select the quantity and tickets they want to purchase from the cart, and finally place the order.

## Table of Contents
1. [Graphical Interface](#graphical-interface)
2. [Project Structure](#project-structure)

## Graphical Interface

![image](https://github.com/SoftwareDistribuitUB-2023/practica-2-p1_f03/assets/90827999/b77e3005-a1b5-436d-8580-55e420995972)

![image](https://github.com/SoftwareDistribuitUB-2023/practica-2-p1_f03/assets/90827999/e3f7f63e-75b3-43d3-a53d-261c9e5b1ce5)


## Project Structure
The main structure of the project is divided into the following directories and files:

```
app
└── services
    ├── backend
    │   ├── src
    │   │   ├── __init__.py
    │   │   ├── .env
    │   │   ├── database.py
    │   │   ├── dependencies.py
    │   │   ├── main.py
    │   │   ├── schemas.py
    │   │   ├── models.py
    │   │   ├── repository.py
    │   │   ├── test_main.py
    │   │   └── test_main.http
    │   ├── data.db
    │   ├── requirements.txt
    │   └── Dockerfile
    └── frontend
        ├── package.json
        ├── Dockerfile
        ├── index.html
        ├── static
        ├── src
        └── bootstrap
        └── config
````