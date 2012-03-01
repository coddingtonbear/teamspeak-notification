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
__author__ = 'Adam Coddington <me@adamcoddington.net>'
__version__ = (1, 0, 2)

import logging
from optparse import OptionParser
import re
import time
from subprocess import Popen, PIPE

import pynotify
import teamspeak3

class TeamspeakNotifier(object):
    CHECK_INTERVAL = 0.25
    RECONNECT_INTERVAL = 1
    TEAMSPEAK_TITLE = "TeamSpeak 3"
    DEFAULT_NAME = "Somebody"

    def __init__(self):
        super(TeamspeakNotifier, self).__init__()
        self.logger = logging.getLogger('TeamspeakNotifier')

        pynotify.init('TeamspeakNotifier')
        self.notification = pynotify.Notification(
            "Starting",
            "TeamspeakNotifier is attempting to find your instance of Teamspeak."
            )
        self.notification.show()
        self.connect()

        self.clients = {}
        self.identity = None

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

    def _update_notification(self, title, message = ''):
        self.logger.debug("Posting Notification: [%s]%s" % (
                    title,
                    message,
                )
            )
        self.notification.update(title, message)
        self.notification.show()

    def notify(self, message):
        if message.ultimate_origination == 'notifytextmessage':
            if not self.teamspeak_is_active() and not self.message_is_mine(message):
                self._update_notification("%s said" % message['invokername'], message['msg'])
        elif message.ultimate_origination == 'notifytalkstatuschange':
            if not self.teamspeak_is_active() and not self.message_is_mine(message):
                if message['status'] == '1':
                    self._update_notification(
                                "%s is talking..." % 
                                self.get_name_for_message(message)
                            )
        elif message.ultimate_origination in ('notifyclientmoved', 'notifyclientleftview', 'notifycliententerview', ):
            self.send_client_update_commands()
        elif message.ultimate_origination == 'clientlist':
            self.update_client_list(message)
        elif message.ultimate_origination == 'whoami':
            self.update_identity(message)
        elif message.ultimate_origination == 'notifyconnectstatuschange':
            self._update_notification(
                                message['status'].title(),
                                "Your connection to Teamspeak is now %s." % message['status']
                            )

    def send_client_update_commands(self):
        self.api.send_command(
                    teamspeak3.Command('clientlist')
                )
        self.api.send_command(
                    teamspeak3.Command('whoami')
                )

    def update_identity(self, message):
        self.identity = message['clid']
        self.logger.info("Updated identity: %s" % self.identity)

    def update_client_list(self, message):
        self.clients = {}
        if not hasattr(message, 'responses'):
            responses = [message]
        else:
            responses = message.responses
        for client_info in responses:
            self.clients[client_info['clid']] = client_info['client_nickname']
        self.logger.info("Updated client list: %s" % self.clients)

    def message_is_mine(self, message):
        return message['clid'] == self.identity

    def get_name_for_message(self, message):
        try:
            return self.clients[message['clid']]
        except KeyError:
            return self.DEFAULT_NAME

    def teamspeak_is_active(self):
        return self.get_active_window_title() == self.TEAMSPEAK_TITLE

    def main(self):
        while True:
            try:
                messages = self.api.get_messages()
                for message in messages:
                    self.notify(message)
            except (teamspeak3.TeamspeakConnectionLost, EOFError, ) as e:
                self._update_notification("Teamspeak is Unavailable", "Teamspeak does not appear to be running.")
                self.logger.warning("Connection lost.")
                self.connect()
            time.sleep(self.CHECK_INTERVAL)

    def connect(self):
        while True:
            try:
                self.logger.info("Attempting to connect.")
                self.api = teamspeak3.Client()
                self.api.subscribe()
                self.logger.info("Connection established.")
                self._update_notification(
                        "Ready", 
                        "Teamspeak is now listening for messages."
                    )
                self.send_client_update_commands()
                return True
            except Exception as e:
                self.logger.exception(e)
                pass
            time.sleep(self.RECONNECT_INTERVAL)

def run_from_cmdline():
    parser = OptionParser()
    parser.add_option('-d', '--debug', dest='debug', default=False, action='store_true')
    parser.add_option('-i', '--info', dest='info', default=False, action='store_true')
    parser.add_option('-l', '--logfile', dest='logfile', default=False)
    options, args = parser.parse_args()
    kwargs = {}
    kwargs['level'] = logging.CRITICAL
    if options.debug:
        kwargs['level'] = logging.DEBUG
    if options.info:
        kwargs['level'] = logging.INFO
    if options.logfile:
        kwargs['filename'] = logging.logfile
    logging.basicConfig(**kwargs)
    app = TeamspeakNotifier()
    app.main()

def get_version():
    return '.'.join(str(bit) for bit in __version__)
