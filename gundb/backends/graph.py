from .resolvers import *
import json
from ..consts import *

class PutRequest:
    def __init__(self, soul, key, value, state, graph):
        self.soul = soul
        self.key = key
        self.value = value
        self.state = state
        self.graph = graph

    def dispatch(self, func):
        func(self.soul, self.key, self.value, self.state, self.graph)

    def node_added(self, node_resolver):
        assert(isinstance(self.value, dict) and '#' in self.value)
        return node_resolver[self.value['#']]

    def node_removed(self, node_resolver):
        if self.key in self.graph[self.soul] and is_reference(self.graph[self.soul][self.key]):
            return node_resolver[self.graph[self.soul][self.key]['#']]
        else:
            return None

class Node:
    def __init__(self, soul):
        self.soul = soul
        self.active = False
        self.requests = []
        self.children = []

    def apply_to_subtree(self, func, node_resolver):
        for e in self.requests:
            self.apply_changes(e, node_resolver)
            e.dispatch(func)
        self.apply_to_children(func, node_resolver)
    
    def apply_to_children(self, func, node_resolver):
        for child in self.children:
            child.apply_to_subtree(func, node_resolver)

    def add_put_request(self, req):
        self.requests.append(req)

    def extract_children(self, soul_obj, nodes):
        for k, v in soul_obj.items():
            if is_reference(k):
                self.children.append(node_resolver[v['#']])

    def apply_changes(self, req, node_resolver):
        node_added = req.node_added(node_resolver)
        node_removed = req.node_removed(node_resolver)
        if node_removed and node_removed in self.children:
            self.children.remove(node_removed)
        self.children.append(node_added)

class Graph:
    def __init__(self, graph):
        self.graph = graph
        self.nodes = {}
        self.initialize_nodes()

    def process_ref_diffs(self, diffs, func):
        for soul, node in diffs.items():
            for k, v in node.items():
                if k != METADATA:
                    self.nodes[soul].add_put_request(PutRequest(soul, k, v, diffs[soul][METADATA][STATE][k], self.graph))

        for soul, node in diffs.items():
            if is_root_soul(soul):
                self.nodes[soul].apply_to_subtree(func, self.nodes)

    def initialize_nodes(self):
        for k, v in self.graph.items():
            self.nodes[k] = Node(k)
        for k, v in self.graph.items():
            self.nodes[k].extract_children(v, self.nodes)

    def get_node_by_soul(self, soul):
        return self.nodes[soul]
