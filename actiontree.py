import anytree


def create_action_node(name, parent, action, agent, models=None, V=None, V_for_agent=None, p=None):
    return anytree.Node(name, parent=parent, action=action, agent=agent, models=models, V=V, V_for_agent=V_for_agent, p=p, next_action=None)

def get_child(node, child_name):
    for child in node.children:
        if child.name == child_name:
            return child
    return None

def next_action_str(node):
    return "NEXTACTION=%s" % node.next_action if node.next_action else ""



def print_tree(root, buffer=None):
    s_next_action = next_action_str(root)
    # print("%s %s" % (root.name, s_next_action))
    for pre, _, node in anytree.RenderTree(root):
        s_next_action = next_action_str(node)
        if isinstance(node.V, float):
            V = "V=%.3f" % node.V
        elif node.V_for_agent:
            V = "V_%s=%.3f" % (node.V_for_agent[0], node.V_for_agent[1])
        else:
            V = ""
        if isinstance(node.p, float):
            p_str = "p=%.2f" % node.p
        else:
            p_str = ""
        models_str = node.models.__str__()
        # print (node.models)
        print >> buffer, "%s%s %s %s models=%s %s" % (pre, node.name, V, p_str, models_str, s_next_action)

def get_next_action(node, next_action_name):
    '''
    Gets the list of next actions as specified in node
    :param node: Node from which to search from next action
    :param next_action_name: name of the next action
    :return: a list of next actions. --> we may have several next actions if the agent makes several hypotheses following the different models it has of other agents.
    '''
    next_actions_list = list()
    for child in node.children:
        if child.name == next_action_name:
            next_actions_list.append(child)
    return next_actions_list


def remove_consecutive_duplicate_actions(nodes_list):
    if len(nodes_list) == 1:
        return nodes_list
    new_list = list()
    n1 = nodes_list[0]
    for n2 in nodes_list[1:]:
        # print("n2.name", n2.name)
        last_node_appended = False
        if n1.name == n2.name:
            if n2.p:
                n1 = n2
        else:
            new_list.append(n1)
            last_node_appended = True
            n1 = n2
    if not last_node_appended:
        new_list.append(n2)
    return new_list
