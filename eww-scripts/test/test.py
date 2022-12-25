import os

filename = '~/.cache'


print(os.path.expandvars(os.path.expanduser(filename)))