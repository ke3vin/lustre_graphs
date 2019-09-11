# Additional functions written 9/2019
# by Kevin Hildebrand

import re
import pwd
import grp
from graphite_api.render.datalib import TimeSeries

def absmax(x):
    absmax = None

    for v in x:
        if v is None:
            continue
        if abs(v) > absmax:
            absmax = abs(v)
    return absmax

def seriesdelta(x):
    for a in x:
        if a is not None:
            break

    if a is None:
        a=0

    for b in reversed(x):
        if b is not None:
            break

    if b is None:
        b=0

    return b-a 

def highestAbsMax(requestContext, seriesList, n=1):
    """
    Takes one metric or a wildcard seriesList followed by an integer N.

    Out of all metrics passed, draws only the N metrics with the highest
    absolute maximum value in the time period specified.

    """

    return sorted(seriesList, key=lambda s: absmax(s))[-n:]

def mostChange(requestContext, seriesList):
    """
    Takes one metric or a wildcard seriesList.  For each series, determine the delta (last
    value minus first value) and create a new series with the delta as its only (first) value.
    Really only useful to create a bar graph showing metrics with the most change over a time period.

    """

    results = []
    for series in seriesList:
        newValues = []
        delta = seriesdelta(series)
        newValues.append(delta)
        newName = "mostChange(%s)" % series.name
        newSeries = TimeSeries(newName, series.start, series.end, series.step, newValues)
        newSeries.pathExpression = newName
        results.append(newSeries)
    return results

def aliasLookupByNode(requestContext, seriesList, db, node):
    """
    Takes a seriesList and applies an alias derived by looking up a "node"
    portion/s of the target name in a database or service (UID, GID, etc)
    Node indices are 0 indexed.

    Example::

        &target=aliasLookupByNode(ganglia.*.cpu.load5,uid,1)

    """
    for series in seriesList:
        metric_pieces = re.search('(?:.*\()?(?P<name>[-\w*\.:#]+)(?:,|\)?.*)?',
				  series.name).groups()[0].split('.')
        try:
            if db == 'uid':
                series.name = pwd.getpwuid(int(metric_pieces[node]))[0]
            elif db == 'gid':
                series.name = grp.getgrgid(int(metric_pieces[node]))[0]
            else:
                series.name = metric_pieces[node]
        except KeyError:
            series.name = metric_pieces[node]
    return seriesList


SeriesFunctions = { 
    'highestAbsMax' : highestAbsMax,
    'aliasLookupByNode' : aliasLookupByNode,
    'mostChange' : mostChange,
}


