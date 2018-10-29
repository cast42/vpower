#!/usr/bin/env python

"""vpower2.py.

Usage:
  vpower2.py [--lever=<lv>] INPUT

Arguments:
  INPUT         Required .TCX input filename

Options:
  -h --help     Show this.
  --lever=<lv>  Specify positon of the lever [default: 5].

"""
from __future__ import print_function
import re, sys
from docopt import docopt
try:
  from lxml import etree
  print("running with lxml.etree")
except ImportError:
  try:
    # Python 2.5
    import xml.etree.cElementTree as etree
    print("running with cElementTree on Python 2.5+")
  except ImportError:
    try:
      # Python 2.5
      import xml.etree.ElementTree as etree
      print("running with ElementTree on Python 2.5+")
    except ImportError:
      try:
        # normal cElementTree install
        import cElementTree as etree
        print("running with cElementTree")
      except ImportError:
        try:
          # normal ElementTree install
          import elementtree.ElementTree as etree
          print("running with ElementTree")
        except ImportError:
          print("Failed to import ElementTree from any known place")
from fitparse import FitFile, FitParseError

def semi2deg(pos):
    """Based on https://github.com/adiesner/Fit2Tcx/blob/master/src/Fit2TcxConverter.cpp"""
    DEGREES = 180.0
    SEMICIRCLES  = 0x80000000
    return float(pos) * DEGREES / SEMICIRCLES

ns1 = 'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2'
ns2 = 'http://www.garmin.com/xmlschemas/ActivityExtension/v2'

def s2p(speed, lever=5):
    assert (lever > 0 and lever < 11)
    lever -= 1 # Start from lever position 0
    # The array factor contains power at 60km/h at lever positions 1 to 10
    factor1 =  [200.0,281.0,366.0,447.0,532.0,614.0,702.0,787.0,868.0,953.0]
    # The array factor contains power at 29.9km/h at lever positions 1 to 10
    factor2 =  [85.0,121.0,162.0,196.0,236.0,272.0,307.0,347.0,382.0,417.0]
    speed *= 3.6 # Convert m/s to km/h
    w = int(factor2[lever]+(speed-29.9)/30.1*(factor1[lever]-factor2[lever]))
    return w if w > 0 else 0


def process_file(fitfilename, lever):
    """
    Process the whole FIT file.
    """

    try:
        fitfile = FitFile(fitfilename)
        fitfile.parse()
    except FitParseError, e:
        print ("Error while parsing .FIT file: %s" % e)
        sys.exit(1)

    ns = {
    'tcx': 'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2',
    } 

    # roottree = etree.ElementTree()
    # root = roottree.getroot()
    tcx = etree.Element('TrainingCenterDatabase')
    tcx.set(
        'xsi:schemaLocation',
        ' '.join([
            'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2',
            'http://www.garmin.com/xmlschemas/TrainingCenterDatabasev2.xsd',
            'http://www.garmin.com/xmlschemas/ActivityExtension/v2',
            'http://www.garmin.com/xmlschemas/ActivityExtensionv2.xsd',
            'http://www.garmin.com/xmlschemas/FatCalories/v1',
            'http://www.garmin.com/xmlschemas/fatcalorieextensionv1.xsd',
        ])
    )
    tcx.set('xmlns:ns5', 'http://www.garmin.com/xmlschemas/ActivityGoals/v1')
    tcx.set('xmlns:ns3', 'http://www.garmin.com/xmlschemas/ActivityExtension/v2')
    tcx.set('xmlns:ns2', 'http://www.garmin.com/xmlschemas/UserProfile/v2')
    tcx.set('xmlns', 'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2')
    tcx.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
    tcx.set('xmlns:ns4', 'http://www.garmin.com/xmlschemas/ProfileExtension/v1')

    activities = etree.SubElement(tcx, 'Activities')
    activity = etree.SubElement(activities, 'Activity')
    activity.attrib['Sport'] = 'Biking'
    for record in fitfile.get_messages('record'):
        vals = record.get_values()
        if 'timestamp' in vals:
            starttime = vals['timestamp']
        break
    activity_id = etree.SubElement(activity, 'Id')
    activity_id.text = starttime.strftime("%Y-%m-%dT%H:%M:%SZ")
    lap = etree.SubElement(activity, 'Lap')
    lap.attrib['StartTime'] = starttime.strftime("%Y-%m-%dT%H:%M:%SZ")
    track = etree.SubElement(lap, 'Track')

    for record in fitfile.get_messages('record'):
        vals = record.get_values()
        trackpoint = etree.SubElement(track, 'Trackpoint')
        if 'position_lat' in vals and 'position_long' in vals:
            p_lat, p_long = semi2deg(vals['position_lat']), semi2deg(vals['position_long'])
            position = etree.SubElement(trackpoint, 'Position')
            position_lat = etree.SubElement(position, 'LatitudeDegrees')
            position_long = etree.SubElement(position, 'LongitudeDegrees')
            position_long.text = str(p_lat)
            position_lat.text = str(p_long)
        if 'timestamp' in vals:
            timestamp = etree.SubElement(trackpoint, 'Time')
            timestamp.text = vals['timestamp'].strftime("%Y-%m-%dT%H:%M:%SZ")
        if 'heart_rate' in vals:
            heart_rate = etree.SubElement(
                etree.SubElement(trackpoint, 'HeartRateBpm'),'Value')
            heart_rate.attrib['xsi:type']="HeartRateInBeatsPerMinute_t"
            heart_rate.text = str(vals['heart_rate'])
        if 'altitude' in vals:
            altitude = etree.SubElement(trackpoint, 'AltitudeMeters')
            altitude.text = str(vals['altitude'])
        if 'distance' in vals:
            distance = etree.SubElement(trackpoint, 'DistanceMeters')
            distance.text = str(vals['distance'])
        if 'cadence' in vals:
            cadence = etree.SubElement(trackpoint, 'Cadence')
            cadence.text = str(vals['cadence'])
        # if 'temperature' in vals:
        #     temperature = etree.SubElement(trackpoint, 'Temperature')
        #     temperature.text = str(vals['temperature'])
        if 'power' in vals or 'speed' in vals:
            extensions = etree.SubElement(trackpoint, 'Extensions')
            tpx = etree.SubElement(extensions, 'ns3:TPX')
            tpx.attrib['CadenceSensor'] = 'Bike'
            if 'power' in vals:
                power = etree.SubElement(
                    etree.SubElement(extensions, 'ns3:Watts'),'Value')
                power.text = str(vals['power'])
            if 'speed' in vals:
                speed = etree.SubElement(extensions, 'ns3:Speed')
                speed.text = str(vals['speed']) # * 60.0 * 60.0 / 1000.0) # Convert m/s to km/h
                if not 'power' in vals:
                    power = etree.SubElement(extensions, 'ns3:Watts')
                    power.text = str(s2p(vals['speed'], lever))

    new_name = "vpower_" + fitfilename[:-3] + 'tcx'
    etree.ElementTree(tcx).write(new_name, encoding='utf-8', xml_declaration=True)

def main(argv=None):
    arguments = docopt(__doc__)
    inputfilename = arguments["INPUT"]
    if not inputfilename.endswith('.fit'):
        print ("input file %s has no .fit extention" % inputfilename)
        exit(-1)
    if arguments['--lever']:
        lever = int(arguments['--lever'])
        assert (lever > 0 and lever <11)
        sys.stderr.write('Handlebar resistance lever position = %d \n' % lever)
        sys.stderr.flush()
    else:
        lever = 5
        sys.stderr.write('Assuming default handlebar resistance lever postion at 5\n')
        sys.stderr.flush()
    process_file(inputfilename, lever)

if __name__ == "__main__":
    sys.exit(main())
