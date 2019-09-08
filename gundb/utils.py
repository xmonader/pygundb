import time
import math
import uuid
from .consts import STATE, METADATA, SOUL


def stategen():
    N = 0
    D = 1000
    STATE_DRIFT = 0

    last = -math.inf

    while True:
        t = time.time()
        if last < t:
            N = 0
            last = t + STATE_DRIFT
        else:
            N + 1
            last = t + (N/D)  + STATE_DRIFT 
        yield last

state = stategen()
def get_current_state():
    return next(state)

def newuid():
    return str(uuid.uuid4())

def get_state(node):
    if METADATA in node and STATE in node[METADATA]:
        return node[METADATA][STATE]
    return {STATE:{}}

def get_state_of(node, key):
    s = get_state(node)
    return s.get(key, get_current_state()) #FIXME: should be 0?

def new_node(name, **kwargs):
    # node with meta
    node = {METADATA: {SOUL:name, STATE:{k:get_current_state() for k in kwargs}}, **kwargs}
    return node

def ensure_state(node):

    if STATE not in node[METADATA]:
        node[METADATA][STATE] = {k: get_current_state() for k in node if k != SOUL}
        node[METADATA][SOUL] = node["#"]
    return node

# conflict resolution algorithm 
def HAM(machine_state, incoming_state, current_state, incoming_value, current_value):
    # TODO: unify the result of the return
    # ADD UNIT TESTS TO COVER CASES
    if not incoming_state:
        incoming_state = 0
    if not current_state:
        current_state = 0
    

    incoming_state = float(incoming_state)
    current_state = float(current_state)

    if incoming_value is None:
        incoming_value = ""
    if current_value is None:
        current_value = ""
    if not isinstance(current_value, str):
        current_value = str(current_value)

    if not isinstance(incoming_value, str):
        incoming_value = str(incoming_value)

    # print("machine state {} , incoming state: {} , current_state {} incoming < current {} ".format(machine_state, incoming_state, current_state, incoming_state<current_state))
    
    if machine_state < incoming_state:
        return {'defer': True}

    if incoming_state < current_state:
        return {'historical': True}

    if incoming_state < current_state:
        return {'converge': True, 'incoming':True}

    # conflict here.
    if incoming_state == current_state:
        if incoming_value == current_value:
            return {'state': True}
        if incoming_value < current_value:
            return {'converge': True, 'current':True}
        
        if current_value < incoming_value:
            return {'converge': True, 'incoming':True}

    return {"err": "Invalid CRDT Data: {} to {} at {} to {} ".format(incoming_value, current_value , incoming_state, current_state)}

# applying updates "change" to the graph
def ham_mix(change, graph):
    machine = int(time.time()*1000)  # because the value coming from client +new Date() 
    diff = {}
    for soul, node in change.items():
        for key, val in node.items():
            if key in [METADATA, SOUL,STATE]:
                continue
            state = get_state_of(node, key) or 0
            graphnode = graph.get(soul, {})
            was = get_state_of(graphnode, key) or 0
            known = graphnode.get(key, 0)
            ham = HAM(machine, state, was, val, known)
            ## FIXME:
            # if ham.get('incoming', False):
            #     # implement defer here.
            #     return 
            if soul not in diff:
                diff[soul] = new_node(soul)

            graph[soul] = graph.get(soul, new_node(soul))
            # print("GRAPH[SOUL]: ", graph[soul], graph, type(graph), type(graph[soul]))
            graph[soul][key], diff[soul][key] = val, val
            graph[soul] = ensure_state(graph[soul])
            diff[soul] = ensure_state(diff[soul])

            graph[soul][METADATA][STATE][key] = state
            diff[soul][METADATA][STATE][key] = state

    return diff

def lex_from_graph(lex, db):
    """
    Graph or backend..
    """
    soul = lex[SOUL]
    key = lex.get(".", None)
    node = db.get(soul, None)
    tmp = None
    if not node:
        return {}
    if key:
        tmp = node.get(key, None)
        if not tmp:
            return
        node = ensure_state(node)
        node[key] = tmp
        tmp = node[METADATA][STATE]
        node[METADATA][STATE][key] = tmp[key]
        node[METADATA][SOUL] = node[SOUL]

    ack = {}
    ack[soul] = node

    return ack

