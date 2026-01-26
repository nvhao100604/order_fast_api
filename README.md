# order_fast_api project
## Thông tin phiên bản:
- Python 3.13.3
- FastAPI 25.3
## Hướng dẫn sử dụng:
- Chạy:
```bash
uvicorn app.main:app --reload --port 8080
```
- Mở: 
[Swagger API Documentation](http://localhost:8080/docs)
## Cài đặt:
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