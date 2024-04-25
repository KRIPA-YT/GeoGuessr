from sys import argv
from geo import *


def main():
    api = mapillary_api.MapillaryAPI(argv[1])
    # Somewhere in Heidelberg, Germany
    responses = api.search(49.395665034392536, 8.599463334284934,
                           0.00025, 0.00025, parallels=20)
    print(f'Total Images: {len(responses)}')
    for i, response in enumerate(responses):
        picture = response.get_picture()
        dimension = picture.size
        coordinates = response.get_coordinates()
        print('#{:2.0f} {}x{}   {:<18} {:<18}'
              .format(i,
                      dimension[0], dimension[1],
                      str(coordinates[0]) + "°N", str(coordinates[1]) + "°E"))


if __name__ == "__main__":
    main()
