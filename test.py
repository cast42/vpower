from __future__ import print_function
from __future__ import division
import sys
from fitparse import FitFile, FitParseError
from datetime import datetime

def s2p(speed, lever=5):
    assert (lever > 0 and lever < 11)
    # The array factor contains power at 60km/h at lever positions 1 to 10
    factor1 =  [200.0,281.0,366.0,447.0,532.0,614.0,702.0,787.0,868.0,953.0]
    # The array factor contains power at 29.9km/h at lever positions 1 to 10
    factor2 =  [85.0,121.0,162.0,196.0,236.0,272.0,307.0,347.0,382.0,417.0]
    w = int(factor2[lever-1]+(speed-29.9)/30.1*(factor1[lever-1]-factor2[lever-1]))
    return w if w > 0 else 0

# fitfile = FitFile('23031620.fit')

try:
    fitfile = FitFile('23031620.fit')
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

with open("test.gpx",'w') as f:
    f.write(header)
    # Get all data messages that are of type record
    f.write('  <trk>\n')
    for record in fitfile.get_messages('record'):
        # Go through all the data entries in this record
        #vals = {record_data.name:record_data.value for record_data in record}
        vals = record.get_values()
        f.write('  <trkpt lat="%s" lon="%s">\n' % (vals['position_lat'], vals['position_long']))
        if 'altitude' in vals:
            f.write('   <ele>%s</ele>\n' % vals['altitude'])
        if 'timestamp' in vals:
            #ts = dt.datetime.strptime(vals['timestamp'], "%Y-%m-%d %H:%M:%S").replace(tzinfo=dt.timezone.utc)
            f.write('   <time>%s</time>\n' % vals['timestamp'].strftime("%Y-%m-%dT%H:%M:%SZ"))
        f.write('  </trkpt>\n')
    f.write('  </trk>\n')
    f.write("</gpx>")
    f.close()
