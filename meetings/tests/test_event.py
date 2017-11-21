"""
author: john nemeth
sources: class material
description: test file for get summary logic
"""
import flask_main
from flask_main import getSummaries
import nose

def test_getsummaries():
    calids = ['first', 'third']
    caldict = [{'id': 'first', 'summary': 'correct'}]
    summaries = flask_main.getSummaries(calids, caldict)
    assert 'correct' in summaries
