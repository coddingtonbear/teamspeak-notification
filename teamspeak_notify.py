#!/usr/bin/python
#
# Copyright (c) 2012 Adam Coddington
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
import re
import time
from subprocess import Popen, PIPE

import pynotify
import teamspeak3

class TeamspeakNotifier(object):
    CHECK_INTERVAL = 0.25
    RECONNECT_INTERVAL = 5
    TEAMSPEAK_TITLE = "TeamSpeak 3"

    def __init__(self):
        super(TeamspeakNotifier, self).__init__()
        pynotify.init('TeamspeakNotifier')
        self.notification = pynotify.Notification(
            "Ready", 
            "TeamSpeak Notifier is listening for messages."
            )
        self.notification.show()
        self.connect()

    def get_active_window_title(self):
        root = Popen(['xprop', '-root', '_NET_ACTIVE_WINDOW'], stdout=PIPE)

        for line in root.stdout:
            m = re.search('^_NET_ACTIVE_WINDOW.* ([\w]+)$', line)
            if m != None:
                id_ = m.group(1)
                id_w = Popen(['xprop', '-id', id_, 'WM_NAME'], stdout=PIPE)
                break

        if id_w != None:
            for line in id_w.stdout:
                match = re.match("WM_NAME\(\w+\) = (?P<name>.+)$", line)
                if match != None:
                    return match.group("name")[1:-1]

    def notify(self, message):
        if message.command == 'notifytextmessage':
            self.notification.update("%s said" % message['invokername'], message['msg'])
            self.notification.show()
        elif message.command == 'notifytalkstatuschange' and message['status'] == '1':
            self.notification.update("Somebody is talking...")
            self.notification.show()

    def main(self):
        while True:
            try:
                messages = self.api.get_messages()
                for message in messages:
                    if self.get_active_window_title() != self.TEAMSPEAK_TITLE:
                        self.notify(message)
            except EOFError:
                self.connect()
            time.sleep(self.CHECK_INTERVAL)

    def connect(self):
        while True:
            try:
                self.api = teamspeak3.Client()
                self.api.subscribe()
                return True
            except Exception as e:
                pass
            time.sleep(self.RECONNECT_INTERVAL)

if __name__ == '__main__':
    app = TeamspeakNotifier()
    app.main()
    
