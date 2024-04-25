from geopy.geocoders import Nominatim
from PIL import Image
from geo.location import Location


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

    def get_location(self) -> Location:
        if self.geometry['type'] != 'Point':
            return Location.zero()
        coordinates = self.geometry['coordinates']
        latitude = coordinates[1]
        longitude = coordinates[0]
        return Location.from_degrees(latitude, longitude)

    def get_address(self) -> str:
        location = self.get_location()
        return self.__GEOLOCATOR.reverse(location)
