import requests
import json


class MapillaryResponse:
    def __init__(self, id, url, timestamp, sequence):
        self.id = id
        self.url = url
        self.timestamp = timestamp
        self.sequence = sequence

    def get_picture(self):
        img_data = requests.get(self.url).content
        with open('response.jpg', 'wb') as handler:
            handler.write(img_data)


class MapillaryAPI:
    __metadata_endpoint = "https://graph.mapillary.com"

    def __init__(self, token):
        self.__token = token
        self.__headers = {"Authorization": "OAuth {}".format(token)}

    def search(self, latitude_degrees, longitude_degrees, latitude_distance_degrees, longitude_distance_degrees):
        url_imagesearch = (self.__metadata_endpoint + '/images?fields=id&bbox= {},{},{},{}'
                           .format(longitude_degrees - longitude_distance_degrees,
                                   latitude_degrees - latitude_distance_degrees,
                                   longitude_degrees + longitude_distance_degrees,
                                   latitude_degrees + latitude_degrees))
        response_imagesearch = requests.get(url_imagesearch, headers=self.__headers)
        imagesearch_json = response_imagesearch.json()
        print("Images found:" + str(len(imagesearch_json['data'])))

        images = []

        for image in imagesearch_json['data']:
            # DOCS: https://www.mapillary.com/developer/api-documentation/#image
            image_url = self.__metadata_endpoint + '/{}?fields=id,thumb_2048_url,captured_at,sequence'.format(
                image['id'])
            image_response = requests.get(image_url, headers=self.__headers)
            image_json = image_response.json()
            images.append(MapillaryResponse(image_json['id'], image_json['thumb_2048_url'],
                                            image_json['captured_at'], image_json['sequence']))
