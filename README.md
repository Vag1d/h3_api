# H3 API

REST API для работы с геопространственным датасетом на основе системы индексации H3. API предоставляет эндпоинты для поиска и фильтрации данных

### Локальный запуск

```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Запуск с Docker
```
docker-compose up --build
```

## API Endpoints
### GET /hex 
    Возвращает записи датасета, входящие в указанный родительский гексагон
    Пример запроса:
    curl "http://localhost:8000/hex?hex=8a11aa648367fff"

### GET /avg
    Группирует записи по cell_id и возвращает медианное значение level с родительским гексагоном нужного разрешения
    Пример запроса:
    curl "http://localhost:8000/avg?resolution=0"

### GET /bbox
    Возвращает записи датасета, гексагоны которых полностью находятся внутри заданного полигона
    Пример запроса:
    curl "http://localhost:8000/bbox?border=56.035953/37.911440,56.280315/37.589786,56.0/37.182514"

### GET /bbox_kml
    Аналог /bbox, но возвращает KML файл
    Пример запроса:
    curl -O "http://localhost:8000/bbox_kml?border=56.035953/37.911440,56.280315/37.589786,56.0/37.182514"