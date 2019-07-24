import anytree


def create_action_node(name, parent, action, agent, type, V=None, V_for_agent=None):
    return anytree.Node(name, parent=parent, action=action, agent=agent,  type=type, V=V, V_for_agent=V_for_agent)

def get_child(node, child_name):
    for child in node.children:
        if child.name == child_name:
            return child
    return None

