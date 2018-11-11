#!/usr/bin/env python

import os
import sys
import re
import gzip
import tarfile
import time
import getopt
import hashlib
import subprocess
import string
import random

reload(sys)
sys.setdefaultencoding('utf8')

def listfile(path):
    item = {}
    for root,dirs,files in os.walk(path):
        for f in files:
            item[root + os.sep + f] = ""
    return item

def logs_read(path):
    buf = ""
    try:
        tar = None
        if path.endswith("tar.gz"):
            tar = tarfile.open(path)
            name = tar.getnames()[0]
            f = tar.extractfile(name)
        elif path.endswith(".gz"):
            f = gzip.open(path, 'rb')
        else:
            f = open(path, 'rb')
        buf = f.read()
        f.close()
        if tar:
            tar.close()
    except Exception,e:
        print e
    return buf

#"all.log.event.txt"
def join_logs(logs, outfile):
    if len(logs) <= 0:
        print "no logs to join"
        return
    dirname,filename = os.path.split(logs[0])
    outdir = dirname
    print "====================================================================="
    print "out",dirname+os.sep+outfile
    print ""
    try:
        f = open(dirname+os.sep+outfile,"wb")
        for l in logs:
            dirname,filename = os.path.split(l)
            dirname1,filename1 = os.path.split(dirname)
            print filename1+os.sep+filename
            buf = logs_read(l)
            f.write(buf)
        f.close()
    except Exception,e:
        print e
    return outdir

def split_multi_logs(logs):
    d = {}
    for l in logs:
        dirname,filename = os.path.split(l)
        if not d.has_key(dirname):
            d[dirname] = [] 
        d[dirname].append(l)
    return d

def get_time_from_log(line):
    result = []
    r = re.compile(r'(\d\d-\d\d\s+\d\d:\d\d:\d\d)')
    match = r.match(line)
    if match:
        return match.group().replace("-","").replace(" ","_").replace(":","")
    return "0000_000000"

def split_log(infile, outfile, maxsize=1024*1024*100):
    if os.path.getsize(infile) <= maxsize:
        return
    f = open(infile, 'rb')
    w = open(outfile+".tmp", "wb")
    startt = None
    last_line = None
    for l in f.xreadlines():
        if not startt:
            startt = get_time_from_log(l)
        last_line = l
        w.write(l)
        if w.tell() >= maxsize:
            w.close()
            endt = get_time_from_log(l)
            if os.path.isfile(outfile+"-"+startt+"-"+endt+".txt"):
                os.remove(outfile+"-"+startt+"-"+endt+".txt")
            os.rename(outfile+".tmp", outfile+"-"+startt+"-"+endt+".txt")
            startt = endt
            w = open(outfile+".tmp", "wb")
    f.close()
    w.close()
    endt = get_time_from_log(last_line)
    if os.path.isfile(outfile+"-"+startt+"-"+endt+".txt"):
        os.remove(outfile+"-"+startt+"-"+endt+".txt")
    os.rename(outfile+".tmp", outfile+"-"+startt+"-"+endt+".txt")
    os.remove(infile)
    
def main(path):
    files = listfile(path)
    for jl in ["main","radio","events","crash","system"]:
        logs = sorted(filter(lambda x:x.find("logcat"+os.sep+"logcat_"+jl)>=0, files.keys()), reverse=True)
        for k,v in split_multi_logs(logs).items():
            out_dir = None
            out_dir = join_logs(v, "all.log."+jl+".txt")
            if out_dir:
                split_log(out_dir+os.sep+"all.log."+jl+".txt", out_dir+os.sep+"all.log."+jl, 100*1024*1024)

    for jl in ["kernel"]:
        logs = sorted(filter(lambda x:x.find("kernel"+os.sep+"log_"+jl)>=0, files.keys()), reverse=True)
        for k,v in split_multi_logs(logs).items():
            join_logs(v, "all.log."+jl+".txt")

if __name__ == '__main__':
    if len(sys.argv) <= 1:
        print "need log dir"
        sys.exit()
    path = sys.argv[1]
    path = unicode(path, "utf-8")
    if not os.path.isdir(path):
        print path,"not exist"
        sys.exit()
    main(path)


