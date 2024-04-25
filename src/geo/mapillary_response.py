from geopy.geocoders import Nominatim
from PIL import Image


class MapillaryResponse:
    __GEOLOCATOR = Nominatim(user_agent="geoguessr_ai")

    def __init__(self, id, url, image: Image, timestamp, geometry):
        self.id = id
        self.url = url
        self.image = image
        self.timestamp = timestamp
        self.geometry = geometry

    def get_picture(self) -> Image:
        return self.image

    def get_coordinates(self) -> tuple[int, int]:
        if self.geometry['type'] != 'Point':
            return 0, 0
        coordinates = self.geometry['coordinates']
        coordinates.reverse()
        return tuple[int, int](coordinates)

    def get_address(self) -> str:
        coordinates = list(self.get_coordinates())
        coordinates.reverse()
        return self.__GEOLOCATOR.reverse(coordinates)
