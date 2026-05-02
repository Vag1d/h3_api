import math
from typing import List, Tuple
import h3.api.numpy_int as h3_numpy


def calculate_level_and_cell_id(h3_index: int) -> Tuple[int, int]:
    """
    Извлекает level и cell_id из целочисленного H3 индекса
    """
    bucket = h3_index >> 9  # h3_index // 512
    level = (bucket % 74) - 120
    cell_id = (bucket % 100) + 1
    return level, cell_id


def destination_point(
    lat_deg: float,
    lon_deg: float,
    bearing_deg: float,
    distance_km: float,
) -> Tuple[float, float]:
    """
    Вычисляет координаты точки назначения
    
    Args:
        lat_deg: Широта начальной точки в градусах
        lon_deg: Долгота начальной точки в градусах
        bearing_deg: Азимут в градусах
        distance_km: Расстояние в километрах
    
    Returns:
        Кортеж (широта, долгота) в градусах
    """
    earth_radius_km = 6371.01
    
    # Преобразование в радианы
    lat = math.radians(lat_deg)
    lon = math.radians(lon_deg)
    bearing = math.radians(bearing_deg)
    angular_distance = distance_km / earth_radius_km

    # Тригонометрические вычисления
    sin_lat = math.sin(lat)
    cos_lat = math.cos(lat)
    sin_ang = math.sin(angular_distance)
    cos_ang = math.cos(angular_distance)

    new_lat = math.asin(
        sin_lat * cos_ang + 
        cos_lat * sin_ang * math.cos(bearing)
    )
    new_lon = lon + math.atan2(
        math.sin(bearing) * sin_ang * cos_lat,
        cos_ang - sin_lat * math.sin(new_lat),
    )
    
    return math.degrees(new_lat), math.degrees(new_lon)


def circle_vertices(
    center_lat: float,
    center_lon: float,
    radius_km: float,
    segments: int = 180,
) -> List[Tuple[float, float]]:
    """
    Создаёт полигон аппроксимирующий круг на поверхности Земли
    
    Args:
        center_lat: Широта центра круга
        center_lon: Долгота центра круга
        radius_km: Радиус круга в километрах
        segments: Количество сегментов для аппроксимации
    
    Returns:
        Список кортежей (lat, lon) вершин полигона
    """
    step = 360.0 / segments
    return [
        destination_point(center_lat, center_lon, bearing * step, radius_km)
        for bearing in range(segments)
    ]


def point_in_polygon(lat: float, lon: float, polygon: List[Tuple[float, float]]) -> bool:
    """
    Проверяет, находится ли точка внутри полигона (алгоритм ray casting)
    
    Args:
        lat: Широта точки
        lon: Долгота точки
        polygon: Список вершин полигона [(lat, lon), ...]
    
    Returns:
        True если точка внутри полигона
    """
    num_vertices = len(polygon)
    inside = False
    j = num_vertices - 1
    
    for i in range(num_vertices):
        lon_i, lat_i = polygon[i][1], polygon[i][0]  # (lon, lat)
        lon_j, lat_j = polygon[j][1], polygon[j][0]
        
        if ((lat_i > lat) != (lat_j > lat)) and \
           (lon < (lon_j - lon_i) * (lat - lat_i) / (lat_j - lat_i) + lon_i):
            inside = not inside
        j = i
        
    return inside


def cell_fully_inside_polygon(
    h3_index: int, 
    poly_vertices: List[Tuple[float, float]]
) -> bool:
    """
    Проверяет находится ли весь гексагон H3 внутри полигона
    
    Args:
        h3_index: Целочисленный индекс H3 ячейки
        poly_vertices: Вершины полигона
    
    Returns:
        True если все вершины гексагона внутри полигона
    """
    boundary = h3_numpy.cell_to_boundary(h3_index)  # список [(lat, lon), ...]
    
    # Проверяем все 6 вершин гексагона
    for vertex in boundary[:6]:
        lat, lon = vertex
        if not point_in_polygon(lat, lon, poly_vertices):
            return False
    return True


def parse_border(border_str: str) -> List[Tuple[float, float]]:
    """
    Парсит строку с координатами полигона в список точек
    
    Args:
        border_str: Строка формата "lat1/lon1,lat2/lon2,..."
    
    Returns:
        Список кортежей (lat, lon)
        
    Raises:
        ValueError: при неверном формате строки
    """
    points = []
    parts = border_str.split(",")
    
    for part in parts:
        coords = part.strip().split("/")
        if len(coords) != 2:
            raise ValueError(f"Invalid coordinate pair: {part}")
        try:
            lat = float(coords[0])
            lon = float(coords[1])
            points.append((lat, lon))
        except ValueError:
            raise ValueError(f"Invalid coordinates in pair: {part}")
    
    if len(points) < 3:
        raise ValueError("Polygon must have at least 3 vertices")
        
    return points