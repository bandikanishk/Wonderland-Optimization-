from math import inf
class Pathqueue:

    def __init__(self):
        self._data = []

    def push(self, item):
        self._data.append(item)

    def pop(self):
        smallest_item = None
        smallest_time = inf
        for i in self._data:
            if i[1] < smallest_time:
                smallest_time = i[1]
                smallest_item = i
        self._data.remove(smallest_item)
        return smallest_item

    def is_empty(self):
        return len(self._data) == 0
