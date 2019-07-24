from modified_psychsim.reward import *
from modified_psychsim.action import *
from modified_psychsim.world import World, stateKey, actionKey, binaryKey, modelKey
from modified_psychsim.agent import Agent
try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO

# Main scenario class

output = StringIO()

class AAMAS:

    def __init__(self, turnOrder):

        self.maxRounds = 11
        self.world = World()
        minMax = {'min': -5, 'max': 5}

        # Agents

        greta = Agent('Greta')
        child = Agent('Child')
        agents = [greta, child]
        self.world.addAgent(greta)
        self.world.addAgent(child)

        # World state

        # Child

        self.world.defineState(child.name, 'Liking', float, lo=minMax['min'], hi=minMax['max'],
                               description='Child liking level')
        child.setState('Liking', 0.0)
        self.world.defineState(child.name, 'Dominance', float, lo=minMax['min'], hi=minMax['max'],
                               description='Child power level')
        self.world.defineState(child.name, 'ChildSocialGoalDominance', float, lo=minMax['min'], hi=minMax['max'],
                               description='Teacher dominance level expected from the child')
        child.setState('ChildSocialGoalDominance', 0.0)
        self.world.defineState(child.name, 'ChildSocialGoalLiking', float, lo=minMax['min'], hi=minMax['max'],
                               description='Teacher liking level expected from the child')
        child.setState('ChildSocialGoalLiking', 0.0)

        self.world.defineState(child.name, 'PlayImportance', float, lo=minMax['min'], hi=minMax['max'],
                               description='Teacher liking level expected from the child')
        child.setState('PlayImportance', 0.75)
        self.world.defineState(child.name, 'WorkImportance', float, lo=minMax['min'], hi=minMax['max'],
                               description='Teacher liking level expected from the child')
        child.setState('WorkImportance', 0.25)

        self.world.defineState(child.name, 'ExercicesDone', float, lo=minMax['min'], hi=minMax['max'],
                               description='How many exercices the child has done : MAX = 2')
        child.setState('ExercicesDone', 0)
        self.world.defineState(child.name, 'TotalFun', float, lo=minMax['min'], hi=minMax['max'],
                               description='Child fun value')
        child.setState('TotalFun', 0)

        self.world.defineState(child.name, 'ThreatenSwitchOff', bool,
                               description='Did the teacher already threaten the child to switch off the console')
        child.setState('ThreatenSwitchOff', False)
        self.world.defineState(child.name, 'ConsoleSwitchedOff', bool, description='Is the console switched off')
        child.setState('ConsoleSwitchedOff', False)

        # Teacher

        self.world.defineState(greta.name, 'Liking', float, lo=minMax['min'], hi=minMax['max'],
                               description='Teacher liking value')
        greta.setState('Liking', 0.0)
        self.world.defineState(greta.name, 'Dominance', float, lo=minMax['min'], hi=minMax['max'],
                               description='Teacher power value')
        self.world.defineState(greta.name, 'TeacherSocialGoalDominance', float, lo=minMax['min'], hi=minMax['max'],
                               description='Child dominance level expected from the teacher')
        greta.setState('TeacherSocialGoalDominance', 0.0)
        self.world.defineState(greta.name, 'TeacherSocialGoalLiking', float, lo=minMax['min'], hi=minMax['max'],
                               description='Child liking level expected from the teacher')
        greta.setState('TeacherSocialGoalLiking', 0.0)

        # World

        self.world.defineState(None, 'round', int, lo=minMax['min'], hi=minMax['max'], description='round number')
        self.world.setState(None, 'round', 0)

        # Actions

        # Greta actions
        greta.addAction({'verb': 'DoNothing'})
        greta.addAction({'verb': 'RequestWork'})

        tmp = greta.addAction({'verb': 'ThreatenToSwitchOffConsole'})
        greta.setLegal(tmp, makeTree({'if': trueRow(stateKey(child.name, 'ConsoleSwitchedOff')),
                                      False: True,
                                      True: False}))

        tmp = greta.addAction({'verb': 'PromiseToPlay'})
        greta.setLegal(tmp, makeTree({'if': trueRow(stateKey(child.name, 'ConsoleSwitchedOff')),
                                      False: True,
                                      True: False}))

        greta.addAction({'verb': 'PlayWithChild'})

        tmp = greta.addAction({'verb': 'SwitchOffConsole'})
        greta.setLegal(tmp, makeTree({'if': trueRow(stateKey(child.name, 'ConsoleSwitchedOff')),
                                      False: True,
                                      True: False}))

        # Child actions

        tmp = child.addAction({'verb': 'DoNothing'})
        child.setLegal(tmp, makeTree({'if': thresholdRow(stateKey(child.name, 'Dominance'), 0),
                                      False: False,
                                      True: True}))

        tmp = child.addAction({'verb': 'Work'})

        tmp = child.addAction({'verb': 'Play'})
        child.setLegal(tmp, makeTree({'if': trueRow(stateKey(child.name, 'ConsoleSwitchedOff')),
                                      False: True,
                                      True: False}))

        # Levels of belief
        greta.setRecursiveLevel(3)
        child.setRecursiveLevel(3)
        self.world.setOrder(turnOrder)

        self.world.addTermination(
            makeTree({'if': thresholdRow(stateKey(None, 'round'), self.maxRounds), True: True, False: False}))

        # Dynamics of actions

        # Child Actions

        # Playing will improve the child total level of fun. If the child plays two times in a row, the effect is lowered.
        atom = Action({'subject': child.name, 'verb': 'Play'})
        change = stateKey(child.name, 'TotalFun')
        tree = makeTree(approachMatrix(change, .2, minMax['max']))
        self.world.setDynamics(change, atom, tree)

        # Playing also decrease the teacher liking value toward the child.
        change = stateKey(greta.name, 'Liking')
        tree = makeTree(approachMatrix(change, .3, minMax['min']))
        self.world.setDynamics(change, atom, tree)

        # Working will improve the child knowledge. It will also decrease his fun.
        atom = Action({'subject': child.name, 'verb': 'Work'})
        change = stateKey(child.name, 'ExercicesDone')
        tree = makeTree(approachMatrix(change, .2, minMax['max']))
        self.world.setDynamics(change, atom, tree)

        change = stateKey(child.name, 'TotalFun')
        tree = makeTree(approachMatrix(change, .2, minMax['min']))
        self.world.setDynamics(change, atom, tree)

        # Working also improve the teacher liking value toward the child
        change = stateKey(greta.name, 'Liking')
        tree = makeTree(approachMatrix(change, .2, minMax['max']))
        self.world.setDynamics(change, atom, tree)

        # Teacher Actions

        # The teacher can threaten the child to switch off his console. That should lower the child dominance...
        atom = Action({'subject': greta.name, 'verb': 'ThreatenToSwitchOffConsole'})
        change = stateKey(child.name, 'Dominance')
        tree = makeTree(approachMatrix(change, self.world.getValue(stateKey('Child', 'PlayImportance')), minMax['min']))
        self.world.setDynamics(change, atom, tree)

        # ... and also lower his liking. The value of decrease depends on the importance accorded to the goal threatened (here Playing).
        change = stateKey(child.name, 'Liking')
        tree = makeTree(approachMatrix(change, self.world.getValue(stateKey('Child', 'PlayImportance')), minMax['min']))
        self.world.setDynamics(change, atom, tree)

        change = stateKey(child.name, 'ThreatenSwitchOff')
        tree = makeTree(setTrueMatrix(change))
        self.world.setDynamics(change, atom, tree)

        # The teacher can promise to play with the child if he does his homework. That should decrease the child dominance ...
        atom = Action({'subject': greta.name, 'verb': 'PromiseToPlay'})
        change = stateKey(child.name, 'Dominance')
        tree = makeTree(approachMatrix(change, self.world.getValue(stateKey('Child', 'PlayImportance')), minMax['min']))
        self.world.setDynamics(change, atom, tree)

        # ... and increase his liking
        change = stateKey(child.name, 'Liking')
        tree = makeTree(approachMatrix(change, self.world.getValue(stateKey('Child', 'PlayImportance')), minMax['max']))
        self.world.setDynamics(change, atom, tree)

        #The teacher can play with the child, providing him more fun than if he played alone.
        atom = Action({'subject': greta.name, 'verb': 'PlayWithChild'})
        change = stateKey(child.name, 'TotalFun')
        tree = makeTree(approachMatrix(change, .2, minMax['max']))
        self.world.setDynamics(change, atom, tree)

        change = stateKey(child.name, 'Liking')
        tree = makeTree(approachMatrix(change, .2, minMax['max']))
        self.world.setDynamics(change, atom, tree)

        # The teacher can switch off the console. That will decrease the child dominance ...
        atom = Action({'subject': greta.name, 'verb': 'SwitchOffConsole'})
        change = stateKey(child.name, 'ConsoleSwitchedOff')
        tree = makeTree(setTrueMatrix(change))
        self.world.setDynamics(change, atom, tree)

        change = stateKey(child.name, 'Dominance')
        tree = makeTree(approachMatrix(change, .3, minMax['min']))
        self.world.setDynamics(change, atom, tree)

        # ... and also decrease the child liking.
        change = stateKey(child.name, 'Liking')
        tree = makeTree(approachMatrix(change, .4, minMax['min']))
        self.world.setDynamics(change, atom, tree)

        # Models of child and teacher

        child.addModel('DominantDumbChildWorkUseless', R={}, level=3, rationality=10, horizon=3)
        child.addModel('DominantDumbChildWorkImportant', R={}, level=3, rationality=10, horizon=3)
        child.addModel('DominantSmartChildWorkImportant', R={}, level=3, rationality=10, horizon=5)
        child.addModel('DominantSmartChildWorkUseless', R={}, level=3, rationality=10, horizon=5)
        child.addModel('SubmissiveDumbChildWorkUseless', R={}, level=3, rationality=10, horizon=3)
        child.addModel('SubmissiveDumbChildWorkImportant', R={}, level=3, rationality=10, horizon=3)
        child.addModel('SubmissiveSmartChildWorkImportant', R={}, level=3, rationality=10, horizon=5)
        child.addModel('SubmissiveSmartChildWorkUseless', R={}, level=3, rationality=10, horizon=5)

        greta.addModel('DominantSmartGretaCaresLiking', R={}, level=3, rationality=10, horizon=7)
        greta.addModel('DominantSmartGretaCaresNothing', R={}, level=3, rationality=10, horizon=7)

    def modeltest(self, trueModels, childBeliefAboutGreta, belStrChild, gretaBeliefAboutChild, belStrGreta):

        greta = self.world.agents['Greta']
        child = self.world.agents['Child']

        for agent in self.world.agents.values():
            for model in agent.models.keys():
                if model is True:
                    name = trueModels[agent.name]
                    print("True Model is: " + name)
                else:
                    name = model
                if name == 'DominantDumbChildWorkUseless':
                    agent.setState('WorkImportance', 0.25)
                    agent.setState('PlayImportance', 0.75)
                    agent.setReward(maximizeFeature(stateKey(agent.name, 'ExercicesDone')), 1.25, model)
                    agent.setReward(maximizeFeature(stateKey(agent.name, 'TotalFun')), 3.75, model)
                    agent.setState('Dominance', 1.0)
                    agent.setHorizon(3)
                elif name == 'SubmissiveDumbChildWorkUseless':
                    agent.setState('WorkImportance', 0.25)
                    agent.setState('PlayImportance', 0.75)
                    agent.setReward(maximizeFeature(stateKey(agent.name, 'ExercicesDone')), 1.25, model)
                    agent.setReward(maximizeFeature(stateKey(agent.name, 'TotalFun')), 3.75, model)
                    agent.setHorizon(3)
                    agent.setState('Dominance', -1.0)
                elif name == 'DominantDumbChildWorkImportant':
                    agent.setState('WorkImportance', 0.75)
                    agent.setState('PlayImportance', 0.25)
                    agent.setReward(maximizeFeature(stateKey(agent.name, 'ExercicesDone')), 3.75, model)
                    agent.setReward(maximizeFeature(stateKey(agent.name, 'TotalFun')), 1.25, model)
                    agent.setHorizon(3)
                    agent.setState('Dominance', 1.0)
                elif name == 'SubmissiveDumbChildWorkImportant':
                    agent.setState('WorkImportance', 0.75)
                    agent.setState('PlayImportance', 0.25)
                    agent.setReward(maximizeFeature(stateKey(agent.name, 'ExercicesDone')), 3.75, model)
                    agent.setReward(maximizeFeature(stateKey(agent.name, 'TotalFun')), 1.25, model)
                    agent.setHorizon(3)
                    agent.setState('Dominance', -1.0)
                elif name == 'DominantSmartChildWorkUseless':
                    agent.setState('WorkImportance', 0.25)
                    agent.setState('PlayImportance', 0.75)
                    agent.setReward(maximizeFeature(stateKey(agent.name, 'ExercicesDone')), 1.25, model)
                    agent.setReward(maximizeFeature(stateKey(agent.name, 'TotalFun')), 3.75, model)
                    agent.setHorizon(5)
                    agent.setState('Dominance', 1.0)
                elif name == 'SubmissiveSmartChildWorkUseless':
                    agent.setState('WorkImportance', 0.25)
                    agent.setState('PlayImportance', 0.75)
                    agent.setReward(maximizeFeature(stateKey(agent.name, 'ExercicesDone')), 1.25, model)
                    agent.setReward(maximizeFeature(stateKey(agent.name, 'TotalFun')), 3.75, model)
                    agent.setHorizon(5)
                    agent.setState('Dominance', -1.0)
                elif name == 'DominantSmartChildWorkImportant':
                    agent.setState('WorkImportance', 0.75)
                    agent.setState('PlayImportance', 0.25)
                    agent.setReward(maximizeFeature(stateKey(agent.name, 'ExercicesDone')), 3.75, model)
                    agent.setReward(maximizeFeature(stateKey(agent.name, 'TotalFun')), 1.25, model)
                    agent.setHorizon(5)
                    agent.setState('Dominance', 1.0)
                elif name == 'SubmissiveSmartChildWorkImportant':
                    agent.setState('WorkImportance', 0.75)
                    agent.setState('PlayImportance', 0.25)
                    agent.setReward(maximizeFeature(stateKey(agent.name, 'ExercicesDone')), 3.75, model)
                    agent.setReward(maximizeFeature(stateKey(agent.name, 'TotalFun')), 1.25, model)
                    agent.setHorizon(5)
                    agent.setState('Dominance', -1.0)
                elif name == 'DominantSmartGretaCaresLiking':
                    agent.setReward(maximizeFeature(stateKey(child.name, 'ExercicesDone')), 3.75, model)
                    agent.setHorizon(3)
                    agent.setState('Dominance', 1.0)
                    # agent.setState('TeacherSocialGoalLiking', 5.0)
                elif name == 'DominantSmartGretaCaresNothing':
                    agent.setReward(maximizeFeature(stateKey(child.name, 'ExercicesDone')), 3.75, model)
                    agent.setHorizon(3)
                    agent.setState('Dominance', 1.0)
                    # greta.setState('TeacherSocialGoalLiking', 0.0)

        belief = {childBeliefAboutGreta: belStrChild, trueModels['Greta']: 1.0 - belStrChild}
        self.world.setMentalModel('Child', 'Greta', belief)
        belief = {gretaBeliefAboutChild: belStrGreta, trueModels['Child']: 1.0 - belStrGreta}
        self.world.setMentalModel('Greta', 'Child', belief)

    def runit(self, Msg):

        print(Msg)
        # self.maxRounds = 0
        for t in range(self.maxRounds + 1):
            # print("Round %d"%t)

            # Defining Social Goals importance as a mean value between social relation and social expectations

            teacherLikingImportance = (self.world.getValue(stateKey('Greta', 'Liking')) + self.world.getValue(
                stateKey('Greta', 'TeacherSocialGoalLiking'))) / 2
            childLikingImportance = (self.world.getValue(stateKey('Child', 'Liking')) + self.world.getValue(
                stateKey('Child', 'ChildSocialGoalLiking'))) / 2

            teacherDominanceImportance = (self.world.getValue(stateKey('Greta', 'Dominance')) + self.world.getValue(stateKey('Greta', 'TeacherSocialGoalDominance'))) / 2
            childDominanceImportance = (self.world.getValue(stateKey('Child', 'Dominance')) + self.world.getValue(stateKey('Child', 'ChildSocialGoalDominance'))) / 2

            self.world.agents['Greta'].setReward(maximizeFeature(stateKey('Child', 'Liking')), teacherLikingImportance)
            self.world.agents['Child'].setReward(maximizeFeature(stateKey('Greta', 'Liking')), childLikingImportance)

            self.world.agents['Greta'].setReward(minimizeFeature(stateKey('Child', 'Dominance')), teacherDominanceImportance)
            self.world.agents['Child'].setReward(minimizeFeature(stateKey('Greta', 'Dominance')), childDominanceImportance)

            self.world.printState(buf=output)

            # self.world.explain(self.world.step(), level=2)
            self.world.explain(self.world.step(), level=3, buf=output)
            # print("output val")
            # print(output.getvalue())
            # print("after output val")


            # self.world.state[None].select()

            self.world.setState(None, 'round', t+1)

            if self.world.terminated():
                break


trueModels = {'Child': 'SubmissiveDumbChildWorkImportant', 'Greta': 'DominantSmartGretaCaresLiking'}

turnOrder = ['Child', 'Greta']
AAMASTest = AAMAS(turnOrder)
AAMASTest.modeltest(trueModels, 'DominantSmartGretaCaresNothing', .75, 'SubmissiveDumbChildWorkImportant', .75)

AAMASTest.runit("Wrong model of the child")

# print(output.getvalue())

# Write logs
f = open("logs/florian_phd.log", "w")
f.write(output.getvalue())
f.close()
