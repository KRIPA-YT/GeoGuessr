import itertools
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

    def _download(self, id):
        point_url = MapillaryAPI.METADATA_ENDPOINT + (f"/{id}"
                                                      f"?fields=id,thumb_1024_url,captured_at,geometry")
        point_response = requests.get(point_url, headers=self.__headers)
        point_json = point_response.json()
        image_url = point_json['thumb_1024_url']
        image_content = requests.get(image_url).content
        image = Image.open(io.BytesIO(image_content)).convert('RGBA')
        return MapillaryResponse(point_json['id'], image_url, image,
                                 point_json['captured_at'], point_json['geometry'])

    def search(self, radial_bounds: tuple[Location, Location], *,
               maximum: int | None = None, parallels: int | None = None,
               chunksize: int = 1, verbose: bool = False) \
            -> list[MapillaryResponse]:
        """
        Single process search and download for Mapillary Street View pictures
        :param radial_bounds: Tuple of structure (center, radius)
        :param maximum: The maximum images to download
        :param parallels: How many download threads at maximum
        :param chunksize: How many downloads per thread at minimum
        :param verbose: Verbose console log
        :return: List of all Responses, will be empty if none found
        """
        ids = self.search_ids(radial_bounds, maximum=maximum, verbose=verbose)

        return self.download_images(ids, parallels=parallels, chunksize=chunksize, verbose=verbose)

    def parallel_search(self, radial_boundaries: list[tuple[Location, Location]], *,
                        maximum: int | None = None, chunksize: int = 1, verbose: bool = False,
                        parallels_search: int | None = None, parallels_download: int | None = None) \
            -> list[MapillaryResponse]:
        """
        Parallel process search and download for Mapillary Street View pictures
        :param radial_boundaries: List of tuple of structure (center, radius)
        :param maximum: The maximum images to download
        :param chunksize: How many downloads per thread at minimum
        :param verbose: Verbose console log
        :param parallels_search: How many search threads at maximum
        :param parallels_download: How many download threads at maximum
        :return: List of all Responses, will be empty if none found
        """
        ids = self.parallel_search_ids(radial_boundaries, parallels=parallels_search, chunksize=chunksize,
                                       maximum=maximum, verbose=verbose)
        return self.download_images(ids, parallels=parallels_download, chunksize=chunksize, verbose=verbose)

    def parallel_search_ids(self, radial_boundaries: list[tuple[Location, Location]], *, parallels: int | None = None,
                            chunksize: int = 1, maximum: int | None = None, verbose: bool = False):
        """
        Parallel search for IDS in specified bounds
        :param radial_boundaries: Tuple of structure (center, radius)
        :param parallels: How many search threads at maximum
        :param chunksize: How many searches per thread at minimum
        :param maximum: The maximum ids to return
        :param verbose: Verbose console log
        :return: List of ids in list[str] form
        """
        return [x for xs in self.parallel_search_mapped_ids(
            radial_boundaries, parallels=parallels, chunksize=chunksize, maximum=maximum, verbose=verbose
        ) for x in xs]

    def parallel_search_mapped_ids(self, radial_boundaries: list[tuple[Location, Location]], *,
                                   parallels: int | None = None,
                                   chunksize: int = 1, maximum: int | None = None, verbose: bool = False):
        """
        Parallel mapped search for IDS in specified bounds
        :param radial_boundaries: Tuple of structure (center, radius)
        :param parallels: How many search threads at maximum
        :param chunksize: How many searches per thread at minimum
        :param maximum: The maximum ids to return
        :param verbose: Verbose console log
        :return: List of ids in list[str] form
        """
        urls = []
        with multiprocessing.Pool(processes=parallels) as pool:
            if verbose:
                for url in tqdm.tqdm(pool.starmap(self._search_ids,
                                                  zip(radial_boundaries, itertools.repeat(maximum),
                                                      itertools.repeat(False)), chunksize=chunksize),
                                     total=len(radial_boundaries), unit='url', colour='green'):
                    urls.append(url)
            else:
                urls = pool.starmap(self._search_ids,
                                    zip(radial_boundaries, itertools.repeat(maximum), itertools.repeat(verbose)),
                                    chunksize=chunksize)
        if len(urls) <= 0:
            return []
        return urls

    def _search_ids(self, radial_bounds, maximum, verbose):
        return self.search_ids(radial_bounds, maximum=maximum, verbose=verbose)

    def search_ids(self, radial_bounds: tuple[Location, Location], *, maximum: int | None = None,
                   verbose: int | None = None) -> list[str]:
        """
        Search for IDs in specified bounds
        :param radial_bounds: Tuple of structure (center, radius)
        :param maximum: The maximum ids to return
        :param verbose: Verbose console log
        :return: List of ids in list[str] form
        """
        boundary = [radial_bounds[0].longitude_degrees - radial_bounds[1].longitude_degrees,
                    radial_bounds[0].latitude_degrees - radial_bounds[1].latitude_degrees,
                    radial_bounds[0].longitude_degrees + radial_bounds[1].longitude_degrees,
                    radial_bounds[0].latitude_degrees + radial_bounds[1].latitude_degrees]

        if verbose:
            print("Searching...")
        url_imagesearch = (self.METADATA_ENDPOINT + '/images?fields=id&bbox={},{},{},{}'
                           .format(boundary[0], boundary[1], boundary[2], boundary[3]))
        imagesearch_response = requests.get(url_imagesearch, headers=self.__headers)
        imagesearch_json = imagesearch_response.json()

        if not imagesearch_json or len(imagesearch_json) <= 0:  # If response is empty or no hits:
            return []

        maximum = len(imagesearch_json['data']) if maximum is None else maximum
        return [data['id'] for data in imagesearch_json['data'][:maximum]]

    def download_images(self, ids: list[str], *, parallels: int | None = None, chunksize: int = 1,
                        verbose: bool = False) -> list[MapillaryResponse]:
        """
        Parallel download for images with given ids
        :param ids: list[str] of all Ids to Mapillary Street View pictures
        :param parallels: How many download threads at maximum
        :param chunksize: How many downloads per thread at minimum
        :param verbose: Verbose console log
        :return: List of MapillaryResponses for downloaded images
        """
        images = []
        with multiprocessing.Pool(processes=parallels) as pool:
            if verbose:
                for image in tqdm.tqdm(pool.imap_unordered(self._download, ids, chunksize=chunksize),
                                       total=len(ids), unit='img', colour='green'):
                    images.append(image)
            else:
                images = pool.imap_unordered(self._download, ids, chunksize=chunksize)

        return images
