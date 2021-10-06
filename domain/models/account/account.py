

class AccountVO(object):
    
    def __init__(self, name: str, id: str, password: str):
        self._name = name
        self._id = id
        self._password = password
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def id(self) -> str:
        return self._id
    
    @property
    def password(self) -> str:
        return self._password
    
    def __eq__(self, other: object):
        if not isinstance(other, AccountVO):
            return False
        if self.name == other.name and self.id == other.id and self.password == other.password:
            return True
        return False
    
    def __repr__(self):
        return "<AccountVO: name=%r, id=%r>" % (self.name, self.id)
    