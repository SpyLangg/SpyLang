from values.value import Value

class RangeValue(Value):
    """
    Represents a range (start..end) as an iterable value in SpyLang.
    """
    def __init__(self, start, end):
        super().__init__()
        self.start = start
        self.end = end

    def iter(self):
        """
        Returns an iterator for the range.
        """
        return iter(range(self.start, self.end + 1))  

    def __repr__(self):
        return f"Range({self.start}..{self.end})"

