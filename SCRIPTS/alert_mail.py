#!/usr/bin/python3
"""
Send a mail to the TOMUSS maintainer :

     SCRIPTS/alert_mail.py "mail_subject" "mail_content"
"""

import sys
import tomuss_init
tomuss_init.terminate_init()
from .. import utilities
from .. import configuration

utilities.send_mail(configuration.maintainer, sys.argv[1], sys.argv[2])
