#!/usr/bin/env python

import urllib2
import urllib
import json
import sys
import os
import datetime
from progbar import AnimatedProgressBar

class Reporter(object):
    def __init__(self):
        self.flag = False

    def reporter(self, count, bz, tz):
        if not self.flag:
            self.p = AnimatedProgressBar(end=tz, width=40, marker=">", blank=".", fill="=")
            self.total_size = tz
            self.block_size = bz
            self.flag = True
        self.p + (count*bz)
        self.p.show_progress()

    def reset(self):
        self.flag = False

if sys.argv[1:2] == ['export']:
    try:
        print 'Gathering information...'
        r = urllib2.urlopen('http://railscasts.com/episodes.json')
        if sys.argv[2:3] == ['json']:
            with open('output.json', 'w') as f:
                f.write(r.read())
        else:
            data = json.loads(r.read())
            l = sorted(data, key=lambda x: x['position'])
            with open('output.txt', 'w') as f:
                f.write('\n'.join(map(lambda x: '%d-%s' % (x['position'], x['permalink']), l)))
        print 'Done.'
    except Exception:
        raise Exception
        r = None
    finally:
        if r is None:
            r.close()
else:
    SKIP_ALL = False
    if sys.argv[1:2] == ['--help'] or sys.argv[1:2] == ['-h']:
        print '''Usage:\n  download   -d    [xxx, [yyy, [...]]]\n  export           [json]\n  help       -h'''
        sys.exit(0)
    try:
        print 'Gathering download information...'
        r = urllib2.urlopen('http://railscasts.com/episodes.json')
        data = json.loads(r.read())
        with open('config.json') as f:
            config = json.loads(f.read())
        print 'Done.'
        print
    except Exception:
        raise Exception
        r = None
    finally:
        if r is None:
            r.close()

    format = config['format']

    if 'path' in config:
        savepath = os.path.abspath(config['path'])
    else:
        savepath = '.'

    pb = Reporter()
    files = [f for f in os.listdir(savepath) if os.path.isfile(os.path.join(savepath,f))]
    if sys.argv[1:2] == ['download'] or sys.argv[1:2] == ['-d']:
        auxdata = dict(map(lambda x: (x['position'], [x['permalink'], x['pro'], int(x['file_sizes'][format])]), data))
        for num in sys.argv[2:]:
            n = int(num)
            filename = '%03d-%s.%s' % (n, auxdata[n][0], format)
            filedir = '%s/%s' % (savepath, filename)
            if filename in files:
                if os.path.getsize(filedir) != auxdata[n][2]:
                    print "File %s seems corrupt..." % filename
                if SKIP_ALL:
                    print 'Skip:', filename
                    continue
                r = raw_input('Override: %s [y/N/a]: ' % filename).lower()
                if r != 'y':
                    if r == 'a':
                        SKIP_ALL = True
                    print 'Skip:', filename
                    continue
            print 'Download: %s' % filename
            pb.reset()
            start_t = datetime.datetime.now()
            if auxdata[n][1]:
                fetch_url = config['purl']
            else:
                fetch_url = config['url']
            urllib.urlretrieve(fetch_url+filename, filedir, reporthook=pb.reporter)
            if os.path.getsize(filedir) != auxdata[n][2]:
                raise Exception("Corrupt download")
            end_t = datetime.datetime.now()
            t = (end_t-start_t).total_seconds()
            print
            print 'Done in', t, 'seconds', '(%.2f KiB/s).' % (pb.total_size/(1024.0*t))
            print
        sys.exit(0)
    
    for d in data:
        filename = '%03d-%s.%s' % (d['position'], d['permalink'], format)
        filedir = '%s/%s' % (savepath, filename)
        if filename in files:
            if os.path.getsize(filedir) != int(d['file_sizes'][format]):
                print "File %s seems corrupt..." % filename
            if SKIP_ALL:
                print 'Skip:', filename
                continue
            r = raw_input('Override: %s [y/N/a]: ' % filename).lower()
            if r != 'y':
                if r == 'a':
                    SKIP_ALL = True
                print 'Skip:', filename
                continue
          
        print 'Download: %s' % filename
        pb.reset()
        start_t = datetime.datetime.now()
        if d['pro']:
            fetch_url = config['purl']
        else:
            fetch_url = config['url']
        urllib.urlretrieve(fetch_url+filename, filedir, reporthook=pb.reporter)
        if os.path.getsize(filedir) != int(d['file_sizes'][format]):
            raise Exception("Corrupt download")
        end_t = datetime.datetime.now()
        t = (end_t-start_t).total_seconds()
        print
        print 'Done in', t, 'seconds', '(%.2f KiB/s).' % (pb.total_size/(1024.0*t))
        print
