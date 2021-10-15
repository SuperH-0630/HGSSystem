from type_ import *


class HGSLocation:
    def __init__(self, location: location_t):
        self.loc: location_t = location

    def get_location(self) -> location_t:
        return self.loc


hgs_location_t: TypeAlias = Union[HGSLocation, location_t]
