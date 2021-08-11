from __future__ import absolute_import
import os
import sys
from mediasetinfinity.support.routing import Script

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

def notify(heading, message, icon=None, display_time=5000, sound=True):
    Script.notify(heading, message, icon, display_time, sound)