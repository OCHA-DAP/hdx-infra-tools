#!/usr/bin/python
"""
Attempt to clean up old backups in a folder (nonrecursive)

Expected backup format:
aaa[.bbb[.ccc[.ddd[.eee[.fff.[....]]]]].YYYYmmDD-HHMMSS.(sql|psql|tar).gz

Available params: -q (quiet) and -f (relly delete)
"""

import sys
import os
import datetime

class BackupCleaner(object):
    """implement a simple schedule to remove old useless backups."""

    def __init__(self, folder='test-backup/', prefix='', num_years=10,
                 num_months=4, num_weeks=5, num_days=8, weekday=5):
        """init."""

        # location of the backup files
        self.BACKUP_FOLDER = folder
        # optional prefix to filter the backups to be removed (e.g prod.ckan.files)
        self.PREFIX = prefix
        # how many yearly backups we keep?
        self.YEARLY = num_years
        # how many monthly backups we keep?
        self.MONTHLY = num_months
        # how many weekly backups we keep?
        self.WEEKLY = num_weeks
        # how many daily backups we keep?
        self.DAILY = num_days
        # what is the weekly backup weekday? (0 Monday, 6 Sunday)
        self.WEEKLY_WEEKDAY = weekday
        # date time reference - the execution time
        self.NOW = datetime.datetime.now()

    def clean_folder(self, pretend=True, verbose=True):
        """main routine."""
        for root, dirs, files in os.walk(self.BACKUP_FOLDER):
            for file in sorted(files):
                file = os.path.join(root, file)
                if self.PREFIX not in file:
                    self._print('skipping file (prefix not found).', verbose)
                    continue
                if file[-3:] != '.gz':
                    self._print([file,'is not a regular backup file. skipping it...'], verbose)
                    continue
                # print file,
                o = self._file_date(file)
                if self._is_yearly(o):
                    if self._get_valid_status(o, self.YEARLY, 'y'):
                        self._print([file, 'YEARLY'], verbose)
                        continue
                    self._print([file, 'older YEARLY - I will delete it!'], verbose)
                elif self._is_monthly(o):
                    if self._get_valid_status(o, self.MONTHLY, 'm'):
                        self._print([file, 'MONTHLY'], verbose)
                        continue
                    self._print([file, 'older MONTHLY - I will delete it!'], verbose)
                elif self._is_weekly(o):
                    if self._get_valid_status(o, self.WEEKLY, 'w'):
                        self._print([file, 'WEEKLY'], verbose)
                        continue
                    self._print([file, 'older WEEKLY - I will delete it!'], verbose)
                elif self._get_valid_status(o, self.DAILY, 'd'):
                    self._print([file, 'DAILY'], verbose)
                    continue
                else:
                    self._print([file, 'UNKNOWN / OLDER DAILY - GOOD FOR DELETION!'], verbose)
                if not pretend:
                    # really removes the file!
                    os.remove(file)

    @staticmethod
    def _print(text, verbose):
        """print stuff."""
        if not verbose:
            return
        if type(text) is str:
            print text
        elif type(text) is list:
            print ' '.join(text)

    def _file_date(self, filename):
        """
        make up the datetime object corresponding to the filename label.

        Relies on the fact that the timestamp in the filename is exactly
        last-last group separated by dot, like:
        prod.fff.ggg.20140506-132245.psql.gz or
        prod.fff.ggg.20140506-132245.tar.gz
        """
        strdatetime = filename.split('.')[-3]
        return datetime.datetime.strptime(strdatetime, '%Y%m%d-%H%M%S')

    def _is_yearly(self, date):
        if date.month == 1 and date.day == 1:
            return True
        return False

    def _is_monthly(self, date):
        if date.day == 1:
            return True
        return False

    def _is_weekly(self, date):
        if date.weekday() == self.WEEKLY_WEEKDAY:
            return True
        return False

    def _get_valid_status(self, o, max, unit):
        """return True if the file needs to be kept."""
        if unit == 'y':
            diff = datetime.timedelta(days=365 * max)
        elif unit == 'm':
            diff = datetime.timedelta(days=31 * max)
        elif unit == 'w':
            diff = datetime.timedelta(days=7 * max)
        elif unit == 'd':
            diff = datetime.timedelta(days=max)
        else:
            print 'Invalid unit passed... Exiting'
            sys.exit()
        if o - self.NOW > datetime.timedelta(minutes=1):
            print 'backup date is in the future... Exiting'
            sys.exit()
        if self.NOW - o < diff:
            return True
        else:
            return False

if __name__ == '__main__':
    pretend = True
    verbose = True
    folder = '.'
    if len(sys.argv):
        for arg in sys.argv:
            if arg == '-f':
                pretend = False
            elif arg == '-q':
                verbose = False
            elif os.path.isdir(arg):
                folder = arg

    cleaner = BackupCleaner(folder=folder)
    cleaner.clean_folder(pretend=pretend, verbose=verbose)
