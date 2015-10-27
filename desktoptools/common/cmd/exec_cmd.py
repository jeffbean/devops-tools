# encoding: utf-8

import logging

import subprocess
import time
import threading
import io


class ExecCommandTimeoutError(Exception):
    """ Timeout exception occurs when an Exec command exceeds timeout.
    """

    def __init__(self, value):
        Exception.__init__(self)
        self.parameter = value

    def __str__(self):
        return repr(self.parameter)


class Exec(object):
    """  Executes a command and stores information about the command and it's results 
    """

    def __init__(self, cmd, cmd_info=None, timeout=60):
        """ Create a new Exec object.
        :param cmd:       Command to execute.
        :keyword cmd_info: Dict containing meta-information relevant to the command.
                          Example: Node on which the command is executed.
        :keyword timeout: Maximum time command allowed to run in seconds.
                          note that passing in a timeout of 0 removes all timeout logic.
        """
        self.cstdout = io.StringIO()
        self.cstderr = io.StringIO()
        self.cstatus = -1  # Current GrinderStatus  -1 if not run or timeout
        self.cmd = cmd
        self.cmdInfo = cmd_info
        self.timeo = int(timeout)
        self.pid = None
        self.start = -1
        self.elapsed = -1
        self.timeoutError = False

    def get_pid(self):
        """ Method to get PID
        """
        return self.pid

    def get_stdout(self):
        """ Get stdout as a string 
        """
        return self.cstdout.getvalue().rstrip('\n')

    def get_stderr(self):
        """ Get stderr as a string 
        """
        return self.cstderr.getvalue().rstrip('\n')

    def get_status(self):
        """ Get the current status.  This is normally an integer, however in some rare
            cases it is None.  What should a None mean to the caller?
        """
        return self.cstatus

    def get_command(self):
        """ The original cmd string which was passed in 
        """
        return self.cmd

    def get_command_info(self):
        """ Dict of meta-information passed in with the command. None if no meta
            information was provided.
        """
        return self.cmdInfo

    def get_elapsed(self):
        """ Amount of time it took to run the command.  Result will be -1 if the command
            hasn't been run yet.
        """
        return self.elapsed

    def is_timeout(self):
        """ Whether this command finished successfully or timed out. 
        """
        return self.timeoutError

    @staticmethod
    def _process_exit(status):
        """ Process the exit code.
        @param status - The status code to process 
        """
        if status != 0:
            if status & 255:
                # Signal killed us; so return the raw signal
                return status
            else:
                # Exited in normal bad-shell fashion, so shift.
                return status >> 8
        return status

    def run(self):
        """ Perform the actual execution of the target command from self.
            May throw a ExecCommandTimeoutError if execution time exceeds the timeout
        """
        self.child = None
        try:
            self._set_start()
            timer = threading.Timer(self.timeo, self._timeout)
            self.child = subprocess.Popen(self.cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                          shell=True, universal_newlines=True)
            self.pid = self.child.pid
            timer.start()
            self._communicate()
            if self.timeoutError:
                raise ExecCommandTimeoutError('Timeout after %d sec running: %s' % (self.timeo, self.cmd))
            else:
                timer.cancel()
            try:
                self.cstatus = self._process_exit(self.child.wait())
            except OSError:
                self.cstatus = None
        except Exception as e:
            logging.exception(e)
            raise
        finally:
            self._update_elapsed()
            try:
                if self.child and self.timeoutError:
                    logging.debug("Child process (PID %s) killed" % self.child.pid)
                    self.child.kill()
            except Exception as e:
                logging.exception(e)

        return self

    def _set_start(self):
        """ Set the start time """
        self.start = time.time()

    def _update_elapsed(self):
        """ Updates the elapsed time based off of current time and the start time """
        self.elapsed = time.time() - self.start

    def _communicate(self):
        stdout, stderr = self.child.communicate()
        self.cstdout.write(stdout)
        self.cstderr.write(stderr)

    def _timeout(self):
        self.child.kill()
        self.timeoutError = True
