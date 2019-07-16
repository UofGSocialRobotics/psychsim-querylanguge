import re
import consts
import json
from StringIO import StringIO
import argparse

def get_ints(s):
    return [int(s) for s in str.split(" ") if s.isdigit()]

def preprocess(s):
    s = s.replace("\n", " ")
    s = s.strip()
    s = re.sub(' +', ' ', s)
    return s


class LogParser:

    def __init__(self, filename):
        self.actions = dict()
        self.filename = filename
        self.n_rounds = -1
        self.agents_list = list()
        self.actions_list = list()
        self.parse_log()

        self.command = None
        self.query_param = dict()
        self.init_queryparams()


    def init_queryparams(self):
        self.query_param = dict()
        self.query_param[consts.AGENT] = None
        self.query_param[consts.ROUND] = -1
        self.query_param[consts.ACTION] = None


    def update_round(self, current_round, line):
        if consts.ROUND in line:
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
            print >> buffer, "ParsingError: found too many \"-\" in %s thus "+shared_err_msg % agentdoesaction
            return False
        else:
            return tuple

    def is_known(self, agent):
        return agent in self.agents_list

    def add_agent(self, agent):
        if not self.is_known(agent):
            self.agents_list.append(agent)

    def parse_log(self, filepath=None, buffer=None):
        round = 0
        if not filepath:
            filepath = self.filename
        with open(filepath) as fp:
           line = fp.readline()
           while line:
                line = fp.readline()
                round = self.update_round(current_round=round, line=line)
                if line and line[0] == "\t":
                    pass
                else:
                    if line[0:4] == "100%":
                        pass
                    else:
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


        self.n_rounds = round
        print(self.n_rounds, self.actions)


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
                if p_name not in self.query_param.keys():
                    print >> buffer, "ParameterError: unknown parameter %s" % p_name
                    return False
                else:
                    if self.check_value_of_parameter(p_name, p_value, buffer):
                        self.query_param[p_name] = p_value
                    else:
                        return False
        return True

    def check_value_of_parameter(self, p_name, p_val, buffer=None):
        if p_name == consts.ROUND:
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
                self.get_actions(p_agent=self.query_param[consts.AGENT],
                                 p_turn=int(self.query_param[consts.ROUND]),
                                 p_action=self.query_param[consts.ACTION],
                                 buffer=buffer)
            else:
                print >> buffer, "QueryError: \"%s\" command unkonwn" % self.command
        else:
            print >> buffer, "ERROR, cannot execute query: %s" % query
            return False


    def query_log(self):
        q= False
        print("Ready to query log. Use q to quit.")
        while(not q):
            query = raw_input("Query: ")
            if query == 'q':
                q = True
            else:
                self.execute_query(preprocess(query))

    ############################################################################################################
    ##                                              Commands                                                  ##
    ############################################################################################################

    def get_all_actions_of_agent(self, agent):
        return [d[consts.ACTION] for d in self.actions.values() if d[consts.AGENT] == agent]

    def print_info(self, turn, agent, action, buffer=None):
        print >> buffer, "%s %d: %s %s" % (consts.ROUND.title(), turn, agent, action)

    def get_actions(self, p_agent=None, p_turn=-1, p_action=None, buffer=None):
        if p_turn > -1:
            agent, action = self.actions[p_turn][consts.AGENT], self.actions[p_turn][consts.ACTION]
            if p_agent and p_agent != agent:
                print >> buffer, "ParameterError: agent %s does not do anything at %s %d" % (p_agent, consts.ROUND, p_turn)
                return False
            if p_action and p_action != action:
                print >> buffer, "ParameterError: action %s is not played at %s %d" % (p_agent, consts.ROUND, p_turn)
                return False
            self.print_info(p_turn, agent, action, buffer=buffer)
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
    argp.add_argument("--eval", help="Checks that all commands listed in \"queries.json\" still work", action="store_true")
    argp.add_argument("--test", help="Test the log querier", action="store_true")
    argp.add_argument("--displayex", help="Displays the examples in \"queries.json\" ", action="store_true")

    args = argp.parse_args()

    if (args.test):
        filename = "logs/florian_phd.log"
        logparser = LogParser(filename)
        logparser.query_log()
    elif args.eval:
        eval()
    elif args.displayex:
        display_examples()
    else:
        argp.print_help()
