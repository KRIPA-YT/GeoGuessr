from mapillary_api import *
from PIL import Image
from sys import argv


def main():
    api = MapillaryAPI(argv[1])
    # Somewhere in Antwerp, Belgium
    responses = api.search(51.1543669, 4.4436676, 0.00025, 0.00025)
    print(f'Total Images: {len(responses)}')
    for response in responses:
        picture = response.get_picture()
        print(f'Picture Dimensions: {picture.size}')
        print(response.get_coordinates())


if __name__ == "__main__":
    main()
