#
#   Copyright (c) 2013-2014, Scott J Maddox
#
#   This file is part of SimplePL.
#
#   SimplePL is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   SimplePL is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public
#   License along with SimplePL.  If not, see
#   <http://www.gnu.org/licenses/>.
#
#######################################################################

# std lib imports
import logging
log = logging.getLogger(__name__)
import multiprocessing
from multiprocessing import Process, Queue
from Queue import Empty
import time
import signal
from collections import OrderedDict

# third party libraries
from PySide import QtCore


class Response(object):
    def __init__(self, command, result):
        self.uuid = command.uuid
        self.name = command.name
        self.result = result


_lastUuid = 0


class Command(object):

    def __init__(self, name, args, kwargs,
                 has_callback=False,
                 persistent=False,
                 uuid=None):
        #self.uuid = uuid.uuid4()
        if uuid is None:
            global _lastUuid
            self.uuid = _lastUuid + 1
            _lastUuid = self.uuid
        else:
            self.uuid = uuid
        self.name = name
        self.args = args
        self.kwargs = kwargs
        self.has_callback = has_callback
        self.persistent = persistent

    def respond(self, result):
        return Response(self, result)


class ConnectedBase(object):
    def __init__(self, max_update_rate=100):
        '''
        parent : ConnectedBase
        '''
        super(ConnectedBase, self).__init__()
        self._max_update_rate = max_update_rate
        self._recvQueue = Queue()
        self._sendQueue = None

        self._wants_quit = False
        self._dispatch_queue = OrderedDict()
        self._commands = {}  # keys are command names, values are functions
        self._callbacks = {}  # keys are uuid's, values are functions
        self._persistentCallbacks = {}  # keys are uuid's, values are functions
        self._invalid_commands = []

    def getRecvQueue(self):
        return self._recvQueue

    def setSendQueue(self, q):
        if self._sendQueue is not None:
            raise ValueError('The send queue is already set.')
        else:
            self._sendQueue = q

    # Private Methods

    def _loop(self):
        # Flush the recvQueue into the dispatch queue
        while True:
            try:
                o = self._recvQueue.get_nowait()
            except Empty:
                break
            log.debug('{}: something in queue'.format(type(self).__name__))
            self._dispatch_queue[o.uuid] = o
        self._dispatch()
        self.update()

    def _dispatch(self):
        if not len(self._dispatch_queue):
            return False
        log.debug('{}: _dispatch'.format(type(self).__name__))

        # get the object
        _uuid, o = self._dispatch_queue.popitem(last=False)

        # check if it is a command or response, and act accordingly
        if isinstance(o, Command):
            self._dispatch_command(o)
        elif isinstance(o, Response):
            self._dispatch_reponse(o)
        else:
            raise TypeError('This queue should only be used to send '
                            'Command and Response objects.')

        return True

    def _dispatch_command(self, command):
        # Make sure the command is a valid, registered command
        if command.name not in self._commands:
            log.debug('{}: Invalid command "{}", id={}'.format(
                                                        type(self).__name__,
                                                        command.name,
                                                        command.uuid))
            self._invalid_commands.append(command)
            return

        log.debug('{}: Dispatching command "{}", id={}'.format(
                                                        type(self).__name__,
                                                        command.name,
                                                        command.uuid))
        # Dispatch the command, and keep the result
        if command.args is None and command.kwargs is None:
            result = self._commands[command.name].__call__()
        elif command.kwargs is None:
            result = self._commands[command.name].__call__(*command.args)
        elif command.args is None:
            result = self._commands[command.name].__call__(**command.kwargs)
        else:
            result = self._commands[command.name].__call__(*command.args,
                                                           **command.kwargs)
        # If a result is requested,
        # create a Response object and send it
        if command.has_callback:
            log.debug('{}: sending response "{}", id={}'.format(
                                                        type(self).__name__,
                                                        command.name,
                                                        command.uuid))
            response = command.respond(result)
            self._sendQueue.put(response)
            log.debug('{}: sent response "{}", id={}'.format(
                                                        type(self).__name__,
                                                        command.name,
                                                        command.uuid))

    def _dispatch_reponse(self, response):
        log.debug('{}: Dispatching response "{}", id={}'.format(
                                                        type(self).__name__,
                                                        response.name,
                                                        response.uuid))
        if response.uuid in self._callbacks:
            self._callbacks.pop(response.uuid).__call__(response.result)
        elif response.uuid in self._persistentCallbacks:
            self._persistentCallbacks[response.uuid].__call__(response.result)
        else:
            raise RuntimeError('No callback registered with uuid '
                               '{}'.format(response.uuid))

    def _register_callback(self, uuid, callback, persistent=False):
        '''
        If the uuid already has a callback registered, it's overwritten.
        '''
        if persistent:
            self._persistentCallbacks[uuid] = callback
        else:
            self._callbacks[uuid] = callback

    def _deregister_callback(self, uuid):
        if uuid in self._callbacks:
            del self._callbacks[uuid]
        elif uuid in self._persistentCallbacks:
            del self._persistentCallbacks[uuid]
        else:
            raise ValueError('No callback registered for command uuid '
                             '{}'.format(uuid))

    # Public Methods
    def send_command(self, name, args=None, kwargs=None,
                     callback=None,
                     persistent=False,
                     uuid=None):
        '''Sends a command through the queue, to the other process'''
        if self._sendQueue is None:
            raise ValueError('The send queue must first be set '
                             'with setSendQueue')
        if callback is None:
            command = Command(name, args, kwargs,
                              has_callback=False,
                              persistent=persistent,
                              uuid=uuid)
        else:
            command = Command(name, args, kwargs,
                              has_callback=True,
                              persistent=persistent,
                              uuid=uuid)
            self._register_callback(command.uuid, callback, persistent)
        log.debug('{}: Sending command "{}", id={}'.format(
                                                        type(self).__name__,
                                                        command.name,
                                                        command.uuid))
        self._sendQueue.put(command)

    def register_command(self, name, func):
        '''Registers a command for the other process to call'''
        if name in self._commands:
            raise ValueError('Command "{}" already exists'.format(name))
        else:
            self._commands[name] = func

    def deregister_command(self, name):
        '''Deregisters a command, so the other process cannot call it'''
        if name not in self._commands:
            raise ValueError('Command "{}" does not exist'.format(name))
        else:
            del self._commands[name]

    def command_registered(self, name):
        '''
        Returns True if the specified command name is registered, or False
        if it is not.
        '''
        return (name in self._commands)

    def init(self):
        '''
        Called once, before starting the loop.
        This is a good method for subclasses to override.
        The default implementation does nothing.
        '''
        pass

    def update(self):
        '''
        Called once per loop, after dispatching all commands in the queue.
        This is a good method for subclasses to override.
        The default implementation does nothing.
        '''
        pass


class ConnectedProcess(Process, ConnectedBase):
    '''
    A process that receives commands from the parent process, and can
    respond assynchronously with the results.
    '''
    def __init__(self, max_update_rate=100, group=None, target=None,
                 name=None, *args, **kwargs):
        '''
        Parameters
        ----------
        max_update_rate : int or float (default: 100)
            the maximum number of calls to ConnectedProcess.update per second
        '''
        if 'debug' in kwargs:
            self.debug = kwargs.pop('debug')
        else:
            self.debug = False
        ConnectedBase.__init__(self, max_update_rate)
        Process.__init__(self, group, target, name, *args, **kwargs)

    def run(self):
        if self.debug:
            logger = multiprocessing.log_to_stderr()
            logger.setLevel(multiprocessing.SUBDEBUG)
            #logging.basicConfig(level=logging.DEBUG)
        self.init()
        self._time = time.time()
        while not self._wants_quit:
            self._loop()

            # Sleep if update was too fast
            t2 = time.time()
            if t2 - self._time < 1. / self._max_update_rate:
                time.sleep(1. / self._max_update_rate - (t2 - self._time))
            self._time = t2

    def init(self):
        '''
        Called once, before starting the loop.
        This is a good method for subclasses to override.
        The default implementation connects signal.SIGINT to
        ConnectedProcess.handle_SIGINT, signal.SIGTERM to
        ConnectedProcess.handle_SIGTERM, and registers the `quit` command.
        '''
        # register the quit command
        self.register_command('quit', self.quit)
        # register handlers to catch Ctrl+C and SIGTERM
        signal.signal(signal.SIGINT, self.handle_SIGINT)
        signal.signal(signal.SIGTERM, self.handle_SIGTERM)

    def handle_SIGINT(self, signum, frame):
        log.debug('{}: SIGINT received'.format(type(self).__name__))
        self.quit()

    def handle_SIGTERM(self, signum, frame):
        log.debug('{}: SIGTERM received'.format(type(self).__name__))
        self.quit()

    # Commands
    def quit(self):
        log.debug('{}: quit called'.format(type(self).__name__))
        self._wants_quit = True


class ConnectedQObject(QtCore.QObject, ConnectedBase):
    '''
    Provides the Qt GUI with an interface to the connected process.
    '''
    def __init__(self, process, max_update_rate=100, parent=None):
        self.process = process
        ConnectedBase.__init__(self, max_update_rate)
        QtCore.QObject.__init__(self, parent)

        # connect the queue's
        process.setSendQueue(self.getRecvQueue())
        self.setSendQueue(process.getRecvQueue())

        # Register commands, etc.
        self.init()

        # Set up the first call to _loop, which calls _dispatch and update
        QtCore.QTimer.singleShot(1000. / self._max_update_rate, self._loop)

    def update(self):
        # Set up the next call to _loop, which calls _dispatch and update
        QtCore.QTimer.singleShot(1000. / self._max_update_rate, self._loop)

    def start(self):
        '''Start the connected process'''
        self.process.start()

    def quit(self):
        '''Tell the connected process to quit'''
        self.send_command('quit')

    def join(self):
        '''Join the connected process'''
        self.process.join()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    app = QtCore.QCoreApplication([])
    proc = ConnectedProcess(debug=True)
    obj = ConnectedQObject(proc)
    obj.start()
    def quit():
        obj.quit()
        app.quit()
    QtCore.QTimer.singleShot(2000, quit)
    app.exec_()
    print 'Done.'
