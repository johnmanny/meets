"""
author: john nemeth
sources: class material
description: test file for get summary logic
"""
#import flask_main
#from flask_main import getSummaries
import nose
import arrow
import timeblock

# test to return span of day
def test_spanGreaterThanDay():
    now = arrow.utcnow()
    later = now.shift(days=1)
    assert timeblock.spanGreaterThanDay(now, later) is True
    assert timeblock.spanGreaterThanDay(now, later.shift(seconds=1)) is True
    assert timeblock.spanGreaterThanDay(now, later.shift(seconds=-1)) is False

# test forming dayList
def test_getDayList():
    begin = arrow.utcnow().floor('day')
    end = begin.shift(days=3)
    lastDate = end.ceil('day')
    beginDate = begin.floor('day')
    testList = timeblock.getDayList(begin, end)
    assert testList[0]['start'] == beginDate.isoformat() and testList[-1]['end'] == lastDate.isoformat()

# test 
def test_sortByDates():
    now = arrow.utcnow()
    newList = []
    newList.append(timeblock.timeblock(now.shift(hours=1), now.shift(hours=2), None, None))
    newList.append(timeblock.timeblock(now, now.shift(hours=1), None, None))
    newList = timeblock.sortByDates(newList)
    assert arrow.get(newList[0].start) < arrow.get(newList[1].start)

# test splitting events that span multiple days
def test_offsetSpan():
    now = arrow.utcnow()
    dayHalfSpan = timeblock.timeblock(now, now.shift(days=1, hours=12), None, None)
    dayTwelveSpan = timeblock.timeblock(now, now.shift(days=12, hours=4, minutes=58), None, None)
    twelveList = timeblock.splitLongEvent(dayTwelveSpan)
    halfList = timeblock.splitLongEvent(dayHalfSpan) 
    time = arrow.get(halfList[-1].end) - arrow.get(halfList[0].start)
    assert time == now.shift(days=1, hours=12) - now
    # if 'now' is < 4hrs58mins away from midnight, extra day event 
    #    will be created.
    time = arrow.get(twelveList[-1].end) - arrow.get(halfList[0].start)
    assert len(twelveList) > 12 and len(twelveList) < 15
    assert time == now.shift(days=12, hours=4, minutes=58) - now


# test splitting events that span multiple days
def test_splitExactSpan():
    now = arrow.utcnow()
    daySpan = timeblock.timeblock(now, now.shift(days=1), None, None)
    dayFourSpan = timeblock.timeblock(now, now.shift(days=4), None, None)
    # now-midnight, nextday-end
    assert len(timeblock.splitLongEvent(daySpan)) == 2
    # now-midnight, tmrw, nextday, nextday, nextdaymidnight-4 days from now == 5
    assert len(timeblock.splitLongEvent(dayFourSpan)) == 5

# test event ranges
def test_getEventsInRange():
    now = arrow.utcnow()
    dayList = timeblock.getDayList(now.floor('day'), now.shift(days=4))
    newList = timeblock.getEventsInRange(dayList, now.shift(hours=1).isoformat(), now.shift(hours=2))
    for days in newList:
        for events in days['agenda']:
            event = arrow.get(events.start)
            assert event.hour == now.shift(hours=1).hour 
