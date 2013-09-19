"""
Your local configuration of TOMUSS goes here.

You can redefine any method, function or variable in the other modules.

This file contains the most important configuration options
that can't be modified interactively in the configuration table.
"""

from .. import configuration

# Define a super user login list before activating the authentication
# So you will be able to edit configuration table.
configuration.root = ("super.user",)


# How to authenticate users with a CAS provider
configuration.cas = "https://cas.domain.org/cas"

# True to use OpenID
if False:
    # The identity is the mail address
    # Modify the ACLS table to give the right to connect to users
    # (for roots users, do it before switching to OpenID)

    # Google
    configuration.cas = 'https://www.google.com/accounts/o8/id'
    # Yahoo
    configuration.cas = 'https://me.yahoo.com'
    configuration.Authenticator = configuration.authenticators.OpenID

# To see how to modify the student lists and other values: see regtestpatch.py
        

# List of 'suivi' servers to launch.
from .. import servers
import socket
import time

configuration.suivi = servers.Suivi(https=False)

# Add a server for each semester of the current year.
# You must redefine this to enumerate the semester in use.
for i, semester in enumerate(configuration.semesters):
    configuration.suivi.add(
        time.localtime()[0],      # The current Year
        semester,                 # A semester
        socket.getfqdn() + ':%d', # The user visible URL for the 'suivi' server
        8889 + i)                 # The socket port number of the server

