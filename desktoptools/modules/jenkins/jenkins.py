import logging

from desktoptools.common import request_helper


JSON_API_SUFFIX = "api/json"


class Jenkins(object):
    """
    Represents a jenkins environment.
    """

    def __init__(self, base_server_url, username=None, password=None):
        """
        :param base_server_url:  jenkins instance including port, str
        :param username: username for jenkins auth, str
        :param password: password for jenkins auth, str
        :return: a Jenkins obj
        """
        self.base_server_url = base_server_url
        self.username = username
        self.password = password

    def base_server_url(self):
        """
        :return: base url for the Jenkins server object
        """
        # TODO: Add a config value here
        return self.base_server_url

    def get_jobs(self):
        """
        Get all the jobs from the Jenkins server
        :return: a list of job names on the jenkins server
        :returns list
        """
        logging.info('Getting all jobs for jenkins')
        jobs_url = "{0}/{1}".format(self.base_server_url, JSON_API_SUFFIX)
        r = request_helper.get_json(jobs_url)
        return [job.get('name') for job in r.get('jobs')]

    def get_views(self):
        """
        Get all the jobs from the Jenkins server
        :return: a list of job names on the jenkins server
        :returns list
        """
        jobs_url = "{0}/{1}".format(self.base_server_url, JSON_API_SUFFIX)
        r = request_helper.get_json(jobs_url)
        return [job.get('name') for job in r.get('views')]

    def get_job_info_by_name(self, job_name):
        """
        Get the json snip for a job by name
        :param job_name: string of the job name
        :return: the json object for that job or None if not found
        """
        job_info_url = "{0}/{1}".format(self.base_server_url, JSON_API_SUFFIX)
        r = request_helper.get_json(job_info_url)
        job_rel_info = next((job for job in r.get('jobs') if job.get('name') == job_name), None)
        logging.debug(job_rel_info)
        return request_helper.get_json("{}/{}".format(job_rel_info.get('url'), JSON_API_SUFFIX))