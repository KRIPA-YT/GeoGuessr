import requests
from PIL import Image
import io
import multiprocessing
from geo.mapillary_response import MapillaryResponse


class MapillaryAPI:
    METADATA_ENDPOINT = "https://graph.mapillary.com"

    def __init__(self, token: str):
        self.__token = token
        self.__headers = {"Authorization": "OAuth {}".format(token)}

    def _download(self, url):
        point_url = MapillaryAPI.METADATA_ENDPOINT + (f"/{url['id']}"
                                                      f"?fields=id,thumb_original_url,captured_at,geometry")
        point_response = requests.get(point_url, headers=self.__headers)
        point_json = point_response.json()
        image_url = point_json['thumb_original_url']
        image_content = requests.get(image_url).content
        image = Image.open(io.BytesIO(image_content))
        return MapillaryResponse(point_json['id'], image_url, image,
                                 point_json['captured_at'], point_json['geometry'])

    def search(self,
               latitude_degrees: float, longitude_degrees: float,
               latitude_distance_degrees: float, longitude_distance_degrees: float,
               *, amount: int = -1, parallels: int = None) \
            -> list[MapillaryResponse]:
        url_imagesearch = (self.METADATA_ENDPOINT + '/images?fields=id&bbox={},{},{},{}'
                           .format(longitude_degrees - longitude_distance_degrees,
                                   latitude_degrees - latitude_distance_degrees,
                                   longitude_degrees + longitude_distance_degrees,
                                   latitude_degrees + latitude_distance_degrees))
        imagesearch_response = requests.get(url_imagesearch, headers=self.__headers)
        imagesearch_json = imagesearch_response.json()

        amount = len(imagesearch_json['data']) if amount == -1 else amount

        urls = imagesearch_json['data'][:amount]

        with multiprocessing.Pool() as pool:
            images = pool.map(self._download, urls, chunksize=parallels)

        return images

    def parallel_search(self):
        pass
