import numpy as np


def get_center_from_degrees(lat1, lon1):
    if len(lat1) <= 0:
        return False

    num_coords = len(lat1)

    X = 0.0
    Y = 0.0
    Z = 0.0

    for i in range (len(lat1)):
        lat = lat1[i] * np.pi / 180
        lon = lon1[i] * np.pi / 180

        a = np.cos(lat) * np.cos(lon)
        b = np.cos(lat) * np.sin(lon)
        c = np.sin(lat)

        X += a
        Y += b
        Z += c

    X /= num_coords
    Y /= num_coords
    Z /= num_coords

    lon = np.arctan2(Y, X)
    hyp = np.sqrt(X * X + Y * Y)
    lat = np.arctan2(Z, hyp)

    newX = (lat * 180 / np.pi)
    newY = (lon * 180 / np.pi)
    return newX, newY


def calculate_centroid_for_twitter_bounding_box(coordinates: list):
    lat1 = [coordinate[0] for coordinate in coordinates]
    lon1 = [coordinate[1] for coordinate in coordinates]
    return get_center_from_degrees(lat1, lon1)


if __name__ == '__main__':
    coords = [
        [
            78.028739,
            27.841366
        ],
        [
            78.028739,
            27.963932
        ],
        [
            78.148531,
            27.963932
        ],
        [
            78.148531,
            27.841366
        ],
        [
            78.028739,
            27.841366
        ]
    ]

    print(calculate_centroid_for_twitter_bounding_box(coords))
