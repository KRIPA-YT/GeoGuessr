class Location:
    __create_key = object()

    @classmethod
    def from_degrees(cls, latitude, longitude):
        return Location(cls.__create_key, latitude, longitude)

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

    @staticmethod
    def __unsigned_decimal_degrees_to_dms(decimal_degrees):
        sign = decimal_degrees > 0
        minutes, seconds = divmod(abs(decimal_degrees) * 3600, 60)
        degrees, minutes = divmod(minutes, 60)
        return sign, degrees, minutes, seconds
