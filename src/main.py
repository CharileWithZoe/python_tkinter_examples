#-*-coding:utf-8-*-
#!/usr/bin/env python
import os
import sys
import re
import getopt
import subprocess
import keysplit
import threading
import time
import xml.dom.minidom
import devinfo
import tarfile

reload(sys)
sys.setdefaultencoding('utf8')

script_path = os.path.dirname(__file__)
if script_path:
    PYTHON_CMD="python "+script_path+os.sep
else:
    PYTHON_CMD="python "

wetest_mode = False
logs_in_dir = False
logs_in_tar = False
mtk_mode = False
fatal_only = False
performance_only = False
monkeypy_mode = False
pull_mode = False
janky_frame_merge = False
mtbf_mode = False
smart_mode = True
skips_reason = []

importent = []
unimportent = []

out_dir = None
debug_mode = False

def read_file(path):
    lines = [];
    f = open(path, "r")
    lines = f.readlines()
    f.close()
    return [line.strip() for line in lines]

def read_config():
    global importent
    global unimportent
    s = re.compile(r"\s*(\S+)")
    filepath = "config"+os.sep+"importent-process.txt"
    if os.path.exists(filepath):
        for l in read_file(filepath):
            match = s.search(l)
            if match:
                importent.append(match.groups()[0])
                #print "found importent",match.groups()[0]
    filepath = "config"+os.sep+"unimportent-process.txt"
    if os.path.exists(filepath):
        for l in read_file(filepath):
            match = s.search(l)
            if match:
                unimportent.append(match.groups()[0])
                #print "found unimportent",match.groups()[0]
    
def read_parsed_log(lines):
    bugs = []
    dict_re = re.compile(r"^\-\-\{(.*)\}:\s*(.*)")
    array_re = re.compile(r"^\-\-\[(.*)\]:")
    ls = []
    d = {}
    for l in lines:
        match = dict_re.search(l)
        if match:
            k,v = match.groups()[0],match.groups()[1]
            if k == "Path":
                d = {}
                bugs.append(d)
            d[k] = v
            continue
        match = array_re.search(l)
        if match:
            k = match.groups()[0]
            ls = []
            d[k] = ls
            continue
        ls.append(l)
    return bugs

def read_parsed_log_from_file(path):
    lines = read_file(path)
    return read_parsed_log(lines)

def bugreport_get(bug, key, default=""):
    if bug.has_key(key):
        return bug[key]
    return default

def bugreport_del_same(bugs):
    md5 = {}
    def f(b):
        k = bugreport_get(b, "MD5")
        if k == "":
            return True
        if not md5.has_key(k):
            md5[k] = ""
            return True
        return False
    
    return filter(f,bugs)

cache={}
def bugreport_get_keysplit(bug):
    md5 = bugreport_get(bug, "MD5", None)
    if md5 and cache.has_key(md5):
        return cache[md5]
    d1 = {}
    for l in bugreport_get(bug, "logs", []):
        keysplit.keyword_split(d1, l)
    if md5:
        cache[md5] = d1
    return d1
        
def bugreport_same(bug1, bug2):
    d1 = bugreport_get_keysplit(bug1)
    d2 = bugreport_get_keysplit(bug2)
    u = keysplit.keyword_score(keysplit.keyword_union(d1,d2))
    diff = keysplit.keyword_score(keysplit.keyword_difference(d1,d2))
    if u == 0:
        return False
    s = 1 - diff*1.0/u
    #print "s",s,"union",u,"diff",diff
    if s > 0.9:
        return True
    else:
        return False
def bugreport_insert(bug, bugs):
    for bs in bugs[2:]:
        for b in bs:
            if bugreport_same(bug, b):
                bs.append(bug)
                return True
    return False

def bugset_mk():
    return {}

#[total, nclass, [class1,..],[class2,..]]
def bugset_insert(bset, bug):
    def insert_bug(bugs):
        for bs in bugs[2:]:
            tt = 10
            for b in bs:
                if bugreport_same(bug, b):
                    bs.append(bug)
                    return True
                tt -= 1
                if tt <= 0:
                    break
        return False

    reason = bugreport_get(bug,"Reason")
    if not bset.has_key(reason):
        bset[reason] = [1,1,[bug]]
        return
    if bugreport_get(bug,"Reason") == "JankyFrame" and not janky_frame_merge:
        bset[reason][1] += 1
        bset[reason].append([bug])
    elif not insert_bug(bset[reason]):
        bset[reason][1] += 1
        bset[reason].append([bug])
    bset[reason][0] += 1
    return 


def bugreport_merge(bugs):
    d = {}
    for bug in bugs:
        proc = bugreport_get(bug,"process_name")
        if not d.has_key(proc):
            d[proc] = bugset_mk()
        bugset_insert(d[proc], bug)
    return d


def bugset_detail(s, detail = None):
    count = 0
    (p, d) = s
    for k,v in d.items():
        count += v[0]
    line = "%-40s %4d "%(p, count)
    for k,v in d.items():
        line += " %-15s %4d %4d"%(k, v[0], v[1])
    if detail:
        line += "\n"
        line += "\n"
        for k,v in d.items():
            for e in v[2:]:
                line += "\n"
                line += "\n"
                line += bugreport_str(e[0])
                for ee in e[1:]:
                    if debug_mode:
                        line += bugreport_str(ee)
                    else:
                        line += bugreport_simple(ee)
    return line

def bugreport_str(bug):
    line = ""
    t = bug.keys()
    for k in ["logs","stack"]:
        if k in t:
            t.remove(k)
            t.append(k)
    for k in ["Reason","process_name"]:
        if k in t:
            t.remove(k)
            t.insert(0, k)
    for k in t:
        v = bug[k]
        if type(bug[k]) == type([]):
            line += "%s\n"%k
            for l in bug[k]:
                line += l+"\n"
            continue
        line += "%s: %s\n"%(k,v)
    return line

def bugreport_simple(bug):
    line = ""
    for k in ["Path","MD5"]:
        v = bug[k]
        if type(bug[k]) == type([]):
            line += "%s\n"%k
            for l in bug[k]:
                line += l+"\n"
            continue
        line += "%s: %s\n"%(k,v)
    return line

def save_bugset_to_file(d):
    if not out_dir:
        return
    (k,v) = d
    name = k.replace("/","-").replace(" ","").replace(":","")
    l = bugset_detail(d, detail=True)
    f = open(out_dir+os.sep+name+".txt", "w")
    f.write(l)
    f.close()
    
    
def foreach_bugset(d, f):
    def fn(k):
        c = map(lambda x:x[0],d[k[0]].values())
        return reduce(lambda x,y: x+y, c)
    d1 = sorted(d.items(), key=fn, reverse=True)
    for k,v in d1:
        f((k, v))

def pr_bugset(d):
    (k,v) = d
    print bugset_detail(d, detail=True)

def pr_bugset_simple(d):
    (k,v) = d
    s = bugset_detail(d, detail=False)
    if performance_only:
        a = s.split("\n")
        s = ""
        for i in a:
            if i.find("Non-protected-broadcast") > 0:
                s += i
    if s != "":
        print s
    if out_dir and s != "":
        f = open(out_dir+os.sep+"result.txt", "a+")
        f.write(s+"\n")
        f.close()
    
def print_bugreport(bug):
    print bugreport_str(bug)
        
def find_commit_for_fatal_bugs(l):
    cmd = PYTHON_CMD+"ico.py --fatal-only "+l
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    lines = p.stdout
    bs = bugreport_del_same(read_parsed_log([line.strip() for line in lines]))
    d = bugreport_merge(bs)
    foreach_bugset(d, pr_bugset)
    foreach_bugset(d, commit_log_for_bugset)
    return 

def call_ico(l):
    cmd = PYTHON_CMD+"ico.py "
    if mtk_mode:
       cmd += "--mtk "
    if fatal_only:
       cmd += "--fatal-only " 
    if wetest_mode:
        cmd = cmd + "--wetest "+l
    elif logs_in_dir:
        cmd = cmd + l + os.sep
    elif logs_in_tar or monkeypy_mode or pull_mode or mtbf_mode or smart_mode:
        cmd = cmd + l
    else:
        cmd = cmd+l+os.sep+"logs.tar.gz"
    print "cmd",cmd
    sys.stdout.flush()

    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    lines = p.stdout
    if pull_mode and os.path.isdir(l):
        fhandle = open(l+os.sep+"logs_parsed.txt","w")
    else:
        fhandle = open(l+".txt","w")
    for l in lines:
        fhandle.write(l)
    fhandle.close()
num_cpu = 4
def call_ico_parallel(a, n=4):
    def action(arg):
        for l in arg:
            print "%s: parsing %s"%(threading.currentThread().getName(), l)
            sys.stdout.flush()
            call_ico(l)
    def task_split(a, n):
        tasks = []
        l = 0
        step = (len(a)+n-1)/n
        if step <= 0:
            step = 1
        print "step",step
        print "len a",len(a)
        sys.stdout.flush()
        while(l < len(a)):
            tasks.append(a[l:(l+step)])
            l+=step
        return tasks
    thread_list = []
    for i in task_split(a, n):
        t =threading.Thread(target=action,args=(i,))
        t.setDaemon(True)
        thread_list.append(t)
    for t in thread_list:
        t.start()

    for t in thread_list:
        t.join()


class modify:
    def __init__(self):
        self.dict = {}
        self.keyword = {}
        pass
    def __str__(self):
        line = ""
        for k,v in self.dict.items():
            line += "========================================================================\n"
            line += "++++++++++++++++++++++++"+k+"++++++++++++++++++++++++++++\n"
            line +=  v + "\n"
        line += "\n\n"
        return line
    def ksplit(self):
        kadd = {}
        kremove = {}
        if self.dict.has_key("detail"):
            str = self.dict["detail"]
            for s in str.split("\n"):
                if re.compile(r'^[\+][^\+]').match(s):
                    keysplit.keyword_split(kadd, s)
                elif re.compile(r'^[-][^-]').match(s):
                    keysplit.keyword_split(kremove, s)
            keysplit.keyword_find_filename(self.keyword, str)
            keysplit.keyword_find_fundef(self.keyword, str)
            keysplit.keyword_find_string(self.keyword, str)
        for k,v in keysplit.keyword_union(kadd, kremove).items():
            self.keyword[k] = min(self.keyword[k], v) if self.keyword.has_key(k) else v
        
    def kprint(self):
        keysplit.keyword_print(self.keyword)

        
def read_modify(xmlfile):
    DOMTree = xml.dom.minidom.parse(xmlfile)
    modifys = []
    for e in  DOMTree.getElementsByTagName('entity'):
        me = modify()
        modifys.append(me)
        for m in e.childNodes:
            me.dict[m.tagName] = m.childNodes[0].data
    return modifys



def printxml(xmlfile):
    DOMTree = xml.dom.minidom.parse(xmlfile)
    for e in  DOMTree.getElementsByTagName('entity'):
        print "**********************************************************************"
        ee = e.childNodes
        for m in ee:
            print "========================================================================"
            print "++++++++++++++++++++++++",m.tagName,"++++++++++++++++++++++++++++"
            if m.tagName == "detail":
                print "skip print detail"            
            else:
                print m.childNodes[0].data
                
            print "========================================================================"
        print "**********************************************************************"

def download_commit_log(s):
    print "try to download",s
    if not os.path.isdir("commit-log"):
        print "mkdir commit-log"
        os.mkdir("commit-log")
    if not os.path.isfile("commit-log"+os.sep+s):
        print "try to download",s
        os.system("wget http://10.67.16.29/log/"+s+" -O commit-log"+os.sep+s)
    else:
        print s,"exist"
    
def try_find_commit(bugs):
    for bug in bugs:
        if "system_server" == bugreport_get(bug, "process_name"):
            utc = bugreport_get(bug, "ro.build.date.utc", None)
            modifys = None
            if utc:
                print "utc",utc
                s=time.strftime("%Y%m%d",time.localtime(int(utc)-24*60*60))+".xml"
                download_commit_log(s)
                if os.path.isfile("commit-log"+os.sep+s):
                    modifys = read_modify("commit-log"+os.sep+s)
            if not modifys:
                print "commit log not found"
                return
            bugkeyd = {}
            compare_result = []
            for l in bugreport_get(bug, "logs", []):
                keysplit.keyword_split(bugkeyd, l)
            for m in modifys:
                m.ksplit()
                tmpd = keysplit.keyword_intersection(bugkeyd, m.keyword)
                score = keysplit.keyword_score(tmpd)
                compare_result.append((score, m))
            s_compare_result = sorted(compare_result, key=lambda k:k[0], reverse=True)
            print "score:", s_compare_result[0][0]
            print "commit:", s_compare_result[0][1]
            print "\n"
            if True:
                tmpd = keysplit.keyword_intersection(bugkeyd, s_compare_result[0][1].keyword)
                print "bugkeyd"
                print ""
                for (k, v) in sorted(bugkeyd.iteritems(), key=lambda k:k[1], reverse=True):
                    print k,":    ",v

                print ""
                print "tmpd\n"
                for (k, v) in sorted(tmpd.iteritems(), key=lambda k:k[1], reverse=True):
                    print k,":    ",v
                print ""
                print ""

                tmpd = keysplit.keyword_intersection(bugkeyd, s_compare_result[1][1].keyword)
                print "tmpd2\n"
                for (k, v) in sorted(tmpd.iteritems(), key=lambda k:k[1], reverse=True):
                    print k,":    ",v
                print ""
                print ""
            for (score, m) in s_compare_result[1:10]:
                print "score:", score
                print m.dict["content"]

def commit_log_for_bugset(s):
    count = 0
    (p, d) = s
    for k,v in d.items():
        for e in v[2:]:
            try_find_commit([e[0]])
    return ""
            
find_commit = False

def collect_all_files(dirpath):
    allfiles = []
    for root,dirs,files in os.walk(dirpath):
        for f in files:
            allfiles.append(root + os.sep + f)
    return allfiles
            
def collect_monkeypy_logs(dirpath):
    files = collect_all_files(dirpath)
    fn = lambda x: x.endswith("logs.tar.gz") and not os.path.isfile(x+".txt")
    return filter(fn, files)

def collect_monkeypy_parsed_logs(dirpath):
    files = collect_all_files(dirpath)
    fn = lambda x: x.endswith("logs.tar.gz") and os.path.isfile(x+".txt")
    return map(lambda x:x+".txt", filter(fn, files))

def collect_mtbf_logs(dirpath):
    files = collect_all_files(dirpath)
    fn = lambda x: x.endswith(".tar.gz") and not os.path.isfile(x+".txt")
    return filter(fn, files)

def collect_mtbf_parsed_logs(dirpath):
    files = collect_all_files(dirpath)
    fn = lambda x: x.endswith(".tar.gz") and os.path.isfile(x+".txt")
    return map(lambda x:x+".txt", filter(fn, files))

def collect_logs(logs_dir):
    logs = [logs_dir+os.sep+i for i in os.listdir(logs_dir)]
    if wetest_mode or logs_in_tar:
        f = lambda x: x.find(".txt") < 0 and os.path.isfile(x) and not os.path.isfile(x+".txt")
    else:
        f = lambda x: os.path.isdir(x) and not os.path.isfile(x+".txt")
    return filter(f, logs)

def collect_parsed_logs(logs_dir):
    logs = [logs_dir+os.sep+i for i in os.listdir(logs_dir)]
    if wetest_mode or logs_in_tar:
        f = lambda x: x.find(".txt") < 0 and os.path.isfile(x) and os.path.isfile(x+".txt")
    else:
        f = lambda x: os.path.isdir(x) and os.path.isfile(x+".txt")
    return map(lambda x:x+".txt", filter(f, logs))


def guess_tar_logs(path):
    tar = tarfile.open(path, mode="r:gz")
    wetest = re.compile(r"adb.*\.tar\.gz")
    for name in tar.getnames():
        dirname,filename = os.path.split(name)
        if filename == "logs.tar.gz":
            return name
        if wetest.search(filename):
            return filename
    return None

def listdir(d):
    if os.path.isdir(d):
        return [d+os.sep+i for i in os.listdir(d)]
    return []

def search_valiad_logs(log):
    def is_monkeypy_log(log):
        if os.path.isfile(log+os.sep+"logs.tar.gz"):
            return [log+os.sep+"logs.tar.gz"]
        return None
    def is_pull_logs(log):
        files = []
        if os.path.exists(log+".tar.gz"):
            return None
        for v in listdir(log):
            files.append(v)
            if os.path.isdir(v):
                files.extend(listdir(v))
        match = 0
        pull_log_name = ["kernel"+os.sep+"log_kernel","kernel"+os.sep+"selinux_audit.txt",
                         "tz"+os.sep+"tz.txt","resetlog"+os.sep+"smem_","resetlog"+os.sep+"smd_",
                         "resetlog"+os.sep+"kernel_","tz"+os.sep+"qsee.txt",
                         "logcat"+os.sep+"exit_", "logcat"+os.sep+"logcat_",
                         "logcat"+os.sep+"anr_", "logcat"+os.sep+"baseinfo.txt"]
        for f in pull_log_name:
            for ff in files:
                if ff.find(f) >= 0:
                    match += 1
                if match > 10:
                    return log
        return None
    def is_wetest_log(log):
        d = []
        if os.path.exists(log+".tar.gz"):
            return d
        files = collect_all_files(log)
        for f in files:
            if f.endswith(".tar.gz") > 0 and (f.find("StrictMode") >= 0 or f.find("MT_") >= 0 or f.find("Multi") >= 0) and guess_tar_logs(f):
                d.append(f)
        return d
    if os.path.isfile(log) and log.endswith(".tar.gz") > 0:
        return [log]
    if os.path.isdir(log) and is_pull_logs(log):
        return [log]
    elif os.path.isdir(log):
        d = []
        logs = [log+os.sep+i for i in os.listdir(log)]
        for l in logs:
            if os.path.isfile(l) and l.endswith(".tar.gz"):
                d.append(l)
                continue
            if os.path.isdir(l) and is_pull_logs(l):
                d.append(l)
                continue
            t = is_monkeypy_log(l)
            if t:
                d.extend(t)
            wl = is_wetest_log(l)
            if wl:
                d.extend(is_wetest_log(l))
            elif os.path.isdir(l) and not os.path.exists(l+os.sep+"tar.gz"):
                d.append(l)
        if len(d) > 0:
            return d
    return []
        
        
def collect_logs_smart(logs_path):
    logs = search_valiad_logs(logs_path)
    f = lambda x: not os.path.exists(x+".txt")
    r = filter(f, logs)
    print "smart logs",r
    return r

def collect_parsed_logs_smart(logs_path):
    logs = search_valiad_logs(logs_path)
    f = lambda x: os.path.exists(x+".txt")
    r = map(lambda x:x+".txt", filter(f, logs))
    print "smart parsed logs",r
    return r

def collect_pull_logs(logs_dir):
    r = re.compile(r"loglast\d*\.tar.gz$")
    logs = [logs_dir+os.sep+i for i in os.listdir(logs_dir)]
    f = lambda x: os.path.isfile(x) and not os.path.isfile(x+".txt") and r.search(x)
    result = []
    if not os.path.isfile(logs_dir+os.sep+"logs_parsed.txt"):
        result = [logs_dir]
    result.extend(filter(f, logs))
    return result

def collect_pull_parsed_logs(logs_dir):
    r = re.compile(r"loglast\d*\.tar.gz$")
    logs = [logs_dir+os.sep+i for i in os.listdir(logs_dir)]
    f = lambda x: os.path.isfile(x) and os.path.isfile(x+".txt") and r.search(x)
    result = []
    if os.path.isfile(logs_dir+os.sep+"logs_parsed.txt"):
        result = [logs_dir+os.sep+"logs_parsed"]
    result.extend(filter(f, logs))
    return map(lambda x:x+".txt", result)

def main():
    def_config = None
    compare_to_config = None
    try:
        opts, args = getopt.getopt(sys.argv[1:],"ho:",["fatal-only","wetest","debug","ncpu=","find-commit","phone-info=","log-in-dir","def-config=","compare-to=","mtk","log-in-tar","performance","monkeypy","pull","jf-merge","mtbf","smart", "skip="])
    except getopt.GetoptError:
        print 'ico.py [--fatal-only] logs'
        sys.exit(-1)
    for opt, arg in opts:
        #print "opt",opt
        if opt == '-h':
            print 'ico.py [--fatal-only] logs'
            sys.exit()
        if opt == '--fatal-only':
            global fatal_only
            fatal_only = True
        if opt == '--wetest':
            global wetest_mode
            wetest_mode = True
        if opt == '--monkeypy':
            global monkeypy_mode
            monkeypy_mode = True
        if opt == '--mtbf':
            global mtbf_mode
            mtbf_mode = True
        if opt == '--smart':
            global smart_mode
            smart_mode = False
        if opt == '--pull':
            global pull_mode
            pull_mode = True
        if opt == '--log-in-dir':
            global logs_in_dir
            logs_in_dir = True
        if opt == '--log-in-tar':
            global logs_in_tar
            logs_in_tar = True
        if opt == '-o':
            global out_dir
            out_dir = arg
            if not os.path.isdir(out_dir):
                os.mkdir(out_dir)
            if not os.path.isdir(out_dir):
                print "mkdir fail"
                sys.exit(-1)
        if opt == '--debug':
            global debug_mode
            debug_mode = True
        if opt == '--find-commit':
            global find_commit
            find_commit = True
        if opt == '--ncpu':
            global num_cpu
            num_cpu = int(arg)
        if opt == '--phone-info':
            fname = arg
            devinfo.get_phone_config(fname)
            return
        if opt == '--def-config':
            def_config = arg
        if opt == '--compare-to':
            compare_to_config = arg
        if opt == '--mtk':
            global mtk_mode
            mtk_mode = True
        if opt == '--performance':
            global performance_only
            performance_only = True
        if opt == '--jf-merge':
            global janky_frame_merge
            janky_frame_merge = True
        if opt == '--skip':
            global skips_reason
            skips_reason.extend(arg.split(","))
            
    if def_config and compare_to_config:
        (i, ni) = devinfo.read_def_config(def_config)
        cs = devinfo.read_compared_file(compare_to_config)
        devinfo.print_compare_config(i, ni, cs)
        return 0
    print "args",args
    if find_commit and (os.path.isfile(args[0]) or os.path.isdir(args[0])):
        find_commit_for_fatal_bugs(args[0])
        return 0
    logs_dir = "logs"
    if len(args) <= 0:
        if not os.path.isdir(logs_dir):
            return
    else:
        logs_dir = args[0]
    logs_dir = logs_dir.strip(os.sep)
    logs_dir = unicode(logs_dir,"utf-8")
    read_config()
    if os.path.isfile(logs_dir) and logs_dir.endswith(".tar.gz"):
        cmd = PYTHON_CMD+"ico.py "
        if fatal_only:
            cmd += "--fatal-only "
        cmd += " "+logs_dir
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
        lines = p.stdout.readlines()
        bugs = []
        bugs.extend(read_parsed_log([line.strip() for line in lines]))
        bs = bugreport_del_same(bugs)
        bs = filter(lambda x:bugreport_get(x,"Reason") not in skips_reason, bs)
        d = bugreport_merge(bs)
        importent_bugs = {}
        for (k,v) in d.items():
            if k in importent:
                importent_bugs[k] = v
                del d[k]
        print ""
        print ""
        if out_dir:
            if os.path.isfile(out_dir+os.sep+"result.txt"):
                os.unlink(out_dir+os.sep+"result.txt")
        if len(importent_bugs.keys()) > 0:
            print "Fatal bugs:"
            foreach_bugset(importent_bugs, pr_bugset_simple)
            foreach_bugset(importent_bugs, save_bugset_to_file)
            print ""
            print ""
        if len(d.keys()) > 0:
            print "Bugs:"
            foreach_bugset(d, pr_bugset_simple)
            foreach_bugset(d, save_bugset_to_file)
    elif os.path.isdir(logs_dir):
        cl = collect_logs
        cpl = collect_parsed_logs
        if monkeypy_mode:
            cl = collect_monkeypy_logs
            cpl = collect_monkeypy_parsed_logs
        elif pull_mode:
            cl = collect_pull_logs
            cpl = collect_pull_parsed_logs
        elif mtbf_mode:
            cl = collect_mtbf_logs
            cpl = collect_mtbf_parsed_logs
        elif smart_mode:
            cl = collect_logs_smart
            cpl = collect_parsed_logs_smart
        sys.stdout.flush()
        call_ico_parallel(cl(logs_dir), num_cpu)
        bugs = []
        for l in cpl(logs_dir):
            #print "found txt",l
            bugs.extend(read_parsed_log_from_file(l))
        #print_bugreport(bugs[0])
        #print ""
        #print ""
        bs = bugreport_del_same(bugs)
        #print "before",len(bugs),"after",len(bs)
        bs = filter(lambda x:bugreport_get(x,"Reason") not in skips_reason, bs)
        d = bugreport_merge(bs)
        importent_bugs = {}
        for (k,v) in d.items():
            if k in importent:
                importent_bugs[k] = v
                del d[k]
        print ""
        print ""
        if out_dir:
            if os.path.isfile(out_dir+os.sep+"result.txt"):
                os.unlink(out_dir+os.sep+"result.txt")
        if len(importent_bugs.keys()) > 0:
            print "Fatal bugs:"
            foreach_bugset(importent_bugs, pr_bugset_simple)
            foreach_bugset(importent_bugs, save_bugset_to_file)
            print ""
            print ""
        if len(d.keys()) > 0:
            print "Bugs:"
            foreach_bugset(d, pr_bugset_simple)
            foreach_bugset(d, save_bugset_to_file)
        
    else:
        print args[0],"not exist"
        sys.exit(-1)
    if find_commit and len(importent_bugs.items()) > 0:
        foreach_bugset(importent_bugs, commit_log_for_bugset)
            
main()


