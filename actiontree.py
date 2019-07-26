import anytree


def create_action_node(name, parent, action, agent, models=None, V=None, V_for_agent=None):
    return anytree.Node(name, parent=parent, action=action, agent=agent, models=models, V=V, V_for_agent=V_for_agent, next_action=None)

def get_child(node, child_name):
    for child in node.children:
        if child.name == child_name:
            return child
    return None

def next_action_str(node):
    return "NEXTACTION=%s" % node.next_action.name if node.next_action else ""



def print_tree(root, buffer=None):
    s_next_action = next_action_str(root)
    # print("%s %s" % (root.name, s_next_action))
    for pre, _, node in anytree.RenderTree(root):
        s_next_action = next_action_str(node)
        if node.V:
            V = "V=%.3f" % node.V
        elif node.V_for_agent:
            V = "V_%s=%.3f" % (node.V_for_agent[0], node.V_for_agent[1])
        else:
            V = ""
        models_str = node.models.__str__()
        # print (node.models)
        print >> buffer, "%s%s %s models=%s %s" %(pre, node.name, V, models_str, s_next_action)
