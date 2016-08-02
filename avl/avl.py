import sys
assert sys.version[0] == '3'


class Stack(object):

    'A first-in last-out datastructure'

    def __init__(self, starts=None):
        self.front = None
        if starts:
            for val in starts:
                self.push(val)

    def __bool__(self):
        return self.front is not None

    def push(self, val):
        item = StackItem(val, following=self.front)
        self.front = item

    def pop(self):
        popped = self.front
        if popped is None:
            return None

        self.front = popped.following
        return popped.obj

    def peek(self):
        return self.front.obj

    def empty(self):
        return self.front is None

    def reverse(self):
        l = list(self)
        for x in l:
            self.push(x)

    def __iter__(self):
        item = self.pop()
        while item is not None:
            yield item
            item = self.pop()


class StackItem(object):
    __slots__ = ['obj', 'following']

    def __init__(self, obj, following=None):
        self.obj = obj
        self.following = following


class AVLNode(object):

    'A node in a self-balancing tree'

    def __init__(self, key):
        self.key = key
        self.height = 0
        self.left = None
        self.right = None
        self.parent = None

    def __repr__(self):
        return 'AVLNode({})'.format(self.key)

    def is_leaf(self):
        return self.left is None and self.right is None

    def is_bst(self):
        if self.left is not None and not self.left.key < self.key:
            return False
        elif self.right is not None and not self.right.key > self.key:
            return False
        else:
            return True

    def verify(self):
        verfied = self.is_balanced() and self.is_bst()
        parcheck = True
        if self.parent is None:
            pass
        elif self.key > self.parent.key:
            parcheck = self is self.parent.right
        elif self.key < self.parent.key:
            parcheck = self is self.parent.left

        return verfied and parcheck

    def update_height(self):
        lheight = self.left.height if self.left is not None else 0
        rheight = self.right.height if self.right is not None else 0
        self.height = max(lheight, rheight) + 1

    @property
    def children(self):
        return self.left, self.right

    @children.setter
    def children(self, value):
        self.left, self.right = value

    @property
    def balance(self):
        lefth = (self.left.height) if self.left is not None else 0
        righth = (self.right.height) if self.right is not None else 0
        return righth - lefth

    def is_balanced(self):
        return -1 <= self.balance <= 1


class AVLTree(object):

    def __init__(self):
        self.root = None

    @staticmethod
    def from_keys(keys):
        tree = AVLTree()
        for key in keys:
            tree.insert(key)

        return tree

    def __contains__(self, key):
        node = self.root
        while node:
            if key > node.key:
                node = node.right
            elif key < node.key:
                node = node.left
            elif key == node.key:
                return True

        return False
        
    def traverse(self, reverse=False):
        if not self.root:
            return

        if reverse:
            yield from self._traverse_reverse()
        else:
            yield from self._traverse()

    def _traverse(self):
        s = Stack()
        node = self.root
        while (not s.empty()) or (node is not None):
            if node is not None:
                s.push(node)
                node = node.left
            else:
                node = s.pop()
                yield node 
                node = node.right

    def _traverse_reverse(self):
        s = Stack()
        node = self.root
        while (not s.empty()) or (node is not None):
            if node is not None:
                s.push(node)
                node = node.right
            else:
                node = s.pop()
                yield node 
                node = node.left

    def size(self):
        return sum(1 for node in self.traverse())

    def keys(self):
        yield from (node.key for node in self.traverse())

    def find_node(self, key):
        node = self.root
        while node is not None:

            if node.key == key:
                return node

            elif key < node.key:
                node = node.left
            elif key > node.key:
                node = node.right
        raise KeyError('Node not found!')

    def path_to_root(self, key):
        s = Stack()
        cur_node = self.root
        while cur_node:
            s.push(cur_node)
            if key > cur_node.key:
                cur_node = cur_node.right
            elif key < cur_node.key:
                cur_node = cur_node.left
            elif key == cur_node.key:
                return s
        raise KeyError

    def path_to_node(self, key):
        s = self.path_to_root(key)
        s.reverse()
        return s

    def insert(self, key):
        new_node = AVLNode(key)

        if self.root is None:
            self.root = new_node
            return

        cur_node = self.root
        while True:
            if new_node.key > cur_node.key:
                if cur_node.right is not None:
                    cur_node = cur_node.right
                else:
                    cur_node.right = new_node
                    new_node.parent = cur_node
                    break

            elif new_node.key < cur_node.key:
                if cur_node.left is not None:
                    cur_node = cur_node.left
                else:
                    cur_node.left = new_node
                    new_node.parent = cur_node
                    break
            else:
                raise ValueError('fart')

        parent = new_node

        while parent:
            self.rebalance_node(parent)
            parent = parent.parent

    def rebalance_node(self, node):
        node.update_height()

        if node.is_balanced():
            return

        if node.balance > 1:
            if node.right is not None and node.right.balance < 0:
                new_root = node.right.left
                rotate_double_left(node)

            else:
                new_root = node.right
                rotate_left(node)

        elif node.balance < -1:
            if node.left is not None and node.left.balance > 0:
                new_root = node.left.right
                rotate_double_right(node)

            else:
                new_root = node.left
                rotate_right(node)

        else:
            pass
        if node is self.root:
            self.root = new_root


    def delete(self, key):
        if self.root is None:
            raise KeyError('Tree is empty')

        ancestors = self.path_to_root(key)
        node = ancestors.pop()


        if node.is_leaf():
            self.delleaf(node, ancestors)
        elif node.right is None:
            self.del1childl(node, ancestors)
        elif node.left is None:
            self.del1childr(node, ancestors)
        else:
            self.del2child(node, ancestors)

    def delleaf(self, node, ancestors):
        ancestor = ancestors.peek()
        if node is self.root:
            self.root = None
            return

        elif node.key > ancestor.key:
            ancestor.right = None
        else: 
            ancestor.left = None

        for ancestor in ancestors:
            self.rebalance_node(ancestor)

    def del1childl(self, node, ancestors):
        if self.root is node:
            self.root = node.left
            node.left.update_height()
            return

        ancestor = ancestors.peek()
        child = node.left
        child.parent = ancestor
        if child.key > ancestor.key:
            ancestor.right = child
        else:
            ancestor.left = child

        for ancestor in ancestors:
            self.rebalance_node(ancestor)

    def del1childr(self, node, ancestors):
        if self.root is node:
            self.root = node.right
            node.right.update_height()
        
        ancestor = ancestors.peek()
        child = node.right    
        child.parent = ancestor
        if child.key > ancestor.key:
            ancestor.right = child
        else:
            ancestor.left = child

        for ancestor in ancestors:
            self.rebalance_node(ancestor)

    def del2child(self, node, ancestors):
        # Find a replacement for the node to be deleted
        replacement = node.left
        while replacement.right:
            replacement = replacement.right

        path_to_replacement = self.path_to_root(replacement.key)
        path_to_replacement.pop() # Remove replacement from stack

        self.delete(replacement.key)

        # The parent of the node to be deleted
        direct_ancestor = ancestors.peek()
                
        replacement.children = node.children 
        replacement.parent = direct_ancestor
        replacement.update_height()

        if node is self.root:
            self.root = replacement
        
        elif replacement.key > direct_ancestor.key:
            direct_ancestor.right = replacement
        else:
            direct_ancestor.left = replacement

        for ancestor in path_to_replacement:
            self.rebalance_node(ancestor)

    def min_node(self, start=None):
        if not self.root:
            raise KeyError('Tree empty!')
        if not start:
            node = self.root
        else:
            node = start

        while node.left is not None:
            node = node.left

        return node

    def min(self):
        return self.min_node().key

    def max_node(self, start=None):
        if not self.root:
            raise KeyError('Tree empty!')
        if not start:
            node = self.root
        else:
            node = start

        while node.right is not None:
            node = node.right

        return node

    def max(self):
        return self.max_node().key

    def intersection(self, other):
        t1 = Stack(self.traverse(reverse=True))
        t2 = Stack(other.traverse(reverse=True))

        a, b = t1.pop(), t2.pop()

        ntree = AVLTree()
        while a is not None and b is not None:
            if a.key == b.key:
                ntree.insert(a.key)
                a, b = t1.pop(), t2.pop()
            elif a.key < b.key:
                a = t1.pop()
            else:
                b = t2.pop()

        return ntree

    def union(self, other):
        t1 = Stack(self.traverse(reverse=True))
        t2 = Stack(other.traverse(reverse=True))

        a, b = t1.pop(), t2.pop()

        ntree = AVLTree()

        while a is not None or b is not None:
            if a is None:
                ntree.insert(b.key)
                b = t2.pop()

            elif b is None:
                ntree.insert(a.key)
                a = t1.pop()

            elif a.key == b.key:
                ntree.insert(a.key)
                a, b = t1.pop(), t2.pop()

            elif a.key < b.key:
                ntree.insert(a.key)
                a = t1.pop()

            else:
                ntree.insert(b.key)
                b = t2.pop()

        return ntree

# Node manipulation functions


def rotate_right(root):
    pivot = root.left
    root.left = pivot.right
    if root.left is not None:
        root.left.parent = root

    pivot.right = root
    pivot.parent = root.parent
    root.parent = pivot

    if pivot.parent is None:
        pass
    elif pivot.parent.left is root:
        pivot.parent.left = pivot
    elif pivot.parent.right is root:
        pivot.parent.right = pivot

    root.update_height()
    pivot.update_height()


def rotate_left(root):

    pivot = root.right
    root.right = pivot.left

    if root.right is not None:
        root.right.parent = root

    pivot.left = root
    pivot.parent = root.parent
    root.parent = pivot

    if pivot.parent is None:
        pass
    elif pivot.parent.left is root:
        pivot.parent.left = pivot
    elif pivot.parent.right is root:
        pivot.parent.right = pivot
    else:
        raise KeyError
    root.update_height()
    pivot.update_height()


def rotate_double_left(root):
    rotate_right(root.right)
    rotate_left(root)


def rotate_double_right(root):
    rotate_left(root.left)
    rotate_right(root)
