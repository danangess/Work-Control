#!/usr/bin/env python

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

import threading
import signal
import sys
import dbus
from subprocess import call
import gi
gi.require_version('Notify', '0.7')
from gi.repository import Notify
from gi.repository import GObject as gobject
from dbus.mainloop.glib import DBusGMainLoop
from datetime import datetime, timedelta

class Utility():
    def diff_time(self, isodate1, isodate2):
        if isodate1 > isodate2:
            tm = isodate1 - isodate2
        else:
            tm = isodate2 - isodate1

        tm = tm.total_seconds()
        hour = 0
        minute = 0
        second = 0
        if tm > 3600:
            hour = int(tm/3600)
        if tm%3600 > 60:
            minute = int((tm%3600)/60)
        if tm%60 > 0:
            second = int(tm%60)

        output = ''
        if hour > 0:
            output = '{hour} Hours '.format(hour=hour)
        if minute > 0:
            output = output+'{minute} Minutes '.format(minute=minute)
        if second >= 0:
            output = output+'{second} Seconds'.format(second=second)

        return output

    def convert_date(self, isodate):
        return isodate.strftime("%A, %d %B %Y %H:%M:%S")

    def notif_stop(self):
        Notify.init("Work Controller")
        summary = "Work Control Stopped :("
        body = "Computer will not auto screen lock"
        app_notification = Notify.Notification.new(summary, str(body), 'appointment-missed-symbolic')
        app_notification.show()

    def notif_start(self):
        Notify.init("Work Controller")
        summary = "Work Control Starting..."
        # body = "Computer will sleep at "+str(self.convert_date(datetime.now()+timedelta(seconds=delay)))
        body = "Computer sleep in\n"+self.diff_time(datetime.now(), datetime.now()+timedelta(seconds=delay))
        body += "\nat "+str(self.convert_date(datetime.now()+timedelta(seconds=delay)))
        app_notification = Notify.Notification.new(summary, str(body), 'alarm-symbolic')
        app_notification.show()

class Mesin:
    delay = 1200
    remain = delay
    def __init__(self):
        self.delay = 1200
        self.remain = self.delay
        self.action = "Lock"
        global delay
        delay = self.delay
        self.thread = 0
        self.is_running = False
        self.mainloop = gobject.MainLoop()
        self.util = Utility()

    def screen_lock(self):
        call(["gnome-screensaver-command", "-l"])

    def sleep(self):
        call(["systemctl", "suspend"])

    def stop(self):
        if self.is_running:
            self.util.notif_stop()
            self.thread.cancel()
            self.mainloop.quit()
            self.is_running = False
            print bcolors.OKGREEN+"["+str(datetime.now())+"]"+bcolors.ENDC, bcolors.FAIL+"Work Controller Stopped :("+bcolors.ENDC

    def start(self):
        print 'start'
        if not self.is_running:
            self.util.notif_start()
            print bcolors.OKGREEN+"["+str(datetime.now())+"]"+bcolors.ENDC, bcolors.WARNING+self.action+" after", delay, "seconds"+bcolors.ENDC
            if self.action == "Lock":
                self.thread = threading.Timer(delay, self.screen_lock)
            elif self.action == "Sleep":
                self.thread = threading.Timer(delay, self.sleep)
            self.thread.start()
            self.is_running = True

    def filter_cb(self, bus, message):
        if message.get_member() != "ActiveChanged":
            return
        args = message.get_args_list()
        if args[0] == True:
            self.is_running = False
            print bcolors.OKGREEN+"["+str(datetime.now())+"]"+bcolors.ENDC, bcolors.HEADER+"Screen Locked"+bcolors.ENDC
        else:
            self.start()

    def listen_lockscreen(self):
        DBusGMainLoop(set_as_default=True)
        bus = dbus.SessionBus()
        bus.add_match_string("type='signal',interface='org.gnome.ScreenSaver'")
        bus.add_message_filter(self.filter_cb)
        gobject.idle_add(self.start, priority=999)
        print self.remain
        self.remain -= 1
        thread = threading.Timer(1, self.listen_lockscreen)
        thread.start
        # self.mainloop.quit()
        # self.mainloop.run()

    def main(self):
        self.listen_lockscreen()


# Standard boilerplate to call the main() function to begin
# the program.
if __name__ == '__main__':
    if len(sys.argv) >= 1:
        try:
            signal.signal(signal.SIGINT, signal.SIG_DFL)
            main = Mesin()
            main.main()
            global delay
            if sys.argv[1].isdigit():
                delay = int(sys.argv[1])
                if sys.argv[2] == "--sleep":
                    main.action = "Sleep"
                elif sys.argv[2] == "--lock":
                    main.action = "Lock"
            elif sys.argv[2].isdigit():
                delay = int(sys.argv[2])
                if sys.argv[1] == "--sleep":
                    main.action = "Sleep"
                elif sys.argv[1] == "--lock":
                    main.action = "Lock"
            # self.listen_lockscreen()
        except Exception as e:
            print "Usage :"
            print "       python "+sys.argv[0]+" <seconds> [--sleep|--lock]"
            sys.exit()
        finally:
            sys.exit()
