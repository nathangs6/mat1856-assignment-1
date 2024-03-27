from typing import Type, Optional
class BinarySearchTree:
    _root: Optional[int]
    _left: Optional['BinarySearchTree']
    _right: Optional['BinarySearchTree']
    def __init__(self, root: int = None):
        if root is None:
            self._root = None
            self._left = None
            self._right = None
        else:
            self._root = root
            self._left = BinarySearchTree()
            self._right = BinarySearchTree()

    def is_empty(self):
        return self._root is None

    def __eq__(self, bst: Type['BinarySearchTree']):
        if self._root != bst._root:
            return False
        if self._left != bst._left:
            return False
        if self._right != bst._right:
            return False
        return True

    def in_order_traversal(self):
        result = []
        if not self.is_empty():
            result.extend(self._left.in_order_traversal())
            result.append(self._root)
            result.extend(self._right.in_order_traversal())
        return result

    def __iter__(self):
        return iter(self.in_order_traversal())

    def insert(self, val):
        if self._root is None:
            self._root = val
            self._left = BinarySearchTree()
            self._right = BinarySearchTree()
        elif val < self._root:
            self._left.insert(val)
        elif val > self._root:
            self._right.insert(val)
        else:
            self._key = val

    def get_closest_below(self, item):
        closest = None
        current = self
        while current._root:
            if current._root < item:
                closest = current._root
                current = current._right
            else:
                current = current._left
        return closest

    def get_closest_above(self, item):
        closest = None
        current = self
        while current._root:
            if current._root > item:
                closest = current._root
                current = current._left
            else:
                current = current._right
        return closest

    def _extract_max(self):
        if self._right.is_empty():
            max_item = self._root
            self._root, self._left, self._right = \
                self._left._root, self._left._left, self._left._right
            return max_item
        else:
            return self._right._extract_max()

    def _delete_root(self):
        if self._left.is_empty() and self._right.is_empty():
            self._root = None
            self._left = None
            self._right = None
        elif self._left.is_empty():
            self._root = self._right._root
            self._left = self._right._left
            self._right = self._right._right
        elif self._right.is_empty():
            self._root = self._left._root
            self._left = self._left._left
            self._right = self._left._right
        else:
            self._root = self._left._extract_max()

    def delete(self, item):
        if self.is_empty():
            pass
        elif self._root == item:
            self._delete_root()
        elif item < self._root:
            self._left.delete(item)
        else:
            self._right.delete(item)


class BinarySortedDict:
    d: dict
    root: Optional[BinarySearchTree]
    def __init__(self):
        self.d = {}
        self.root = BinarySearchTree()

    def __eq__(self, bsd: Type['BinarySortedDict']):
        return self.d == bsd.d

    def __str__(self):
        return str(self.d)

    def __len__(self):
        return len(self.d)

    def __contains__(self, key):
        return key in self.d

    def __getitem__(self, key):
        if key in self.d:
            return self.d[key]
        else:
            return self.linearly_interpolate(key)

    def __setitem__(self, key, item):
        if key not in self.d:
            self.root.insert(key)
        self.d[key] = item

    def return_sorted_list(self):
        return list(self.root)

    def sorted_key_vals(self):
        x = self.return_sorted_list()
        y = []
        for a in x:
            y.append(self[a])
        return x, y

    def get_closest_keys(self, item):
        return [self.root.get_closest_below(item), self.root.get_closest_above(item)]

    def linearly_interpolate(self, key) -> float:
        if self.d == {}: return None
        if key in self.d: return self.d[key]
        closest_keys = self.get_closest_keys(key)
        x0 = closest_keys[0]
        x1 = closest_keys[1]
        if x0 is None:
            return self.d[x1]
        if x1 is None:
            return self.d[x0]
        y0 = self.d[x0]
        y1 = self.d[x1]
        return y0 + (y1 - y0) * (key - x0) / (x1 - x0)
