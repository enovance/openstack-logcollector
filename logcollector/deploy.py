# Copyright (C) 2013 eNovance SAS <licensing@enovance.com>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import argparse
import glob
from subprocess import Popen, PIPE
import sys
import os


class HostAgent(object):

    def __init__(self):
        self.callback_url = None
        self.host_id = None

    def execCmd(self, command):
        p = Popen(command, stdin=PIPE, stdout=PIPE,
                  stderr=PIPE, close_fds=True)
        (stdout, stderr) = p.communicate()
        rc = p.returncode
        return (rc, stdout, stderr)

    def callback(self, file=None, error=None):
        pass

    def copy_locally(self, file_path, local_store):
        pass

    def find_file(self, filename, task=None):
        if task:
            filename = '/tmp/sosreport*%s' % task
        path = glob.glob('%s*' % filename)
        return path

    def daemonize(self):
        try:
            pid = os.fork()
            if pid > 0:
                # Exit parent process
                sys.exit(0)
        except OSError, e:
            err = "Failed to fork: %d (%s)" % (e.errno, e.strerror)
            self.callback(error=err)
            sys.exit(1)

    def main(self, args=None, filename=None):
        parser = argparse.ArgumentParser()
        parser.add_argument('--command',
            help='Command to start the log collectoin process.')
        parser.add_argument('--callback_url',
            help='URL of the controller to communicate comletion.')
        parser.add_argument('--filename',
            help='Filename for the logs archive.')
        parser.add_argument('--host_id',
            help='ID of the host.')
        (options, args) = parser.parse_known_args(sys.argv[1:])
        self.callback_url = args.callback_url
        self.host_id = args.host_id

        if args.callback_url:
            self.daemonize()

            rc, out, err = self.execCmd(args.command.split())
            if rc != 0:
                self.callback(error=err)
            else:
                filePath = self.find_file(args.filename)
                self.callback(file=filePath)
        else:
            cmd_args = args if args else args.command.split()
            return self.execCmd(cmd_args)

if __name__ == "__main__":
    HostAgent().main()
