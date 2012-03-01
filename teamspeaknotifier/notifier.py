import logging
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
    TARGETMODE_CLIENT = '1'
    TARGETMODE_CHANNEL = '2'
    TARGETMODE_SERVER = '3'

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
                if message['targetmode'] == self.TARGETMODE_CLIENT:
                    title = "%s said (in private message)" % (message['invokername'], )
                else:
                    title = "%s said" % (message['invokername'], )
                self._update_notification(title, message['msg'])
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
        try:
            if 'clid' in message.keys():
                return message['clid'] == self.identity
            elif 'invokerid' in message.keys():
                return message['invokerid'] == self.identity
            elif 'invokername' in message.keys():
                return self.clients[self.identity] == message['invokername']
        except KeyError:
            pass
        return False

    def get_name_for_message(self, message):
        try:
            if 'clid' in message.keys():
                return self.clients[message['clid']]
            elif 'invokerid' in message.keys():
                return self.clients[message['invokerid']]
            elif 'invokername' in message.keys():
                return message['invokername']
        except KeyError:
            pass
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


