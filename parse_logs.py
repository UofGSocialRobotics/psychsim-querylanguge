import re
import consts
import json
from StringIO import StringIO
import argparse
from termcolor import colored
import helper_functions as helper
import anytree
import actiontree
import itertools

def get_ints(s):
    return [int(s) for s in str.split(" ") if s.isdigit()]

def preprocess(s):
    s = s.replace("\n", " ")
    s = s.strip()
    s = re.sub(' +', ' ', s)
    return s


class LogParser:


    ############################################################################################################
    ##                       Initialisation: arsing log and saving info to answer queries                     ##
    ############################################################################################################


    def __init__(self, filename):
        self.actions = dict()
        self.filename = filename
        self.n_rounds = -1
        self.agents_list = list()
        self.actions_list = list()
        self.models = dict()
        self.parse_log()

        self.command = None
        self.query_param = dict()
        self.init_queryparams()


    def init_queryparams(self):
        self.query_param = dict()
        self.query_param[consts.AGENT] = None
        self.query_param[consts.ROUND] = -1
        self.query_param[consts.ACTION] = None


    def update_round(self, current_round, line, n_tabs):
        if (n_tabs == 0 and consts.ROUND in line) or (n_tabs == 3 and consts.ROUND in line and "World" not in line):#and not "World" in line:
            # print(n_tabs, line)
            line_splited = line.split("round:")
            round_str = line_splited[1]
            return int(re.search('\t(.*)\n', round_str).group(1))
        else:
            return current_round

    def who_does_what(self, agentdoesaction, buffer=None):
        tuple = agentdoesaction.split("-")
        shared_err_msg = "cannot retrieve an agent name and an action %s. Expecting \"AgentName-ActionName\""
        if len(tuple) < 2:
            print >> buffer, "ParsingError: cannot find \"-\" in %s thus "+shared_err_msg % agentdoesaction
            return False
        elif len(tuple) > 2:
            # print >> buffer, "ParsingError: found too many \"-\" in %s thus "+shared_err_msg % agentdoesaction
            # return False
            # print(tuple)
            agent, action = tuple [0], "-".join(tuple[1:])
            return agent, action
        else:
            return tuple

    def is_known(self, agent):
        return agent in self.agents_list

    def add_agent(self, agent):
        if not self.is_known(agent):
            self.agents_list.append(agent)

    def parse_utility(self, log_line):
        return helper.string_between_parentheses(log_line), helper.extract_floats(log_line)[0]

    def parse_model(self, log_line):
        return log_line.split("__model__")[1].strip()

    def is_projection_action_utility_line(self, s):
        # return (("Effect:" not in s) and ("State:" not in s) and (helper.count_tabs_at_beginning_of_line(s) == s.count('\t')))
        return "(V_" in s
    
    def parse_projection_action_utility_line(self, line):
        splited_at_dash = line.strip().split("-")
        agent = splited_at_dash[0]
        action = "-".join(splited_at_dash[1:]).split()[0]
        # print("parse_projection_action_utility_line")
        # print(agent, action)
        splited_at_equal = line.split("=")
        u = float(helper.extract_floats(splited_at_equal[1])[0])
        u_for = splited_at_equal[0].split("_")[-1]
        p = float(line.split("[P=")[1].split("%")[0])/ 100.0
        # print(agent, action, u, u_for, p)
        return agent, action, u, u_for, p

    # def init_projection_tree(self):
    #     last_node_of_depth = dict()
    #     root = anytree.Node("root", parent=None)
    #     last_node_of_depth[0] = root
    #     return last_node_of_depth

    def add_model(self, tuple, agent):
        model, model_about = tuple[1], tuple[0]
        if agent not in self.models.keys():
            self.models[agent] = dict()
        self.add_model_about(model, model_about, agent)

    def add_model_about(self, model, model_about, agent):
        if model_about not in self.models[agent].keys():
            self.models[agent][model_about] = list()
        if model not in self.models[agent][model_about]:
            self.models[agent][model_about].append(model)


    def parse_log(self, filepath=None, buffer=None):
        print("Loading...")
        # last_node = None
        round = -1
        models = list()
        line_worldstate = 1
        model_about = None
        if not filepath:
            filepath = self.filename
        with open(filepath) as fp:
            lines = fp.readlines()
            for i, line in enumerate(lines):

                n_tabs = helper.count_tabs_at_beginning_of_line(line)
                new_round = self.update_round(current_round=round, line=line, n_tabs=n_tabs)
                if new_round != round:
                    round = new_round
                    last_node_of_depth = dict()
                    # print("line", i)
                    # print("new round, round = %d" % round)


                if n_tabs == 0:
                    # print(i)

                    ## What the agent actually does
                    if line[0:4] == "100%":
                        pass
                    else:
                        # print(i, line)
                        agentdoesaction = line[:-1]
                        if len(agentdoesaction):
                            agent, action = self.who_does_what(agentdoesaction, buffer=buffer)
                            if not self.is_known(agent):
                                self.add_agent(agent)
                            if action not in self.actions_list:
                                self.actions_list.append(action)
                            self.actions[round] = dict()
                            self.actions[round][consts.AGENT] = agent
                            self.actions[round][consts.ACTION] = action
                            root = actiontree.create_action_node(agentdoesaction, parent=None, agent=agent, action=action, models=models)
                            self.actions[round][consts.PROJECTION] = root
                            last_node_of_depth[0] = root


                elif "__model__" in line:
                    models.append([model_about, self.parse_model(line)])
                    # print(models)

                elif "V(" in line:
                    # print(i, line, n_tabs)
                    # print(last_node_of_depth)
                    agentdoesaction, utility = self.parse_utility(line)
                    agent, action = self.who_does_what(agentdoesaction, buffer=buffer)
                    parent = last_node_of_depth[n_tabs-1]
                    new_node = actiontree.create_action_node(agent+"-"+action, parent=parent, action=action, agent=agent, models=models, V=float(utility))
                    if parent.name == agentdoesaction: # n_tabs == 1
                        parent.next_action = new_node.name
                    last_node_of_depth[n_tabs] = new_node
                    for tuple in models:
                        self.add_model(tuple, agent)
                    models = list()




                elif "(V_" in line:
                    # print(i, line, n_tabs)
                    # print(last_node_of_depth)
                    agent, action, u, u_for, p = self.parse_projection_action_utility_line(line)
                    agentdoesaction = agent+'-'+action
                    try:
                        parent = last_node_of_depth[n_tabs-1]
                    except KeyError as e:
                        print("KeyError: %s" % e.__str__())
                        print("at line", i, line)
                        print(last_node_of_depth)
                        exit(0)
                    new_node = actiontree.create_action_node(agentdoesaction, parent=parent, action=action, agent=agent, models=models, V_for_agent=(u_for,u), p=p)
                    last_node_of_depth[n_tabs] = new_node
                    if parent.agent != agent or parent.name == agentdoesaction:
                        parent.next_action = new_node.name
                    for tuple in models:
                        self.add_model(tuple, agent)
                    models = list()
                # print(last_node_of_depth)


                if "State:" in line:
                    line_worldstate = 0
                    model_about = None
                else:
                    line_worldstate -= 1
                    if line_worldstate == -1:
                        model_about_indent = helper.count_tabs_at_beginning_of_line(line)
                    elif line_worldstate <-1:
                        tabs = helper.count_tabs_at_beginning_of_line(line)
                        if tabs == model_about_indent:
                            model_about = line.strip().split(" ")[0]


        self.n_rounds = round
        # print(self.n_rounds)
        # print(self.actions)
        # root = last_node_of_depth[0]
        # actiontree.print_tree(root)




    ############################################################################################################
    ##                            Reading, understanding and executing user command                           ##
    ############################################################################################################

    def get_command(self, query):
        self.command = ' '.join(query.split()[:2])


    def get_arguments(self, query, buffer=None):
        query_dash_splited = query.split('-')
        for args in query_dash_splited[1:]:
            # print(args)
            args_pair = args.strip().split(' ')
            # print(args_pair)
            if len(args_pair) < 2:
                print >> buffer, "ParameterError: missing value for query parameter %s" % args
                return False
            elif len(args_pair) > 2:
                print >> buffer, "ParameterError: too many values for query parameter %s" % args
                return False
            else:
                p_name, p_value = args_pair[0], args_pair[1]
                if p_name not in consts.ALL_QUERY_PARAMS:
                    print >> buffer, "ParameterError: unknown parameter %s" % p_name
                    return False
                else:
                    if self.check_value_of_parameter(p_name, p_value, buffer):
                        self.query_param[p_name] = p_value
                    else:
                        return False
        return True

    def check_value_of_parameter(self, p_name, p_val, buffer=None):
        if p_name in consts.QUERY_PARAM[consts.ROUND]:
            # print("in here")
            try:
                i = int(p_val)
                # print("got turn "+i.__str__())
                if i > self.n_rounds:
                    print >> buffer, "ValueError: max for parameter %s is %d" % (p_name, self.n_rounds)
                    return False
                else:
                    self.query_param[consts.ROUND] = i
                return True
            except ValueError:
                print >> buffer, "ValueError: parameter %s takes integers, got %s" % (p_name, p_val)
                return False
        elif p_name == consts.AGENT:
            if self.is_known(p_val):
                self.query_param[consts.AGENT] = p_val
                return True
            else:
                print >> buffer, "ParameterError: we have no agent named %s in the simulation." % p_val
                return False
        elif p_name == consts.ACTION:
            if p_val in self.actions_list:
                self.query_param[consts.ACTION] = p_val
                return True
            else:
                print >> buffer, "ParamaterError: %s does not exists." % p_val
                return False


    def parse_query(self, query, buffer):
        self.init_queryparams()
        self.get_command(query)
        res = self.get_arguments(query, buffer=buffer)
        return res


    def execute_query(self, query, buffer=None):
        if self.parse_query(query, buffer=buffer):
            if self.command in consts.COMMANDS_GET_ACTIONS:
                self.get_actions(p_agent=self.query_param[consts.AGENT], r_round=int(self.query_param[consts.ROUND]), p_action=self.query_param[consts.ACTION], buffer=buffer)
            elif self.command in consts.COMMAND_REPLAY_SIM:
                self.replay_simulation(buffer=buffer)
            elif self.command in consts.COMMAND_GET_AGENTS:
                self.get_agents(p_agent=self.query_param[consts.AGENT], r_round=int(self.query_param[consts.ROUND]), p_action=self.query_param[consts.ACTION], buffer=buffer)
            elif self.command in consts.COMMAND_GET_UTILITIES:
                self.get_utilities(p_round=int(self.query_param[consts.ROUND]), buffer=buffer)
            elif self.command in consts.COMMAND_PROJECTION_FULL:
                self.full_projection(p_round=int(self.query_param[consts.ROUND]), buffer=buffer)
            elif self.command in consts.COMMAND_PROJECTION_SUBTREE:
                self.projection_subtree(p_round=int(self.query_param[consts.ROUND]), p_action=self.query_param[consts.ACTION], buffer=buffer)
            elif self.command in consts.COMMAND_GET_MODEL:
                self.get_models(buffer=buffer)
            elif self.command in consts.COMMAND_PROJECTION_SEQUENCE:
                self.projection_optpath(p_round=int(self.query_param[consts.ROUND]), buffer=buffer)
            else:
                print >> buffer, "QueryError: \"%s\" command unkonwn" % self.command
        else:
            print >> buffer, "ERROR, cannot execute query: %s" % query
            return False

    ############################################################################################################
    ##                                     Loop: read and execute commands                                    ##
    ############################################################################################################

    def query_log(self):
        q= False
        print(colored("Ready to query log. Use q to quit and h for help.", "red"))
        while(not q):
            query = raw_input(colored("Query: ", "red"))
            if query == 'q':
                q = True
            elif query == 'h':
                print_help()
            else:
                self.execute_query(preprocess(query))

    ############################################################################################################
    ##                                              COMMANDS                                                  ##
    ############################################################################################################


    ## --------------------------------              What happened           -------------------------------- ##

    def get_all_actions_of_agent(self, agent):
        return [d[consts.ACTION] for d in self.actions.values() if d[consts.AGENT] == agent]

    def print_info(self, turn, agent, action, buffer=None):
        print >> buffer, "%s %d: %s %s" % (consts.ROUND.title(), turn, agent, action)

    def get_actions(self, p_agent=None, r_round=-1, p_action=None, buffer=None):
        if (not p_action and not p_agent and r_round == -1):
            return self.get_all_actions_played(buffer=buffer)

        if r_round > -1:
            agent, action = self.actions[r_round][consts.AGENT], self.actions[r_round][consts.ACTION]
            if p_agent and p_agent != agent:
                print >> buffer, "ParameterError: agent %s does not do anything at %s %d" % (p_agent, consts.ROUND, r_round)
                return False
            if p_action and p_action != action:
                print >> buffer, "ParameterError: action %s is not played at %s %d" % (p_agent, consts.ROUND, r_round)
                return False
            self.print_info(r_round, agent, action, buffer=buffer)
            return True

        bool_got_res = False
        for t, d in self.actions.items():
            agent, action = d[consts.AGENT], d[consts.ACTION]
            cond_agent = not p_agent or (p_agent and p_agent == agent)
            cond_action = not p_action or (p_action and p_action == action)
            if (cond_agent and cond_action):
                bool_got_res = True
                self.print_info(t, agent, action, buffer=buffer)
        if not bool_got_res:
            print >> buffer, "ParameterError: agent %s never does action %s" % (p_agent, p_action)


    def replay_simulation(self, buffer=None):
        for t, d in self.actions.items():
            agent, action = d[consts.AGENT], d[consts.ACTION]
            self.print_info(t, agent, action, buffer=buffer)
        return True


    def get_all_actions_played(self, buffer=None):
        print >> buffer, "All the different actions that are played during the simulation are:\n%s" % ", ".join(self.actions_list)
        return True


    def get_all_agents(self, buffer=None):
        print >> buffer, "All the agents who do at least one action during the simulation are:\n%s" % ", ".join(self.agents_list)
        return True


    def get_agents(self, p_agent=None, r_round=-1, p_action=None, buffer=None):
        if (p_agent or p_action or r_round != -1):
            return self.get_actions(p_agent,r_round,p_action,buffer)
        else:
            return self.get_all_agents(buffer=buffer)



    ## --------------------------------       Why it happened         -------------------------------- ##

    def get_utilities(self, p_round, buffer=None):
        if p_round == -1 :
            print >> buffer, "ParameterError: missing argument -round"
            return False
        # sorted_actions = list(reversed(helper.sort_dic_by_values(self.actions[p_round][consts.UTILITIES])))
        l = [(child.name, child.V) for child in self.actions[p_round][consts.PROJECTION].children]
        l_sorted = helper.sort_list_of_tuples_by_second_param(l)
        # print(l_sorted)
        actions = [k for k,v in l_sorted]
        longest_str = max(actions, key=len)
        max_len = len(longest_str) + 2
        for a, u in l_sorted:
            print >> buffer, helper.add_space_at_end(a,max_len-len(a)) + u.__str__()
        return True


    def full_projection(self, p_round, buffer=None):
        if p_round == -1 :
            print >> buffer, "ParameterError: missing argument -round"
            return False
        actiontree.print_tree(self.actions[p_round][consts.PROJECTION], buffer)
        return True


    def projection_subtree(self, p_round, p_action, buffer=None):
        if p_round == -1 :
            print >> buffer, "ParameterError: missing argument -round"
            return False
        action_found = False
        for child in self.actions[p_round][consts.PROJECTION].children:
            if child.action == p_action:
                actiontree.print_tree(child)
                action_found = True
                break
        if not action_found:
            print >> buffer, "ParameterError: cannot find action \"%s\" at round %d." % (p_action, p_round)
            print >> buffer, "At round %s, actions are:"
            self.get_utilities(p_round, buffer)
            return False
        return True



    def get_models(self, buffer=None):
        l = self.models.keys()
        if len(l) == 0:
            print >> buffer, "Error: No logs about agents' models of others."
        else:
            for a in l:
                s = a + " has models: " # + ", ".join(self.models[a])
                for model_about, models in self.models[a].items():
                    if model_about != a:
                        s+= "\n\t- about %s: %s" %(model_about, ", ".join(models))
                print >> buffer, s


    def add_action_in_path_list(self, paths, action, models, buffer):

        if len(models) == 0:
            #no model specified: add the action to every branch (every model)
            # print("no model specified: add the action to every branch (every model)")
            for _, actions_list in paths.items():
                actions_list.append(action)
        else:
            # models are specified: add them to the correct branch (with matching models)
            for c, actions_list in paths.items():
                cond = 0
                for m in models:
                    d = helper.depth(c)
                    if d == 2:
                        for m2 in c:
                            # print(m,m2)
                            if helper.tuples_equal(m, m2):
                                cond += 1
                                # break
                    elif d == 1:
                        if helper.tuples_equal(c,m):
                            cond = 1
                            break
                    else:
                        print("ERROR, we should not be in the case where d = %d" % d)
                if (d == 1 and cond == 1) or (d == 2 and cond == len(c)):
                    # print("models are specified: add them to the correct branch (with matching models) --- models are")
                    # print(c)
                    actions_list.append(action)
                    break
            if (d == 1 and cond == 0) or (d == 2 and cond != len(c)):
                #no branch was found with that model: add action to every branch
                print("/!\\ no branch was found with that model: add action to every branch")
                for _, actions_list in paths.items():
                    actions_list.append(action)
        return True


    def projection_optpath(self, p_round, buffer=None):
        if p_round == -1 :
            print >> buffer, "ParameterError: missing argument -round"
            return False
        agent = self.actions[p_round][consts.AGENT]
        combinations = list()
        for about, list_of_models in self.models[agent].items():
            if about != agent:
                prep_list = [(about, m) for m in list_of_models]
                if len(combinations) == 0:
                    combinations = prep_list
                else:
                    combinations = [zip(x, prep_list) for x in itertools.permutations(combinations,len(prep_list))]
                    combinations = [item for sublist in combinations for item in sublist]
        # combinations = helper.convert_nested_tuples_to_nested_list(combinations)
        # print("Combinations of models:")
        # print(combinations)
        # print("------------------\n")

        paths = dict()
        node = self.actions[p_round][consts.PROJECTION]
        for c in combinations:
            paths[c] = list()
        pile_of_nodes_to_explore = [node]
        active_models = list()

        while len(pile_of_nodes_to_explore) > 0:
            node = pile_of_nodes_to_explore.pop()
            if len(node.models):
                active_models = node.models
            r = self.add_action_in_path_list(paths=paths, action=node, models=active_models, buffer=buffer)
            if not r:
                return False
            next_action_name = node.next_action
            explain_bool = (len(node.children) == 2 and (node.children[0].name == node.name and node.children[1].name))
            cond = next_action_name or explain_bool
            if cond:
                if next_action_name:
                    # pile_of_nodes_to_explore.insert(0, next_action)
                    pile_of_nodes_to_explore = actiontree.get_next_action(node, next_action_name) + pile_of_nodes_to_explore
                else:
                    print(" in else")
                    for child in node.children:
                        pile_of_nodes_to_explore.insert(0, child)

        paths_string = dict()
        # print(paths)
        for key, value in paths.items():
            reduced_list = actiontree.remove_consecutive_duplicate_actions(value)
            # print("\nreduced_list")
            # print(key)
            # print(reduced_list)
            paths_string[key] = dict()
            paths_string[key]["string_list"] = [node.name for node in reduced_list]
            paths_string[key]["p"] = reduced_list[0].p
            # paths_string[key] = helper.remove_duplicate_consecutive_elements(paths_string[key])

        s = "At round %d, %s thinks that the future sequence of actions will be" % (p_round, self.actions[p_round][consts.AGENT])
        for key, value in paths_string.items():
            string_actions_list, p = value["string_list"], value["p"]
            d = helper.depth(key)
            if d == 2:
                #agent models about several agents
                s += "\n\t[p=%.3f] " % p
                for (m_about, m) in key:
                    s += " %s is %s," % (m_about, m)
                s = s[:-1] + ":"
            elif d ==1:
                #agent has models about one other agent
                m_about, m = key[0], key[1]
                s += "\n\t[p=%.3f] %s is %s:" % (p, m_about, m)
            else:
                print("ERROR, we should not have depth should be 1 or 2!")
            s += " " + ", ".join(string_actions_list)
        print >> buffer, s
        # print(paths_string)



        # actions.append(node)
        # while not (node.is_leaf() or (not node.next_action and node.height <= 2)):




############################################################################################################
##                                              GENERAL METHODS                                           ##
############################################################################################################



def print_help():
    print(colored("Commands - optional arguments are between []", "yellow"))
    for c_list, c_desc in consts.HELP[consts.commands].items():
        s = c_list[0]
        for arg in c_desc[consts.parameters]:
            name, optional = arg[consts.name], arg[consts.optional]
            optional_open = "[" if optional else ""
            optional_close = "]" if optional else ""
            s += " "+optional_open+"-" + arg[consts.name] + optional_close
        print(s)
        print(c_desc[consts.description]+"\n")

    print(colored("Arguments", "yellow"))
    args = consts.HELP[consts.parameters].keys()
    longest_str = max(args, key=len)
    max_len = len(longest_str) + 2
    f = '{:>%d}' % max_len
    for arg, arg_desc in consts.HELP[consts.parameters].items():
        s = helper.add_space_at_end(arg, max_len-len(arg))
        s += arg_desc[consts.value_type]
        print(s)
        s = helper.add_space_at_end("", max_len)
        s += arg_desc[consts.description]
        print(s)

    print("\n")






def eval():
    filename = "logs/florian_phd.log"
    logparser = LogParser(filename)
    total, err = 0, 0
    with open("queries.json", "r") as f:
        content = json.load(f)
        for ex in content:
            buffer = StringIO()
            command = ex["command"]
            res_expected = preprocess(ex["res"])
            logparser.execute_query(command, buffer)
            res = preprocess(buffer.getvalue())
            if res_expected != res:
                err += 1
                print("----------")
                print("Query: %s" % command)
                print("Expected:\n%s" % res_expected)
                print("Got:\n%s" % res)
            total += 1
            buffer.close()
        print("\n----------\nError: %.2f (%d/%d)" % (float(err)/total, err, total))


def display_examples():
    with open("queries.json", "r") as f:
        content = json.load(f)
        for ex in content:
            print(ex["details"])
            print("Query:" + ex["command"])
            print("Result:\n%s" % ex["res"])
            print("----------")


if __name__ == "__main__":

    argp = argparse.ArgumentParser()
    argp.add_argument('logfile', metavar='logfile', type=str, help='Path to the log file to wrok from.')
    argp.add_argument("--eval", help="Checks that all commands listed in \"queries.json\" still work", action="store_true")
    argp.add_argument("--test", help="Test the log querier", action="store_true")
    argp.add_argument("--displayex", help="Displays the examples in \"queries.json\" ", action="store_true")

    args = argp.parse_args()

    if (args.test):
        # filename = "logs/florian_phd.log"
        logparser = LogParser(args.logfile)
        logparser.query_log()
    elif args.eval:
        eval()
    elif args.displayex:
        display_examples()
    else:
        argp.print_help()
