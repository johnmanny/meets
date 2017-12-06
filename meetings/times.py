"""
Author: John Nemeth
Sources: Class Material
Description: implementation file for functions used to manipulate agendas
"""

import arrow
from dateutil import tz

class timeblock:

    def __init__(self, first, last, aType, summ):
        self.start = first
        self.end = last
        self.type = aType
        self.summary = summ

    def setStart(self, begin):
        self.start = begin

    def setEnd(self, last):
        self.end = last

    def setType(self, category):
        self.type = category

    def setSummary(self, description):
        self.summary = description

    def setCalSum(self, calsum):
        self.calSum = calsum 
