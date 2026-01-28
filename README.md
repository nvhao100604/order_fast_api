# order_fast_api project
## Version infomation:
- Python 3.13.3
- FastAPI 25.3
## Intruction:
- Run:
```bash
uvicorn app.main:app --reload --port 8080
```
- Open link: 
[Swagger API Documentation](http://localhost:8080/docs)
## Install:
+ Framework:
```bash
pip install fastapi[all]
```
```bash
python -m venv venv
```
+ Database:
```bash
pip install sqlalchemy psycopg2
```

## Set up:
### Create database:    
```bash
create database restaurant_database
```

### Migrations running:
+ Initializing:
```bash
alembic init migrations
```
+ Migrating:
```bash
python -m scripts.migrate <message>
```
+ Seeding:
```bash
python -m scripts.seed.py
```
