"""
The Graph module manages a graph of nodes and applies put requests on these nodes in dfs order.

A node represents a soul in the sent graph.
"""

from .resolvers import *
import json
from ..consts import *

class PutRequest:
    """
        PutRequst contains data about a pull request that is dispatched later using dispatch method.

        Args:
            soul  (str) : The soul to which the change is applied.
            key   (str) : The key of the property in the soul object.
            value (str) : The new value associated with the key
            state (dict): The state.
            graph (dict): The updated graph sent by gundb.
    """
    def __init__(self, soul, key, value, state, graph):
        self.soul = soul
        self.key = key
        self.value = value
        self.state = state
        self.graph = graph

    def dispatch(self, func):
        """
        Calls the sent function with self attributes as arguments.
        """
        func(self.soul, self.key, self.value, self.state, self.graph)

    def node_added(self, node_resolver):
        """
        Returns the node object that is added as a result of this put request.

        Args:
            node_resolver (dict): A mapping between souls and node objects.
        """
        assert(isinstance(self.value, dict) and '#' in self.value)
        return node_resolver[self.value['#']]

    def node_removed(self, node_resolver):
        """
        Returns the node object that is deleted as a result of this put request.

        Args:
            node_resolver (dict): A mapping between souls and node objects.
        """
        if self.key in self.graph[self.soul] and is_reference(self.graph[self.soul][self.key]):
            return node_resolver[self.graph[self.soul][self.key]['#']]
        else:
            return None

class Node:
    """
    Node object represents a soul in the graph.
    
    Attributes:
        soul     (str)               : The soul that the node represents.
        requests (list[PutRequests]) : Requests that modifies some key belonging to the soul object directly.
        children (list[Node])        : Nodes that are referenced in some key belonging to the soul object directly.
    """
    def __init__(self, soul):
        self.soul = soul
        self.requests = []
        self.children = []

    def apply_to_subtree(self, func, node_resolver):
        """
        Dispatches the put requests in this node and the subtree of this node.

        Args:
            func          (function) : The function that handles a put request.
            node_resolver (dict)     : Maps between the souls and the nodes.
        """
        for e in self.requests:
            e.dispatch(func)
        self.apply_to_children(func, node_resolver)
    
    def apply_to_children(self, func, node_resolver):
        """
        Dispatches the put requests in the subtree (not including self).

        Args:
            func          (function) : The function that handles a put request.
            node_resolver (dict)     : Maps between the souls and the nodes.
        """
        for child in self.children:
            child.apply_to_subtree(func, node_resolver)

    def add_put_request(self, req):
        """
        Appends a put requests to the node.

        Args:
            req (PutRequest): The request to be added.
        """
        self.requests.append(req)

    def extract_children(self, soul_obj, node_resolver):
        """
        Extracts the children of the soul_obj and stores them in self.children.

        Args:
            soul_obj      (dict): The object associated with soul in the graph (graph[soul]).
            node_resolber (dict): Mapping between souls and nodes.
        """
        for k, v in soul_obj.items():
            if k != '_' and is_reference(v):
                self.children.append(node_resolver[v['#']])

class Graph:
    """
    Graph object keeps track of all nodes in the graph and applies the put requests in dfs order starting from root object.

    The main objective is not to apply put requests except for souls referenced in the graph.

    Attributes:
        graph (dict): The graph sent by GUN.
        nodes (dict): Mapping between souls and nodes.
    """
    def __init__(self, graph):
        self.graph = graph
        self.nodes = {}
        self.initialize_nodes()

    def process_ref_diffs(self, diffs, func):
        """
        Applies diffs in dfs order starting from root objects.
        """
        for soul, node in diffs.items():
            for k, v in node.items():
                if k != METADATA:
                    self.nodes[soul].add_put_request(PutRequest(soul, k, v, diffs[soul][METADATA][STATE][k], self.graph))

        for soul, node in diffs.items():
            if is_root_soul(soul):
                self.nodes[soul].apply_to_subtree(func, self.nodes)

    def initialize_nodes(self):
        """
        Initializee the nodes from the graph and build the relations between them.
        """
        for k, v in self.graph.items():
            self.nodes[k] = Node(k)
        for k, v in self.graph.items():
            self.nodes[k].extract_children(v, self.nodes)
