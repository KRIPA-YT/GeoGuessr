import math
import re
from typing import Self


class Location:
    __create_key = object()

    @classmethod
    def from_degrees(cls, latitude, longitude):
        return Location(cls.__create_key, latitude, longitude)

    @classmethod
    def from_string(cls, string):
        dms = re.search('((\d*)°(\d*)\'([\d\.]*)\")[NS]( )*((\d*)°(\d*)\'([\d\.]*)\")[EW]', string)
        if dms:
            coordinates = re.findall('((\d*\.)?\d+)', string)
            coordinates = [coordinate[0] for coordinate in coordinates]
            lat_degrees, lat_minutes, lat_seconds, \
                lon_degrees, lon_minutes, lon_seconds = coordinates
            directions = re.findall('[NSEW]{1}', string)
            lat_direction, lon_direction = directions
            latitude = cls.__dms_to_decimal_degrees(lat_degrees, lat_minutes, lat_seconds, lat_direction)
            longitude = cls.__dms_to_decimal_degrees(lon_degrees, lon_minutes, lon_seconds, lon_direction)
            return cls.from_degrees(latitude, longitude)

    @classmethod
    def zero(cls):
        return cls.from_degrees(0, 0)

    def __init__(self, create_key, latitude_degrees, longitude_degrees):
        assert (create_key == Location.__create_key), \
            "Location objects must be created using Location.from*"
        self.__latitude_degrees = latitude_degrees
        self.__longitude_degrees = longitude_degrees

    @property
    def coordinates_degrees(self):
        return self.__latitude_degrees, self.__longitude_degrees

    @property
    def latitude_degrees(self):
        return self.__latitude_degrees

    @property
    def longitude_degrees(self):
        return self.__longitude_degrees

    def __repr__(self):
        latitude_sign, latitude_degrees, latitude_minutes, latitude_seconds \
            = self.__unsigned_decimal_degrees_to_dms(self.latitude_degrees)
        longitude_sign, longitude_degrees, longitude_minutes, longitude_seconds \
            = self.__unsigned_decimal_degrees_to_dms(self.longitude_degrees)
        return (f"{latitude_degrees:.0f}°{latitude_minutes:.0f}'"
                f"{latitude_seconds:.2f}\"{'N' if latitude_sign else 'S'} "
                f"{longitude_degrees:.0f}°{longitude_minutes:.0f}'"
                f"{longitude_seconds:.2f}\"{'E' if longitude_sign else 'W'}")

    def distance_km(self, other: Self):
        earth_radius_km = 6371
        difference_lat = math.radians(other.latitude_degrees - self.latitude_degrees)
        difference_lon = math.radians(other.longitude_degrees - self.longitude_degrees)
        a = (math.sin(difference_lat / 2) * math.sin(difference_lat / 2)
             + math.cos(math.radians(self.latitude_degrees)) * math.cos(math.radians(other.latitude_degrees))
             * math.sin(difference_lon / 2) * math.sin(difference_lon / 2))

        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = earth_radius_km * c
        return distance

    @staticmethod
    def __unsigned_decimal_degrees_to_dms(decimal_degrees):
        sign = decimal_degrees > 0
        minutes, seconds = divmod(abs(decimal_degrees) * 3600, 60)
        degrees, minutes = divmod(minutes, 60)
        return sign, degrees, minutes, seconds

    @staticmethod
    def __dms_to_decimal_degrees(degrees, minutes, seconds, direction):
        return (float(degrees) + float(minutes) / 60 + float(seconds) / (60 * 60)) * (
            -1 if direction in ['W', 'S'] else 1)
