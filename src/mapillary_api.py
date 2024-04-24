import requests
from PIL import Image
import io


class MapillaryResponse:
    def __init__(self, id, url, timestamp, geometry):
        self.id = id
        self.url = url
        self.timestamp = timestamp
        self.geometry = geometry

    def get_picture(self) -> Image:
        img_data = requests.get(self.url).content
        return Image.open(io.BytesIO(img_data))

    def get_coordinates(self) -> tuple[int, int]:
        if self.geometry['type'] != 'Point':
            return 0, 0
        coordinates = self.geometry['coordinates']
        coordinates.reverse()
        return tuple[int, int](coordinates)


class MapillaryAPI:
    __METADATA_ENDPOINT = "https://graph.mapillary.com"

    def __init__(self, token):
        self.__token = token
        self.__headers = {"Authorization": "OAuth {}".format(token)}

    def search(self,
               latitude_degrees, longitude_degrees,
               latitude_distance_degrees, longitude_distance_degrees,
               *, amount=-1)\
            -> list[MapillaryResponse]:
        url_imagesearch = (self.__METADATA_ENDPOINT + '/images?fields=id&bbox={},{},{},{}'
                           .format(longitude_degrees - longitude_distance_degrees,
                                   latitude_degrees - latitude_distance_degrees,
                                   longitude_degrees + longitude_distance_degrees,
                                   latitude_degrees + latitude_distance_degrees))
        imagesearch_response = requests.get(url_imagesearch, headers=self.__headers)
        imagesearch_json = imagesearch_response.json()

        images = []

        amount = len(imagesearch_json['data']) if amount == -1 else amount

        for image in imagesearch_json['data'][:amount]:
            # DOCS: https://www.mapillary.com/developer/api-documentation/#image
            image_url = self.__METADATA_ENDPOINT + f"/{image['id']}?fields=id,thumb_original_url,captured_at,geometry"
            image_response = requests.get(image_url, headers=self.__headers)
            image_json = image_response.json()
            images.append(MapillaryResponse(image_json['id'], image_json['thumb_original_url'],
                                            image_json['captured_at'], image_json['geometry']))
        return images
