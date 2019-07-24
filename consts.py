description = "description"
parameters = "param"
commands = "commands"
value_type = "type"
name = "name"
optional = "optional"


ROUND = "round"
AGENT = "agent"
ACTION = "action"
UTILITIES = "utilities"
PROJECTION = "projection"

COMMANDS_GET_ACTIONS = "get action", "get actions"
COMMAND_REPLAY_SIM = "replay simulation", "replay sim", "replay"
COMMAND_GET_AGENTS = "get agent", "get agents"
COMMAND_GET_UTILITIES = "get utilities", "get utility"

COMMAND_PROJECTION_FULL = "projection full"

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
                {name:ACTION,
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
            description: "Returns the utilities of all possible actions as computed by the agent."
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
