from codequick import Script
import os
import sys

def __callerInfo(args):
    frame = sys._getframe(2).f_code
    route = os.path.splitext(os.path.basename(frame.co_filename))[0]
    callback = frame.co_name
    return [route, callback] + list(args)

def log(lvl=Script.DEBUG, msg="", *args):
    Script.log("(%s.%s) " + msg, __callerInfo(args), lvl)

def debug(msg="", *args):
    Script.log("(%s.%s) " + msg, __callerInfo(args), Script.DEBUG)

def info(msg="", *args):
    Script.log("(%s.%s) " + msg, __callerInfo(args), Script.INFO)

def error(msg="", *args):
    Script.log("(%s.%s) " + msg, __callerInfo(args), Script.ERROR)