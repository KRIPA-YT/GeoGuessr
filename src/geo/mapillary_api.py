import requests
from PIL import Image
import io
import multiprocessing
from geo.mapillary_response import MapillaryResponse
from geo.location import Location
import tqdm


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

    def search(self, location: Location, radius: Location, *,
               amount: int | None = None, parallels: int | None = None,
               chunksize: int = 1,
               verbose: bool = False) \
            -> list[MapillaryResponse]:
        url_imagesearch = (self.METADATA_ENDPOINT + '/images?fields=id&bbox={},{},{},{}'
                           .format(location.longitude_degrees - radius.longitude_degrees,
                                   location.latitude_degrees - radius.latitude_degrees,
                                   location.longitude_degrees + radius.longitude_degrees,
                                   location.latitude_degrees + radius.latitude_degrees))
        imagesearch_response = requests.get(url_imagesearch, headers=self.__headers)
        imagesearch_json = imagesearch_response.json()

        if not imagesearch_json or len(imagesearch_json) <= 0:  # If response is empty or no hits:
            return []

        amount = len(imagesearch_json['data']) if amount is None else amount

        urls = imagesearch_json['data'][:amount]

        images = []
        with multiprocessing.Pool(processes=parallels) as pool:
            if verbose:
                for image in tqdm.tqdm(pool.imap_unordered(self._download, urls, chunksize=chunksize), total=len(urls)):
                    images.append(image)
            else:
                for image in pool.imap_unordered(self._download, urls, chunksize=chunksize):
                    images.append(image)

        return images

    def parallel_search(self):
        pass
