import uuid
import string

class UID(object):
    all_chars = string.digits + string.ascii_letters

    def __init__(self):
        self.int = uuid.uuid4().int
        self.str = self._calculate_str()

    def _calculate_str(self):
        rval = ''
        val = self.int
        while len(rval) < 11:
            dm = divmod(val, 62)
            rval = self.all_chars[dm[1]] + rval
            val = dm[0]
        return rval

def new_uid():
    return UID().str
