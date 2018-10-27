#!/usr/bin/env python
"""fit2gpx.py.

Usage:
  fit2gpx.py  INPUT

Arguments:
  INPUT         Required .fit input filename

Options:
  -h --help     Show this.

"""
from __future__ import print_function
from __future__ import division
import sys
from fitparse import FitFile, FitParseError
from datetime import datetime
from docopt import docopt

def process_file(inputfilename):
    try:
        fitfile = FitFile(inputfilename)
        fitfile.parse()
    except FitParseError, e:
        print ("Error while parsing .FIT file: %s" % e)
        sys.exit(1)

    header = """<?xml version="1.0" encoding="UTF-8"?>
    <gpx creator="https://github.com/cast42/vpower" 
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="http://www.topografix.com/GPX/1/1
        http://www.topografix.com/GPX/1/1/gpx.xsd
        http://www.garmin.com/xmlschemas/GpxExtensions/v3
        http://www.garmin.com/xmlschemas/GpxExtensionsv3.xsd
        http://www.garmin.com/xmlschemas/TrackPointExtension/v1
        http://www.garmin.com/xmlschemas/TrackPointExtensionv1.xsd"
        version="1.1" xmlns="http://www.topografix.com/GPX/1/1"
        xmlns:gpxtpx="http://www.garmin.com/xmlschemas/TrackPointExtension/v1"
        xmlns:gpxx="http://www.garmin.com/xmlschemas/GpxExtensions/v3">
"""
#  <metadata>
#   <time>2018-10-13T06:24:30Z</time>
#  </metadata>

    with open(inputfilename[:-3]+'gpx','w') as f:
        f.write(header)
        # Get all data messages that are of type record
        f.write('  <trk>\n')
        for record in fitfile.get_messages('record'):
            # Go through all the data entries in this record
            vals = record.get_values()
            f.write('  <trkpt lat="%s" lon="%s">\n' % (vals['position_lat'], vals['position_long']))
            if 'altitude' in vals:
                f.write('   <ele>%s</ele>\n' % vals['altitude'])
            if 'timestamp' in vals:
                #ts = dt.datetime.strptime(vals['timestamp'], "%Y-%m-%d %H:%M:%S").replace(tzinfo=dt.timezone.utc)
                f.write('   <time>%s</time>\n' % vals['timestamp'].strftime("%Y-%m-%dT%H:%M:%SZ"))
            if 'speed' in vals:
                f.write('   <speed>%s</speed>\n' % vals['speed'])
            if 'temperature' in vals or 'heart_rate' in vals or 'cadence' in vals:
                f.write('   <extensions>\n')
                f.write('    <gpxtpx:TrackPointExtension>\n')
                if 'temperature' in vals:
                    f.write('    <gpxtpx:atemp>%s</gpxtpx:atemp>\n' % vals['temperature'])
                if 'heart_rate' in vals:
                    f.write('    <gpxtpx:hr>%s</gpxtpx:hr>\n' % vals['heart_rate'])
                if 'cadence' in vals:
                    f.write('    <gpxtpx:cad>%s</gpxtpx:cad>\n' % vals['cadence'])
                f.write('   </gpxtpx:TrackPointExtension>\n')
                f.write('  </extensions>\n')
            f.write('  </trkpt>\n')
        f.write('  </trk>\n')
        f.write('</gpx>')
        f.close()

def main(argv=None):
    arguments = docopt(__doc__)
    inputfilename = arguments["INPUT"]
    if not inputfilename.endswith('.fit'):
        print ("input file %s has no .fit extention" % inputfilename)
        exit(-1)
    process_file(inputfilename)

if __name__ == "__main__":
    sys.exit(main())