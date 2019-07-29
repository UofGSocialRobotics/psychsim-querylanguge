description = "description"
parameters = "param"
commands = "commands"
value_type = "type"
name = "name"
optional = "optional"


ROUND = "round"
AGENT = "agent"
ACTION = "action"
QUERY_PARAM = {
    ROUND: ["round", "r"],
    AGENT: ["agent", "ag"],
    ACTION: ["action", "act"]
}
ALL_QUERY_PARAMS = [y for x in QUERY_PARAM.values() for y in x ]

UTILITIES = "utilities"
PROJECTION = "projection"

COMMANDS_GET_ACTIONS = "get action", "get actions"
COMMAND_REPLAY_SIM = "replay simulation", "replay sim", "replay"
COMMAND_GET_AGENTS = "get agent", "get agents"
COMMAND_GET_UTILITIES = "get utilities", "get utility"
COMMAND_GET_MODEL = "get models", ""

COMMAND_PROJECTION_FULL = "projection full", "proj full"
COMMAND_PROJECTION_OPTPATH = "projection optimalpath", "proj optpath", "projection optpath", "p o"
COMMAND_PROJECTION_SUBTREE = "projection subtree", "p s", "proj sub", "proj subtree"

HELP = {
    commands: {
        COMMAND_REPLAY_SIM: {
            description: "Replays the simulation",
            parameters: ""},
        COMMAND_GET_AGENTS: {
            description: "Returns a list of agents",
            parameters: [
                {name: ROUND,
                 optional: True},
                {name: AGENT,
                 optional: True},
                {name: ACTION,
                 optional:True}
            ]
        },
        COMMANDS_GET_ACTIONS: {
            description: "Returns a list of actions",
            parameters: [
                {name: ROUND,
                 optional: True},
                {name: AGENT,
                 optional: True},
                {name:ACTION,
                 optional:True}
            ]
        },
        COMMAND_GET_UTILITIES: {
            parameters: [
                {name: ROUND,
                 optional: False}
            ],
            description: "For the specified round, prints the utilities of all possible actions as computed by the agent."
        },
        COMMAND_PROJECTION_FULL: {
            parameters: [
                {name: ROUND,
                 optional: False}
            ],
            description: "For the specified round, prints the full projection tree as computed by the agent."
        },
        COMMAND_PROJECTION_SUBTREE: {
            parameters: [
                {name: ROUND,
                 optional: False},
                {name: ACTION,
                 optional: False}
            ],
            description: "For the specified round, prints the subtree corresponding to the projection of the specified action."
        }
    },
    parameters: {
        ROUND: {
            value_type: "int",
            description: "Focus on given round"
        },
        AGENT: {
            value_type: "agent name (string, case sensitive) --> to know agents' names, use \"get agents\"",
            description: "Focus on given agent name"
        },
        ACTION: {
            value_type: "agent name (string, case sensitive) --> to know the actions, use \"get actions\"",
            description: "Focus on given action"
        }
    }

}
