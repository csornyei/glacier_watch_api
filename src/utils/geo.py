import json

from src.schemas.shared import GeoJSON


def geojson_point_to_latlng(geojson_str: str | None) -> list[float] | None:
    if not geojson_str:
        return None

    pt = json.loads(geojson_str)
    lon, lat = pt["coordinates"]
    return [lat, lon]


def geojson_to_model(geojson_str: str | None) -> GeoJSON | None:
    if not geojson_str:
        return None
    return GeoJSON(**json.loads(geojson_str))


def bounds_from_minmax(
    min_lat: float | None,
    min_lon: float | None,
    max_lat: float | None,
    max_lon: float | None,
) -> (
    tuple[
        tuple[float | int | None, float | int | None],
        tuple[float | int | None, float | int | None],
    ]
    | None
):
    if None in (min_lat, min_lon, max_lat, max_lon):
        return None
    return ((min_lat, min_lon), (max_lat, max_lon))
