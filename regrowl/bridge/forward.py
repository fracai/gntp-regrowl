"""
Forwards a notification or registration to another machine

Pulls destinations from the .regrowl config in the
[regrowl.bridge.forward.destinations] section. Each machine
should have its own line with the following format:
machinename = <hostname>,<port>,<password>

Currently forwards all packets that come in to the destinations
in the configuration.
"""

from __future__ import absolute_import

import logging
import gntp.notifier
import gntp.core
import ConfigParser

from regrowl.regrowler import ReGrowler
from regrowl.cli import CONFIG_PATH

logger = logging.getLogger(__name__)

__all__ = ['GrowlForwarder']


class GrowlForwarder(ReGrowler):
    key = __name__
    valid = ['REGISTER', 'NOTIFY', 'SUBSCRIBE']

    def forwardpacket(self, packet):
        destinations = self.load_destinations()
        for destination in destinations:
            logger.info("Forwarding packet to " + destination[0] + ":" + destination[1] + "...")
            notifier = gntp.notifier.GrowlNotifier(hostname = destination[0], port = int(destination[1]), password = destination[2])
            if destination[2]:
                packet.set_password(destination[2],'MD5')
            notifier._send(packet.info['messagetype'],packet)

    def load_destinations(self):
        parser = ConfigParser.ConfigParser()
        parser.read('/'.join(CONFIG_PATH)) #[TODO] this is not portable
        conf_destinations = parser.items("regrowl.bridge.forward.destinations")
        destinations = []
        for destination, options in conf_destinations:
            destinations.append(options.split(','))
        return destinations

    def instance(self, packet):
        return None

    def register(self, packet):
        logger.info('Register')
        self.forwardpacket(packet)

    def notify(self, packet):
        logger.info('Notify')
        self.forwardpacket(packet)

    def subscribe(self, packet):
        logger.info('Subscribe')
        self.forwardpacket(packet)
