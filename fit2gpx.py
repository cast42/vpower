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

    header = """<gpx xmlns="http://www.topografix.com/GPX/1/1"
        creator="https://github.com/cast42/vpower"
        version="1.1"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd">
    """

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
            f.write('  </trkpt>\n')
        f.write('  </trk>\n')
        f.write("</gpx>")
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