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


def prepare(ticketNum=None, customer=None, tmpDir=None, task=None):

    command = 'sosreport -e openstack'
    if ticketNum:
        ticket = ' --ticket-number=%s' % ticketNum
        command += ticket
    if customer or task:
        if customer and task:
            entry = '%s_%s' % (customer and task)
        else:
            entry = customer if customer else task
        custName = ' --name=%s' % entry
        command += custName
    if tmpDir:
        tmpdir = ' --tmp-dir=%s' % tmpDir
        command += tmpDir
    return command


def prepareLocal(ticketNum=None, customer=None, tmpDir=None, task=None):

    command = ['sosreport', '-e', 'openstack']
    if ticketNum:
        ticket = '--ticket-number=%s' % ticketNum
        command.append(ticket)
    if customer or task:
        if customer and task:
            entry = '%s_%s' % (customer and task)
        else:
            entry = customer if customer else task
        custName = '--name=%s' % entry
        command.append(custName)
    if tmpDir:
        tmpdir = '--tmp-dir=%s' % tmpDir
        command.append(tmpDir)
    return command
