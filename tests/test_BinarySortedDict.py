import os
import sys
test_directory = os.path.dirname(__file__)
src_dir = os.path.join(test_directory, '..', 'src')
sys.path.append(src_dir)
import BinarySortedDict as src
import numpy as np
TOL = 0.00001

def test_bst():
    bst = src.BinarySearchTree()
    assert bst._root is None and bst._left is None and bst._right is None
    assert bst.is_empty()
    bst = src.BinarySearchTree(10)
    assert bst._root == 10 and bst._left.is_empty() and bst._right.is_empty()
    assert not bst.is_empty()
    bst2 = src.BinarySearchTree(10)
    assert bst == bst2
    bst2 = src.BinarySearchTree(11)
    assert bst != bst2
    bst.insert(11)
    bst.insert(9)
    assert bst._left == src.BinarySearchTree(9) and bst._right == src.BinarySearchTree(11)
    bst.insert(6)
    bst.insert(8)
    bst.insert(7)
    bst.insert(4)
    bst.insert(5)
    assert bst._left._left._root == 6 and \
           bst._left._left._right._root == 8 and \
           bst._left._left._right._right == src.BinarySearchTree() and \
           bst._left._left._right._left == src.BinarySearchTree(7) and \
           bst._left._left._left._root == 4 and \
           bst._left._left._left._left == src.BinarySearchTree() and \
           bst._left._left._left._right == src.BinarySearchTree(5)
    assert bst.in_order_traversal() == [4,5,6,7,8,9,10,11]
    bst.delete(6)
    bst_check = src.BinarySearchTree(10)
    bst_check.insert(11)
    bst_check.insert(9)
    bst_check.insert(5)
    bst_check.insert(4)
    bst_check.insert(8)
    bst_check.insert(7)
    assert bst == bst_check
    target = 6
    closest_below = bst.get_closest_below(target)
    closest_above = bst.get_closest_above(target)
    assert closest_below == 5 and closest_above == 7

def test_bsd():
    bsd = src.BinarySortedDict()
    assert str(bsd) == "{}"
    bsd[5] = 0.1
    bsd[6] = 0.2
    assert str(bsd) == "{5: 0.1, 6: 0.2}"
    assert 5 in bsd
    assert 4 not in bsd
    assert len(bsd) == 2
    assert bsd[5] == 0.1
    assert bsd[6] != 5
    bsd2 = src.BinarySortedDict()
    bsd2[5] = 0.1
    bsd2[6] = 0.2
    assert bsd == bsd2
    assert bsd.return_sorted_list() == [5,6]
    bsd[1] = 6
    assert bsd.get_closest_keys(3) == [1,5]
