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
__version__ = (1, 0, 3)

def run_from_cmdline():
    import logging
    from optparse import OptionParser
    from notifier import TeamspeakNotifier
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
