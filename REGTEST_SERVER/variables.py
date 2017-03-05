
from .. import utilities
from .. import plugin
from . import tests_config

V = utilities.Variables(tests_config.vars)

def get_var(server):
    server.the_file.write(repr(getattr(V, server.something)))

plugin.Plugin('get_var', '/get_var/{?}',
              documentation="Variable Regtest",
              function=get_var, authenticated=False
              )
