﻿# Library service API

API  service for library written on DRF

## Features:

- JWT authenticated
- Admin panel /admin/
- Documentation is located via /api/doc/swagger/
- Managing of borrowing and book return
- Telegram notifications about overdue borrowings
- Creating book with two type of covers
- Filtering borrowings by user ID and status
- Docker app starts only when db is available ( custom command via management/commands )

## Installing:
```angular2html
git clone https://github.com/anastasiia-tsurkan/library-service-api.git
cd library-service-api
python3 -m venv venv
source venv/bin/activate #for iOS or Linux
venv/Scripts/activate #for Windows
pip install -r requirements.txt
python3 manage.py loaddata fixtures_file.json 
```
open .env.sample and change environment variables on yours !Rename file from .env.sample to .env
```
python manage.py migrate
python manage.py runserver
```

## Run with Docker:
```angular2html
docker-compose build
docker-compose up
```

## Getting access

- Create user via /api/user/register/
- Get user token via /api/user/token/
- Authorize with it on /api/doc/swagger/ OR
- Install ModHeader extension to your browser and create Request header with value Bearer <Your access tokekn>

or use already created one:

Email: ```admin@library.com```
Password: ```admin12345```

## Endpoints:
### User:
- [POST] /api/users/register/ (register your user)
- [POST] /api/users/login/ (login your user)
- [GET] /api/users/me (info about yourself)
- [PUT] /api/users/me (update all info about yourself)
- [PATCH] /api/users/me (partial update of info about yourself)
- [POST] /api/users/token (get your JWT token for access)
- [POST] /api/users/token/refresh (update your access token)

### Book:
- [POST] /api/library/books/ (create nem book)
- [GET] /api/library/books/ (list of all books)
- [GET] /api/library/books/{id} (detail info about book)
- [PUT] /api/library/books/{id} (update all book instance)
- [PATCH] /api/library/books/{id} (partial update of book instance)
- [DELETE] /api/library/books/{id} (delete book with chosen id)

### Borrowing:
- [GET] /api/library/borrowings/ (list of all borrowings)
- [GET] /api/library/borrowings/{id} (detail info about borrow)
- [GET] /api/library/borrowings/?is_active=true&user_id={user.id} (filter borrowings by return state and user id for staff user)
- [PUT] /api/library/borrowings/{id} (update all borrow instance)
- [PATCH] /api/library/borrowings/{id} (partial update of borrow instance)
- [DELETE] /api/library/borrowings/{id} (delete borrow with chosen id)
- [DELETE] /api/library/borrowings/{id}/return (return book with given borrow id)

## Get Telegram notifications:
- Create new bot by BotFather and get token as TELEGRAM_BOT_TOKEN
- Through @RawDataBot in the created bot get chat_id {"from":{"id": chat_id}} as TELEGRAM_CHAT_ID

![image](https://github.com/anastasiia-tsurkan/library-service-api/assets/117210097/51fc94e7-7973-4279-a22c-0327e4c5fb93)

