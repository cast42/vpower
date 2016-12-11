#!/usr/bin/env python

"""tcx_vpower.py.

Usage:
  tcx_vpower.py [--lever=<lv>] INPUT

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


ns1 = 'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2'
ns2 = 'http://www.garmin.com/xmlschemas/ActivityExtension/v2'

def s2p(speed, lever=5):
    assert (lever > 0 and lever < 11)
    # The array factor contains power at 60km/h at lever positions 1 to 10
    factor1 =  [200.0,281.0,366.0,447.0,532.0,614.0,702.0,787.0,868.0,953.0]
    # The array factor contains power at 29.9km/h at lever positions 1 to 10
    factor2 =  [85.0,121.0,162.0,196.0,236.0,272.0,307.0,347.0,382.0,417.0]
    w = int(factor2[lever-1]+(speed-29.9)/30.1*(factor1[lever-1]-factor2[lever-1]))
    return w if w > 0 else 0

def process_trackpoint(trackpoint, lever):
     for child in trackpoint:
        for elem in child.iter():
            if elem.tag == '{%s}TPX'%ns2:
                #elem.attrib['xmlns'] = ns2
                for node in elem.iter():
                    if node.tag == '{%s}Speed'%ns2:
                        speed_in_m_per_sec = float(node.text)
                        speed_km_per_h = speed_in_m_per_sec /1000.0 * 60 *60
                        power = s2p(speed_km_per_h, lever)
                        # add power to trackpoint
                        w = etree.SubElement(elem, '{%s}Watts'%ns2)
                        w.text = str(power)
                        w.tail = '\n'


def process_track(track, lever):
    """
    Process a TCX file track element.
    """
    for child in track:
        if child.tag == '{%s}Trackpoint'%ns2:
            process_trackpoint(child, lever)

def process_file(tcxfile, lever):
    """
    Process the whole TCX file.
    """

    tree = etree.parse(tcxfile)
    root = tree.getroot()

    tracks = []

    for element in root.iter():
        if element.tag == '{%s}Track'%ns2:
            tracks.append(element)

    for element in tracks:
        process_track(element, lever)

    new_name = "vpower_" + tcxfile
    tree.write(new_name, encoding='utf-8', xml_declaration=True)

def main(argv=None):
    arguments = docopt(__doc__)
    inputfilename = arguments["INPUT"]
    if not inputfilename.endswith('.tcx'):
        print ("input file %s has no .tcx extention" % inputfilename)
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
