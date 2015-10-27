import argparse
import logging
from pprint import pformat
import sys
import time

from desktoptools.common.cmd import shell_lib

from desktoptools.modules.jenkins import jenkins


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-6s line %(lineno)-4s %(message)s')
parser = argparse.ArgumentParser()
parser.add_argument('--jenkins_url', help='The base URL for Jenkins server')
parser.add_argument('--job_name', help='Get info on a specific job.')

def jenkins_cli():
    args = parser.parse_args()
    jenkins_obj = jenkins.Jenkins(args.jenkins_url)
    # TODO: variable from config?!
    job_we_want = args.job_name
    job_info = jenkins_obj.get_job_info_by_name(job_we_want)
    if not job_info:
        logging.error('The job [{}] is not in the list of jobs from jenkins'.format(job_we_want))
        # TODO: do some smart search to get close to the name and pick one
        sys.exit(1)
    logging.info('Job info: {}'.format(pformat(job_info)))


def main():
    if not shell_lib.run_command('docker ps'):
        logging.error('You must be be running a docker daemon!')
        sys.exit(1)
    logging.info('Pulling the latest build docker image..')

    # TODO: This will be a config option
    slave = 'jeffbean/'

    shell_lib.assert_command('docker pull {}'.format(slave))
    logging.info('Starting the container from image')
    docker_container = shell_lib.assert_command('docker run -d {}'.format(slave))
    try:
        logging.info('getting container IP address')
        container_ip_address = shell_lib.assert_command(
            "docker inspect --format '{{{{ .NetworkSettings.IPAddress }}}}' {container[0]}".format(
                container=docker_container))[0]
        time.sleep(10)
        print(shell_lib.assert_remote_command(container_ip_address, "ls -l", user='jenkins', password='jenkins'))

    finally:
        shell_lib.assert_command('docker stop {[0]}'.format(docker_container))
        shell_lib.assert_command('docker rm {[0]}'.format(docker_container))


if __name__ == '__main__':
    '''
    1. First we need to know where the source code of the adapter is
    2. Is docker installed?
        a. it is: move on
        b. it isn't: clone and run the ansible playbook to install docker
    2. pull the docker containers to do the build
    3. More to come..
    '''
    main()
