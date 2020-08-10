import re
import time
import os

from ip2geotools.databases.noncommercial import DbIpCity

# regex for pulling out the ip address
ip_regex = r"(?:[0-9]{1,3}\.){3}[0-9]{1,3}"
# regex for pulling out the epoch time
epoch_regex = r"(?:[0-9]{9,15}\.){1}[0-9]{1,15}"

log_db: dict = dict()


# this is our custom ip log class for holding are data struct.
class IPLogs:
    ip_address = None
    tries = 0
    reports = None
    latitude = None
    longitude = None
    final_report: dict = dict()

    def __init__(self, ip):
        self.final_report = dict()
        self.reports = set()
        self.ip_address = ip
        self.tries = 1
        # run geo location one time to pull the data down.
        # this will reduce the amount of api request we make
        # some api servers throttle the call requests.
        self.get_location()

    def add_retry(self, another_time):
        self.tries += 1
        self.reports.add(float(another_time))

    def get_location(self):
        if self.ip_address != '0.0.0.0' and self.ip_address != '127.0.0.1':
            api_response = DbIpCity.get(ip_match, api_key='free')
            # pull the response objects from the json and assign it to
            # the lat, long vars
            self.latitude = api_response.latitude
            self.longitude = api_response.longitude
        else:
            self.latitude = '0'
            self.longitude = '0'

    def generate(self):
        first_report = None

        for r in self.reports:
            # if we don't have any reports just set the first report
            if first_report is None:
                first_report = r
                self.final_report[first_report] = 0

            if r - float(first_report) < 300:
                # if we are less than 5 mins from the first report
                # increment the count
                self.final_report[first_report] += 1
            else:
                # take the epoch time and normalize it to human readable
                # print out the report
                # clear out and start over
                self.final_report[r] = 0
                first_report = r


def generate_report():
    for report in log_db:
        log_db[report].generate()
    for final_report in log_db:
        for report in log_db[final_report].final_report:
            if log_db[final_report].final_report[report] >= 10:
                normalize_time = time.strftime('%Y-%m-%d %H:%M:%S',
                                               time.localtime(report))
                print(
                        f'{final_report} had '
                        f'{log_db[final_report].final_report[report]} '
                        f'failed login attempts in a 5 minute period on '
                        f'{normalize_time} and has a Lat/Long of '
                        f'{log_db[final_report].latitude}/'
                        f'{log_db[final_report].longitude}.')


with open(os.path.dirname(__file__) + '/flask_server.log', 'r') as logs:
    count = 0
    first_time = None
    for line in logs:
        ip_match_reg = re.search(ip_regex, line)
        epoch_match_reg = re.search(epoch_regex, line)

        # try:
        ip_match = ip_match_reg.group()
        epoch_match = epoch_match_reg.group()

        if ip_match and epoch_match:
            # if we have a match in the log_db dict add the retry for the
            # object
            if ip_match in log_db:
                log_db[ip_match].add_retry(epoch_match)
            else:
                # else just create a new instance of IPLogs
                log_db[ip_match] = IPLogs(ip_match)
        # gotcha caught them all
        # except:
        #     print(f'[Error] parsing error')
    # generate the report after looping over the text file
    generate_report()
