import logging
import platform
from queue import Queue
from threading import Thread

from desktoptools.common.cmd import exec_cmd


class ShellLibException(Exception):
    def __init__(self, cmd, exitcode, stdout, stderr):
        Exception.__init__(self, stdout)
        self.cmd = cmd
        self.exitcode = exitcode
        self.stdout = stdout
        self.stderr = stderr

    def __str__(self):
        return "CmdError: '%s'; exitcode: %s; stdout: %s; stderr: %s" % \
               (self.cmd, self.exitcode, self.stdout, self.stderr)


class MultiHostException(Exception):
    """ Contains multiple instances of ShellLib Exception.  Variable exceptions is
        a dictionary of {host => Exception}.
    """

    def __init__(self, exceptions):
        Exception.__init__(self)
        self.exceptions = exceptions

    def __str__(self):
        """ String representation of this error. """
        return_string = ""
        for host, error in self.exceptions.iteritems():
            return_string += u"\n  [{0:s}] {1:s}".format(host, error)
        return return_string


def assert_command(command, quiet=False, timeout_min=2):
    """ Runs the specified command and returns the output. Throws exception on Error.
        :param command:  Command to execute.
        :param quiet:    True to suppress the command output and return generic string
                         for pass/fail. False to return command output.
    """
    return run_command(command, True, quiet, timeout_min)


def run_command(command, raise_on_error=False, quiet=False, timeout_min=2):
    """
        Runs the specified command and returns the command_output.

        :param command:        Command to execute.
        :type command str
        :param raise_on_error: Set True to raise exception is an error is found.
        :type raise_on_error bool
        :param quiet:          True to suppress the command command_output and return generic string
                               for pass/fail. False to return command command_output.
        :type quiet bool
        :param timeout_min     Number of minnutes to wait for a given command
        :type timeout_min int
        :return                output lines either static strings or the stdout of the command run
    """
    logging.info("Running Command: {}".format(command))
    timeout_sec = timeout_min * 60  # converting into seconds
    exec_command = exec_cmd.Exec(command, timeout=timeout_sec)
    try:
        exec_command.run()
    except exec_cmd.ExecCommandTimeoutError as e:
        logging.exception(e)
    # Check we executed the command successfully
    exitcode = exec_command.get_status()
    # If quiet flag is set, don't show command_output (useful when executing rise)
    if quiet:
        command_output = "Command executed"
    else:
        command_output = exec_command.get_stdout()
        # Check the ExitCode
    if exitcode != 0:
        if quiet:
            command_error = "Command failed"
        else:
            command_error = exec_command.get_stderr()
        if raise_on_error:
            raise ShellLibException(command, exitcode, command_output, command_error)
        else:
            logging.warning(u"CmdError: '{0:s}'; exitcode: {1:s}; command_output: {2:s}; command_error: {3:s}"
                            .format(command, exitcode, command_output, command_error))
            # Parse and return the command_output as a list
    lines = command_output.split('\n')
    if lines[-1] == '':
        lines = lines[:-1]
    return lines


def assert_remote_command(host_address, command, user="root", quiet=False, timeout_min=5, **kwargs):
    """
        Runs a remote command on the specified host_address,  Throws exception on Error.

        :param host_address:     Remote host_address on which to run a command.
        :param command:  Command to execute.
        :param quiet:    Set True to suppress the command output and return generic string
                         for pass/fail.  False to return command output.
    """
    return run_remote_command(host_address, command, True, user, quiet=quiet, timeout_min=timeout_min, **kwargs)


def run_remote_command(host_address, command, raise_on_error=False, user="root", password=None, quiet=False,
                       timeout_min=5):
    """

        :param host_address:          IP Address of remote host_address.
        :param command:       Command to execute.
        :param raise_on_error:  Set True to raise exception is an error is found.
        :param user:          User Name to use to SSH to remote machine.
        :param quiet:         Set True to suppress the command output and return generic string for pass/fail.
            False to return command output.

    """
    if platform.system() == 'Linux':
        command = u'sshpass -p {password}  ssh -A -o StrictHostKeyChecking=no  {user}@{host_address} "{command}"'.format(
            **locals())
    else:
        command = 'putty -load "{host_address}" -l {user} -pw {password}  "{command}"'.format(**locals())
    return run_command(command, raise_on_error, quiet, timeout_min)


def assert_multi_node_command(host_list, command, user="root", quiet=False):
    """
        Run the specified command and assert it ran successfully on all nodes.

        :param host_list:  List of node IPs to run the command on.
        :type host_list list
        :param command:   Command to execute.
        :param user:      User Name to use to SSH to remote machine.
        :param quiet:     Set True to suppress the command output and return generic string
                          for pass/fail.  False to return command output.
    """
    return run_multi_node_command(host_list, command, True, user, quiet)


def run_multi_node_command(host_list, command, raise_on_error=False, user="root", quiet=False, timeout_min=5):
    """
        Remotely run the specified command on all specified nodes.  Returns a dictionary
        containing {host => stdout}.

        :param host_list:      List of node IPs to run the command on.
        :param command:       Command to execute
        :param raise_on_error:  Set True to raise exception is an error is found.
        :param user:          User Name to use to SSH to remote machine.
        :param quiet:         Set True to suppress the command output and return generic string
                              for pass/fail.  False to return command output
    """
    results = {}  # Dictionary of NodeIP => Successful run Results
    exceptions = {}  # Dictionary of NodeIP => Exceptions occurred

    q = Queue()
    requests = []
    for host in host_list:
        args = [host, command, raise_on_error, user, quiet, timeout_min]
        t = Thread(target=run_remote_command, args=args)
        t.start()
        requests.append(t)

    # Create and run the threadQueue
    for request in results:
        q.put(request)

    q.join()

    if raise_on_error and exceptions:
        raise MultiHostException(exceptions)
    return results
