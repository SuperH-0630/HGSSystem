from .type_ import *


class HGSLocation:
    def __init__(self, location: location_t):
        self._loc: location_t = location

    def get_location(self) -> location_t:
        return self._loc


hgs_location_t = "hgs_location_t", Union[HGSLocation, location_t]
