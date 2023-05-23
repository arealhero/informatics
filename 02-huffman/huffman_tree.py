import bisect
from serialization import open_serializer

class Node:
    def __init__(self, value, left = None, right = None):
        self.value = value
        self.left = left
        self.right = right

    def is_leaf(self):
        return not (self.left or self.right)

class NodeHelper:
    def __init__(self, node, frequency):
        self.node = node
        self.frequency = frequency

    def __lt__(self, other):
        return self.frequency < other.frequency

class HuffmanTree:
    def __init__(self):
        self.tree = None
        self.frequencies = []

    def build(self, frequencies):
        self.frequencies = frequencies

        nodes = [NodeHelper(Node(i), frequencies[i]) for i in range(256) if
                 frequencies[i] != 0]
        nodes.sort()

        while len(nodes) != 1:
            left = nodes[0]
            right = nodes[1]

            nodes = nodes[2:]
            bisect.insort(nodes, NodeHelper(Node(None, left.node, right.node),
                                            left.frequency + right.frequency))

        self.tree = nodes[0].node

    def to_dict(self):
        result = {}
        HuffmanTree.__generate_codes(self.tree, result)
        return result

    def decode_one_letter(self, serializer):
        node = self.tree
        while True:
            if node is None:
                raise RuntimeError('Unknown code found')

            if node.is_leaf():
                return node.value

            bit = serializer.read_bit()
            if bit == '0':
                node = node.left
            else:
                node = node.right

    def serialize(self, serializer):
        HuffmanTree.__write_paths(self.tree, serializer)

    @staticmethod
    def deserialize(deserializer):
        tree = HuffmanTree()
        tree.tree = HuffmanTree.__read_node(deserializer)
        return tree

    @staticmethod
    def __read_node(deserializer):
        bit = deserializer.read_bit()

        if bit == '1':
            value = deserializer.read_int8()
            return Node(value)
        else:
            left = HuffmanTree.__read_node(deserializer)
            right = HuffmanTree.__read_node(deserializer)
            return Node(None, left, right)

    @staticmethod
    def __write_paths(node, serializer):
        if not node:
            return

        if node.is_leaf():
            serializer.send_bits(f'1{node.value:08b}')
            return

        serializer.send_bits('0')
        if node.left:
            HuffmanTree.__write_paths(node.left, serializer)

        if node.right:
            HuffmanTree.__write_paths(node.right, serializer)

    @staticmethod
    def __generate_codes(node, codes, code=''):
        if not node:
            return

        HuffmanTree.__generate_codes(node.left, codes, code+'0')
        if node.is_leaf():
            codes[node.value] = code
        HuffmanTree.__generate_codes(node.right, codes, code+'1')

