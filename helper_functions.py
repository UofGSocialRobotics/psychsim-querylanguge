import re
import operator
import itertools

def string_between_parentheses(s):
    return  s[s.find("(")+1:s.find(")")]

def extract_floats(s):
    return re.findall("\d+\.\d+", s)

def sort_dic_by_values(x):
    return sorted(x.items(), key=operator.itemgetter(1))

def add_space_at_end(s, n=1):
    for i in range(n):
        s += " "
    return s

def count_tabs_at_beginning_of_line(s):
    n_tabs = 0
    for c in s:
        if c == '\t':
            n_tabs += 1
        else:
            return n_tabs

def sort_list_of_tuples_by_second_param(l):
    l.sort(key=lambda x: x[1])
    return list(reversed(l))

def child_with_this_name_exists(node, child_name):
    for child in node.children:
        if child.name == child_name:
            return True
    return False

def convert_nested_tuples_to_nested_list(t):
    if isinstance(t, tuple):
        l = list(t)
        return [convert_nested_tuples_to_nested_list(x) for x in l]
    elif isinstance(t, list):
        return [convert_nested_tuples_to_nested_list(x) for x in t]
    else:
        return t

def convert_nested_list_to_nested_tuple(t):
    if isinstance(t, list):
        new_list = list()
        for x in t:
            x = convert_nested_list_to_nested_tuple(x)
            new_list.append(x)
        l = tuple(new_list)
        return l
    # elif isinstance(t, tuple):
    #     return [convert_nested_list_to_nested_tuple(x) for x in t]
    else:
        return t


def remove_duplicate_consecutive_elements(l):
    return [x[0] for x in itertools.groupby(l)]

def tuples_equal(t1, t2):
    for i, e1 in enumerate(t1):
        e2 = t2[i]
        if isinstance(e1, tuple):
            if isinstance(e2, tuple):
                bool = tuples_equal(e1, e2)
                if not bool:
                    return False
            return False
        if e1 != e2:
            return False
    return True

def depth(l):
    depths = [depth(item) for item in l if (isinstance(item, tuple) or isinstance(item, list))]
    if len(depths) > 0:
        return 1 + max(depths)
    return 1
