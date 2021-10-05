

class DiskVO(object):
    def __init__(self, id: str) -> None:
        self._set_id(id)

    def _set_id(self, id: str):
        self._id = id

    @property
    def id(self) -> str:
        return self._id
    
    def __eq__(self, other: object):
        if not isinstance(other, DiskVO):
            return False
        if self.id == other.id:
            return True
        return False
    
    def __repr__(self):
        return "<DiskVO: id=%r>" % (self.id)
