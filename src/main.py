from sys import argv
from geo.mapillary_api import MapillaryAPI
from geo.location import Location


def main():
    api = MapillaryAPI(argv[1])
    # Somewhere in Heidelberg, Germany
    responses = api.search(Location.from_degrees(49.395665034392536, 8.599463334284934),
                           Location.from_degrees(0.00025, 0.00025), parallels=20, verbose=True)
    print(f'Total Images: {len(responses)}')
    for i, response in enumerate(responses):
        picture = response.get_picture()
        dimension = picture.size
        loc = response.get_location()
        print(f'#{i:2.0f} {dimension[0]}x{dimension[1]}   {loc}')


if __name__ == "__main__":
    main()