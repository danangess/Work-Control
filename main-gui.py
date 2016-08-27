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
# import signal
import sys
import dbus
from subprocess import call
import pygtk
import gi
gi.require_version('Notify', '0.7')
from gi.repository import Notify
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
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
        summary = "Work Control Stopped :("
        body = "Computer will not auto screen lock"
        app_notification = Notify.Notification.new(summary, str(body), 'appointment-missed-symbolic')
        app_notification.show()

    def notif_start(self):
        summary = "Work Control Starting..."
        # body = "Computer will sleep at "+str(self.convert_date(datetime.now()+timedelta(seconds=delay)))
        body = "Computer sleep in\n"+self.diff_time(datetime.now(), datetime.now()+timedelta(seconds=delay))
        body += "\nat "+str(self.convert_date(datetime.now()+timedelta(seconds=delay)))
        app_notification = Notify.Notification.new(summary, str(body), 'alarm-symbolic')
        app_notification.show()

class Mesin:
    def __init__(self):
        self.delay = 1200
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

        hello.jeda = delay
        hello.set_button()
        hello.set_entry()

    def start(self):
        if not self.is_running:
            self.util.notif_start()
            print bcolors.OKGREEN+"["+str(datetime.now())+"]"+bcolors.ENDC, bcolors.WARNING+self.action+" after", delay, "seconds"+bcolors.ENDC
            if self.action == "Lock":
                self.thread = threading.Timer(delay, self.screen_lock)
            elif self.action == "Sleep":
                self.thread = threading.Timer(delay, self.sleep)
            self.thread.start()
            self.is_running = True

        hello.jeda = delay
        hello.set_button()
        hello.set_entry()

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
        self.mainloop.run()

    def main(self, jeda):
        try:
            Notify.init("Work Controller")
            global delay
            delay = int(jeda)
            self.listen_lockscreen()
        except Exception as e:
            print "Invalid command"
            print e
            sys.exit(1)
        finally:
            sys.exit(1)

class Exit(Gtk.Dialog):
    def __init__(self, parent):
        Gtk.Dialog.__init__(self, "Stop -> Exit?", parent, 0,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            "Hide", Gtk.ResponseType.CLOSE,
             Gtk.STOCK_OK, Gtk.ResponseType.OK))

        self.set_default_size(150, 60)

        label = Gtk.Label("Work Control is running\nExit?")

        box = self.get_content_area()
        box.add(label)
        self.show_all()

class tooSmall(Gtk.Dialog):
    def __init__(self, parent):
        Gtk.Dialog.__init__(self, "Warning!", parent, 0,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OK, Gtk.ResponseType.OK))

        self.set_default_size(150, 60)

        label = Gtk.Label("Time is to small\nContinue?")

        box = self.get_content_area()
        box.add(label)
        self.show_all()

class Main(Gtk.Window):
    def __init__(self):
        self.jeda = 1200
        self.msn = Mesin()
        self.util = Utility()

        # create a new window
        Gtk.Window.__init__(self, title="Work Controller")
        # self.window = Gtk.Window()
        self.set_default_size(75, 150)
        self.set_size_request(75, 100)
        self.set_border_width(10)
        self.set_resizable(False)
        self.connect("delete_event", self.delete_event)

        self.vbox = Gtk.VBox(False, 0)
        self.add(self.vbox)

        self.entry = Gtk.Entry()
        self.entry.set_max_length(5)
        self.entry.set_alignment(1)
        self.entry.set_width_chars(10)
        self.entry.connect("activate", self.start, self.entry)
        self.entry.connect_object("activate", Gtk.Widget.destroy, self)
        self.entry.insert_text("1200", len(self.entry.get_text()))
        self.entry.select_region(0, len(self.entry.get_text()))

        self.label = Gtk.Label()
        self.label.set_width_chars(10)
        self.label.set_label(" seconds")

        self.hbox = Gtk.HBox(False, 0)
        self.vbox.add(self.hbox)

        self.hbox.pack_start(self.entry, True, True, 0)
        self.hbox.pack_start(self.label, True, True, 0)

        self.radio_sleep = Gtk.RadioButton("Sleep")
        self.radio_sleep.connect("toggled", self.radio_toggled, "sleep")
        self.radio_lock = Gtk.RadioButton(group=self.radio_sleep, label="Lock Screen")
        self.radio_lock.connect("toggled", self.radio_toggled, "lock")
        self.radio_lock.set_active(True)
        self.vbox.pack_start(self.radio_sleep, True, True, 0)
        self.vbox.pack_start(self.radio_lock, True, True, 0)

        self.button = Gtk.Button("Start")
        self.button.connect("clicked", self.start, self.entry)
        self.button.connect_object("clicked", Gtk.Widget.destroy, self)
        self.vbox.pack_start(self.button, True, True, 0)
        self.button.CAN_DEFAULT = True

    def radio_toggled(self, widget, data=None):
        # print "%s was toggled %s" % (data, ("OFF", "ON")[widget.get_active()])
        if data == "sleep" and widget.get_active():
            self.msn.action = "Sleep"
        elif data == "lock" and widget.get_active():
            self.msn.action = "Lock"

    def start(self, widget, entry):
        if self.button.get_label() == "Stop":
            self.stop(widget)
        elif self.button.get_label() == "Start":
            ent = entry.get_text()
            if ent.isdigit():
                ent = int(entry.get_text())
                if ent > 60:
                    self.jeda = ent
                    self.msn.main(ent)
                else:
                    dialog = tooSmall(self)
                    response = dialog.run()
                    dialog.destroy()
                    if response == Gtk.ResponseType.OK:
                        self.jeda = ent
                        self.msn.main(ent)
                    elif response == Gtk.ResponseType.CANCEL:
                        Gtk.main_quit()
                        self.set_entry()
                        Gtk.main()
            else:
                dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, "Mistake")
                dialog.format_secondary_text("The input must be a number in seconds")
                dialog.run()
                dialog.destroy()
                Gtk.main_quit()
                Gtk.main()

    def stop(self, widget):
        self.msn.stop()
        Gtk.main_quit()
        Gtk.main()

    def set_button(self):
        if self.msn.is_running:
            self.button.set_label("Stop")
        else:
            self.button.set_label("Start")

    def set_entry(self):
        if self.msn.is_running:
            self.entry.set_property("editable", False)
            self.entry.hide()
            self.set_label()
        else:
            self.entry.set_property("editable", True)
            self.entry.set_text(str(self.jeda))
            self.entry.select_region(0, len(self.entry.get_text()))
            self.entry.grab_focus()
            self.entry.show()
            self.set_label()

    def set_label(self):
        thread = threading.Timer(1, self.set_label)
        if self.msn.is_running:
            self.jeda = self.jeda - 1
            thread.start()
            label = self.util.diff_time(datetime.now(), datetime.now()+timedelta(seconds=self.jeda+1))
            self.label.set_label(str(label))
            self.label.set_width_chars(38)
        else:
            thread.cancel()
            self.label.set_width_chars(10)
            self.label.set_label(' seconds')

    def delete_event(self, widget, event, data=None):
        if self.msn.is_running:
            dialog = Exit(self)
            response = dialog.run()
            dialog.destroy()
            if response == Gtk.ResponseType.OK:
                self.destroy(widget)
                return False
            elif response == Gtk.ResponseType.CANCEL:
                return True
            elif response == Gtk.ResponseType.CLOSE:
                # self.hide() #run on background
                self.iconify() #minimize
                return True
        else:
            self.destroy(widget, data)
            return False

    def destroy(self, widget, data=None):
        self.msn.stop()
        Gtk.main_quit()

    def main(self):
        self.show_all()
        Gtk.main()

# If the program is run directly or passed as an argument to the python
# interpreter then create a HelloWorld instance and show it
if __name__ == "__main__":
    hello = Main()
    hello.main()
