import itertools

import requests
from PIL import Image
import io
from geopy.geocoders import Nominatim
import multiprocessing


def download(url, headers):
    point_url = MapillaryAPI.METADATA_ENDPOINT + (f"/{url['id']}"
                                                  f"?fields=id,thumb_original_url,captured_at,geometry")
    point_response = requests.get(point_url, headers=headers)
    point_json = point_response.json()
    image_url = point_json['thumb_original_url']
    image_content = requests.get(image_url).content
    image = Image.open(io.BytesIO(image_content))
    return MapillaryResponse(point_json['id'], image_url, image,
                             point_json['captured_at'], point_json['geometry'])


class MapillaryResponse:
    __GEOLOCATOR = Nominatim(user_agent="geoguessr_ai")

    def __init__(self, id, url, image, timestamp, geometry):
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


class MapillaryAPI:
    METADATA_ENDPOINT = "https://graph.mapillary.com"

    def __init__(self, token):
        self.__token = token
        self.__headers = {"Authorization": "OAuth {}".format(token)}

    def search(self,
               latitude_degrees, longitude_degrees,
               latitude_distance_degrees, longitude_distance_degrees,
               *, amount=-1, parallels=None) \
            -> list[MapillaryResponse]:

        url_imagesearch = (self.METADATA_ENDPOINT + '/images?fields=id&bbox={},{},{},{}'
                           .format(longitude_degrees - longitude_distance_degrees,
                                   latitude_degrees - latitude_distance_degrees,
                                   longitude_degrees + longitude_distance_degrees,
                                   latitude_degrees + latitude_distance_degrees))
        imagesearch_response = requests.get(url_imagesearch, headers=self.__headers)
        imagesearch_json = imagesearch_response.json()

        amount = len(imagesearch_json['data']) if amount == -1 else amount

        # Create download queues
        urls = imagesearch_json['data'][:amount]

        with multiprocessing.Pool() as pool:
            images = pool.starmap(download, zip(urls, itertools.repeat(self.__headers)), chunksize=parallels)

        return images
