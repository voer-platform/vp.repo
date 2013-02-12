# VOER CORE - Repository
# Initialized by Ha Pham - 08/01/2013


class MaterialBase(object):
    """docstring for MaterialBase"""

    def __init__(self):
        super(MaterialBase, self).__init__()
        #self.arg = arg
        
    def checkIn(self):
        """docstring for checkIn"""
        pass


class Repository(object):
    """docstring for Repository"""

    __materials = []

    def __init__(self, arg):
        super(Repository, self).__init__()
        self.arg = arg
        
    def checkInMaterial(self, material):
        """docstring for checkIn"""
        pass

    def checkOut(self, revision=''):
        """docstring for checkOut"""
        pass

    def performSearch(self):
        """docstring for performSearch"""
        pass
    
