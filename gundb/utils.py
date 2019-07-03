import time
import uuid
from .consts import STATE, METADATA, SOUL

def newuid():
    return str(uuid.uuid4())

def get_state(node):
    if METADATA in node and STATE in node[METADATA]:
        return node[METADATA][STATE]
    return {STATE:{}}

def get_state_of(node, key):
    s = get_state(node)
    return s.get(key, 0) #FIXME: should be 0?

def new_node(name, **kwargs):
    # node with meta
    node = {METADATA: {SOUL:name, STATE:{k:0 for k in kwargs}}, **kwargs}
    return node

def ensure_state(node):
    name = node[METADATA][SOUL]
    if STATE not in node[METADATA]:
        node[METADATA][STATE] = {k:0 for k in node if k!=SOUL}
    return node
# conflict resolution algorithm 
def HAM(machine_state, incoming_state, current_state, incoming_value, current_value):
    # TODO: unify the result of the return
    # ADD UNIT TESTS TO COVER CASES
    if incoming_state in ["None", None]:
        incoming_state = 0
    if current_state in ["None", None]:
        current_state = 0
    

    incoming_state = int(incoming_state)
    current_state = int(current_state)

    if not isinstance(current_value, str):
        current_value = str(current_value)

    if not isinstance(incoming_value, str):
        incoming_value = str(incoming_value)

    # print("MACHINE STATE: ", machine_state, " INCOMING STATE: ", incoming_state, " CURRENT STATE: ", current_state, " INCOMING VAL:", incoming_value, " CURRENT VAL: ", current_value )
    # print(list(map(type, [machine_state, incoming_state, current_state, incoming_value, current_value])))
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
            print("GRAPH[SOUL]: ", graph[soul], graph, type(graph), type(graph[soul]))
            graph[soul][key], diff[soul][key] = val, val
            graph[soul] = ensure_state(graph[soul])
            diff[soul] = ensure_state(diff[soul])

            graph[soul][METADATA][STATE][key] = state
            diff[soul][METADATA][STATE][key] = state

    return diff

def lex_from_graph(lex, graph):
    """
    Graph or backend..
    """
    soul = lex[SOUL]
    key = lex.get('.', None)
    node = graph.get(soul, None)
    tmp = None
    if not node: return {}
    if key:
        tmp = node.get(key, None)
        if not tmp:
            return 
        node = {METADATA: node[METADATA]}
        node[key] = tmp 
        tmp = node[METADATA][STATE]
        node[METADATA][STATE][key] = tmp[key]

    ack = {}
    ack[soul] = node

    return ack