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
