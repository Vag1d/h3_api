"""Модуль для генерации и управления исходным датасетом."""
from typing import List
import h3.api.numpy_int as h3_numpy
from models import H3CellRecord
from geo_utils import calculate_level_and_cell_id, circle_vertices


def generate_dataset(
    center_lat: float = 56.0,
    center_lon: float = 38.0,
    radius_km: float = 7.0,
    resolution: int = 12,
) -> List[H3CellRecord]:
    """
    Генерирует датасет H3 записей для заданной области.
    
    Args:
        center_lat: Широта центра области
        center_lon: Долгота центра области
        radius_km: Радиус области в километрах
        resolution: Разрешение H3 сетки
    
    Returns:
        Список H3CellRecord записей
    """
    # Создаём полигон круга
    vertices = circle_vertices(center_lat, center_lon, radius_km)
    polygon = h3_numpy.LatLngPoly(vertices)
    
    # Получаем ячейки-кандидаты
    candidates = h3_numpy.polygon_to_cells(polygon, resolution)
    
    center = (center_lat, center_lon)
    records: List[H3CellRecord] = []
    
    for h3_index in candidates:
        h3_index_int = int(h3_index)
        hex_center = h3_numpy.cell_to_latlng(h3_index_int)
        
        # Фильтруем по точному расстоянию до центра
        distance = h3_numpy.great_circle_distance(
            center, hex_center, unit="km"
        )
        
        if distance <= radius_km:
            level, cell_id = calculate_level_and_cell_id(h3_index_int)
            records.append(
                H3CellRecord(
                    h3_index=h3_index_int,
                    level=level,
                    cell_id=cell_id
                )
            )
    
    return records


# Создаём фиксированный датасет при импорте модуля
DATASET_RECORDS: List[H3CellRecord] = generate_dataset()