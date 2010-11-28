"""
Your local configuration of TOMUSS goes here.

You can redefine any method, function or variable in the other module.

This file contains the most important configuration options
that can't be modified interactively in the configuration table.
"""

import configuration

# Define a super user login list before activating the authentication
# So you will be able to edit configuration table.
configuration.root = ("super.user",)


# How to authenticate users
configuration.cas = "https://cas.domain.org/cas"


# List of 'suivi' servers to launch.
import servers
import socket
import time

configuration.suivi = servers.Suivi()
configuration.suivi.add(time.localtime()[0], 'Printemps',
                        socket.getfqdn() + ':%d', 8889)
configuration.suivi.add(time.localtime()[0], 'Automne',
                        socket.getfqdn() + ':%d', 8890)
