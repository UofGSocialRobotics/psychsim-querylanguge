import re
import operator

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
