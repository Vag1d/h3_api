from dataclasses import dataclass
import h3.api.numpy_int as h3_numpy


@dataclass(frozen=True)
class H3CellRecord:
    """Запись о гексагоне H3"""
    h3_index: int
    level: int
    cell_id: int

    def to_row(self) -> list:
        """Сериализация в список [hex_string, level, cell_id]"""
        return [h3_numpy.int_to_str(self.h3_index), self.level, self.cell_id]

    @staticmethod
    def from_row(row: list) -> "H3CellRecord":
        """Десериализация из списка"""
        return H3CellRecord(
            h3_index=int(h3_numpy.str_to_int(str(row[0]))),
            level=int(row[1]),
            cell_id=int(row[2]),
        )


@dataclass(frozen=True)
class GeoPoint:
    lat: float
    lon: float