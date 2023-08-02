# Copyright (C) 2021 Silvan Fischbacher


class Team(object):
    """
    Class for a team.

    :param name: Name of the team
    :param GoalsF: Goals scored
    :param GoalsA: Goals conceded
    :param played: Number of games played
    :param penalty_scoring: Factor for penalty scoring
    """

    def __init__(self, name, GoalsF, GoalsA=None, played=1, penalty_scoring=0.75):
        """
        Initialize the team class
        """
        self.name = name
        self.GoalsF = GoalsF
        self.GoalsA = GoalsA
        self.played = played
        self.penalty_scoring = penalty_scoring

    @property
    def AvGoalsF(self):
        """
        Average goals scored per game
        """
        return self.GoalsF / self.played

    @property
    def AvGoalsA(self):
        """
        Average goals conceded per game
        """
        return self.GoalsA / self.played
