from statistics import median
import math
from typing import Dict, List

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

import h3.api.numpy_int as h3_numpy

from models import H3CellRecord
from dataset import DATASET_RECORDS
from geo_utils import cell_fully_inside_polygon, parse_border
from kml_utils import generate_kml



app = FastAPI(
    title="H3 Dataset API",
    description="API для работы с датасетом H3 гексагонов"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    """Корневой эндпоинт"""
    return {
        "message": "H3 Dataset API",
        "docs": "/docs",
        "endpoints": ["/hex", "/avg", "/bbox", "/bbox_kml"]
    }


@app.get("/hex")
def get_hex(hex: str = Query(..., description="H3 индекс в hex формате")):
    """
    Возвращает элементы датасета, входящие в заданный гексагон
    
    Args:
        hex: Индекс родительского гексагона в формате строки
        
    Returns:
        Список записей [hex_string, level, cell_id]
    
    Example:
        GET /hex?hex=8a11aa648367fff
    """
    try:
        h3_int = int(h3_numpy.str_to_int(hex))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid H3 index string")

    try:
        resolution = h3_numpy.get_resolution(h3_int)
    except Exception:
        raise HTTPException(status_code=400, detail="Cannot determine H3 resolution")

    # Фильтруем записи, чьи H3 ячейки являются потомками указанного индекса
    result = [
        rec for rec in DATASET_RECORDS
        if h3_numpy.cell_to_parent(rec.h3_index, resolution) == h3_int
    ]

    return [rec.to_row() for rec in result]


@app.get("/avg")
def get_avg(
    resolution: int = Query(
        ...,
        ge=0,
        le=12,
        description="Разрешение H3 (0-12)"
    )
):
    """
    Группирует записи по cell_id с медианным значением level
    
    Args:
        resolution: Желаемое разрешение для родительских гексагонов
        
    Returns:
        Список [hex_string, median_level, cell_id]
    
    Example:
        GET /avg?resolution=0
    """
    # Группируем записи по cell_id
    groups: Dict[int, List[H3CellRecord]] = {}
    for rec in DATASET_RECORDS:
        groups.setdefault(rec.cell_id, []).append(rec)

    avg_result = []
    for cell_id, records in groups.items():
        # Вычисляем медиану уровней с округлением вниз
        levels = [r.level for r in records]
        med_level = math.floor(median(levels))

        # Берём первый h3_index и находим родителя нужного разрешения
        parent = h3_numpy.cell_to_parent(records[0].h3_index, resolution)
        hex_str = h3_numpy.int_to_str(parent)

        avg_result.append([hex_str, med_level, cell_id])

    return avg_result


@app.get("/bbox")
def get_bbox(
    border: str = Query(
        ...,
        description="Координаты полигона: lat1/lon1,lat2/lon2,..."
    )
):
    """
    Возвращает записи полностью находящиеся внутри заданного полигона
    
    Args:
        border: Строка с координатами вершин полигона
        
    Returns:
        Список записей [hex_string, level, cell_id]
    
    Example:
        GET /bbox?border=56.035953/37.911440,56.280315/37.589786,56.0/37.182514
    """
    try:
        polygon = parse_border(border)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    result = [
        rec for rec in DATASET_RECORDS
        if cell_fully_inside_polygon(rec.h3_index, polygon)
    ]
    
    return [rec.to_row() for rec in result]


@app.get("/bbox_kml")
def get_bbox_kml(
    border: str = Query(
        ...,
        description="Координаты полигона: lat1/lon1,lat2/lon2,..."
    )
):
    """
    Возвращает KML файл с гексагонами внутри заданного полигона
    
    Args:
        border: Строка с координатами вершин полигона
        
    Returns:
        KML файл для скачивания
    
    Example:
        GET /bbox_kml?border=56.035953/37.911440,56.280315/37.589786,56.0/37.182514
    """
    try:
        polygon = parse_border(border)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    filtered_records = [
        rec for rec in DATASET_RECORDS
        if cell_fully_inside_polygon(rec.h3_index, polygon)
    ]

    kml_content = generate_kml(filtered_records)

    return Response(
        content=kml_content,
        media_type="application/vnd.google-earth.kml+xml",
        headers={
            "Content-Disposition": "attachment; filename=hexagons.kml"
        },
    )