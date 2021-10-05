from typing import List
from .disk import diskVO


class ServerVO(object):
    def __init__(self, address: str, name: str, disks: List[diskVO]):
        self._set_address(address)
        self._set_name(name)
        self._set_disks(disks)

    def _set_address(self, address: str):
        self._address = address

    def _set_name(self, name: str):
        self._name = name

    def _set_disks(self, disks: List[diskVO]):
        self._disks = disks
    
    @property
    def address(self) -> str:
        return self._address
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def disks(self) -> List[diskVO]:
        return self._disks

    def __eq__(self, other: object):
        if not isinstance(other, ServerVO):
            return False
        if self.address == other.address and self.name == other.name:
            if len(self.disks) > 0 and len(other.disks):
                return sorted(self.disks) == sorted(other.disks)
        return False
    
    def __repr__(self):
        return "<ServerVO: address=%r, name=%r, disks=%r>" % (self.address, self.name, self.disks)