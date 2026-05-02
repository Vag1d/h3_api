"""Утилиты для генерации KML файлов."""
from typing import List
import h3.api.numpy_int as h3_numpy
from models import H3CellRecord


def generate_kml(records: List[H3CellRecord]) -> str:
    """
    Создаёт KML документ с полигонами гексагонов
    
    Args:
        records: Список записей H3CellRecord
    
    Returns:
        Строка с KML документом
    """
    kml_header = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>H3 Hexagons Dataset</name>
    <description>Hexagons from H3 dataset</description>
"""
    
    placemarks = []
    for i, rec in enumerate(records, 1):
        boundary = h3_numpy.cell_to_boundary(rec.h3_index)
        
        # Формируем координаты в формате KML: lon,lat,alt
        coords = []
        for lat, lon in boundary:
            coords.append(f"{lon},{lat},0")
        
        coord_str = " ".join(coords)
        
        placemark = f"""    <Placemark>
      <name>Hexagon {i}</name>
      <description>H3 Index: {h3_numpy.int_to_str(rec.h3_index)}</description>
      <styleUrl>#hexagonStyle</styleUrl>
      <Polygon>
        <extrude>0</extrude>
        <altitudeMode>clampToGround</altitudeMode>
        <outerBoundaryIs>
          <LinearRing>
            <coordinates>{coord_str}</coordinates>
          </LinearRing>
        </outerBoundaryIs>
      </Polygon>
    </Placemark>"""
        placemarks.append(placemark)
    
    # Добавляем стиль для отображения
    style = """    <Style id="hexagonStyle">
      <LineStyle>
        <color>ff0000ff</color>
        <width>2</width>
      </LineStyle>
      <PolyStyle>
        <color>80ffffff</color>
        <fill>1</fill>
        <outline>1</outline>
      </PolyStyle>
    </Style>"""
    
    kml_footer = """  </Document>
</kml>"""
    
    return kml_header + style + "\n".join(placemarks) + kml_footer