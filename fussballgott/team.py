"""
This defines the team class
"""


class team(object):

    def __init__(self, name, GoalsF, GoalsA = None, played = 1, penalty_scoring = 0.75):

        self.name = name
        self.GoalsF = GoalsF
        self.GoalsA = GoalsA
        self.played = played
        self.AvGoalsF = self.GoalsF / self.played
        self.AvGoalsA = self.GoalsA / self.played
        self.penalty_scoring = penalty_scoring
