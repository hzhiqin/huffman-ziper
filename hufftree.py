class HuffTree:
    def __lt__(self, other):
        return self.root.freq < other.root.freq

    def __eq__(self, other):
        return self.root.freq == other.root.freq

    def __init__(self, *args):
        if len(args) == 1:
            if isinstance(args[0], LeafNode):
                self._root = args[0]
            else:
                raise TypeError
        elif len(args) == 2:
            self._root = NonLeafNode(args[0].root, args[1].root)

    @staticmethod
    def build_tree(freq_book: dict):
        from queue import PriorityQueue
        queue = PriorityQueue()
        for k, v in freq_book.items():
            queue.put(HuffTree(LeafNode(k, v)))
        while queue.qsize() > 1:
            t1 = queue.get()
            t2 = queue.get()
            queue.put(HuffTree(t1, t2))
        return queue.get()

    def get_codebook(self):
        codebook = {}
        wl = [(self.root, "")]
        while wl:
            cur = wl.pop()
            if cur[0].is_leaf:
                codebook[cur[0].value] = cur[1]
            else:
                wl.append((cur[0].right, cur[1] + "1"))
                wl.append((cur[0].left, cur[1] + "0"))
        return codebook

    @property
    def root(self):
        return self._root


class HuffNode:
    def freq(self):
        raise NotImplementedError

    def is_leaf(self):
        raise NotImplementedError


class LeafNode(HuffNode):
    def __init__(self, value, freq):
        super()
        self._value = value
        self._freq = freq

    @property
    def is_leaf(self):
        return True

    @property
    def freq(self):
        return self._freq

    @property
    def value(self):
        return self._value


class NonLeafNode(HuffNode):
    def __init__(self, left, right):
        super()
        self._freq = left.freq + right.freq
        self._left = left
        self._right = right

    @property
    def freq(self):
        return self._freq

    @property
    def is_leaf(self):
        return False

    @property
    def left(self):
        return self._left

    @property
    def right(self):
        return self._right
