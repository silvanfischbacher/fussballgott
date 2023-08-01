# Copyright (C) 2021 Silvan Fischbacher

"""
This defines the team class
"""


class team(object):
    def __init__(self, name, GoalsF, GoalsA=None, played=1, penalty_scoring=0.75):
        self.name = name
        self.GoalsF = GoalsF
        self.GoalsA = GoalsA
        self.played = played
        self.penalty_scoring = penalty_scoring

    @property
    def AvGoalsF(self):
        return self.GoalsF / self.played

    @property
    def AvGoalsA(self):
        return self.GoalsA / self.played
