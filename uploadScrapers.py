import os
import requests
import sys
import time


class UploadScrapers(object):
    '''get a scraper archive (currently either fts, rw or sw) and update it on hdx ckan'''

    TMPDIR = '/tmp'
    FILENAME = 'csv.zip'
    FORMAT = 'zip'
    DATE = time.strftime('%Y-%m-%dT%H:%M:%S%z')
    DESCRIPTION = 'Automatic file upload at: ' + DATE

    # define each scraper as a list of [package_id, resource_id, source_url]
    SCRAPERS = {
        'fts': [
            'raw-fts-input',
            '12300d47-dc3b-480d-bcd6-9a2872b26d23',
            'https://ds-ec2.scraperwiki.com/gbgac6a/8018ef27ff614e4/http/v1.1/' + FILENAME
        ],
        'rw': [
            'raw-reliefweb-statistics',
            '8d61a3f3-3fea-4b9c-924c-e5a4744793c8',
            'https://ds-ec2.scraperwiki.com/bcbk6tq/e81a96f6e040418/http/v1.1/' + FILENAME
        ],
        'sw': [
            'raw-scraperwiki-input',
            '14b71a81-f61a-4ebd-bbbd-795b6762d805',
            'https://ds-ec2.scraperwiki.com/enf6nmy/8ab0038b6f524ae/http/v1.1/' + FILENAME
        ]
    }

    def __init__(self, type):
        if type not in self.SCRAPERS:
            raise NameError('No scraper by that name.')
        for envvar in ['HDX_PREFIX', 'HDX_DOMAIN', 'HDX_CKAN_API_KEY', 'HDX_USER_AGENT']:
            if not len(envvar):
                raise NameError(envvar + ' not defined in the environment.')
        self.PACKAGE_ID, self.RESOURCE_ID, self.SOURCE_URL = self.SCRAPERS[type]
        self.CKAN_URL = 'https://' + os.getenv('HDX_PREFIX') + 'data.' + os.getenv('HDX_DOMAIN')
        self.HEADERS = {
            'X-CKAN-API-Key': os.getenv('HDX_CKAN_API_KEY'),
            'User-agent': os.getenv('HDX_USER_AGENT')
        }
        self.FILE = os.path.join(self.TMPDIR, self.FILENAME)

    def _format_resource(self):
        '''formats a HDX resource to be uploaded'''
        resource = {}
        resource['package_id'] = self.PACKAGE_ID
        resource['id'] = self.RESOURCE_ID
        resource['name'] = self.FILENAME
        resource['format'] = self.FORMAT
        # retarded ckan is still requesting a mandatory url field
        # just use a blank url field, it will be replaced with the correct url
        resource['url'] = ''
        resource['description'] = self.DESCRIPTION
        self.RESOURCE = resource

    def _download_file(self):
        '''download the scraper file locally'''
        print('Trying to get', self.FILE, 'from', self.SOURCE_URL)
        r = requests.get(self.SOURCE_URL, stream=True)
        r.status_code
        with open(self.FILE, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    # filter out keep-alive new chunks
                    f.write(chunk)
                    f.flush()

    def remove_local_file(self):
        '''clean up the downloaded file'''
        try:
            os.remove(self.FILE)
        except:
            print('File', self.FILE, 'was not found.')

    def create_resource(self):
        '''creates or overwrites a resource on HDX ckan'''

        self._download_file()
        self._format_resource()
        url = self.CKAN_URL + '/api/3/action/resource_create'
        files = {'upload': open(self.FILE, 'rb')}
        print('Uploading', self.FILENAME)
        try:
            r = requests.post(url, data=self.RESOURCE, headers=self.HEADERS, files=files)
            if r.status_code == 200:
                if r.json()['success']:
                    print('Success.')
            elif r.status_code == 413:
                message = 'File is too large'
                print('FAILED.', message)
                raise IndexError(message)
            else:
                print('FAILED.', r.text)
                raise IndexError(r.text)
        except IndexError:
            raise
        except:
            e = sys.exc_info()
            print(e[1])
            raise Exception(e)


def main():
    if len(opts):
        scraper = opts.pop(0)
        s = UploadScrapers(scraper)
        s.create_resource()
        s.remove_local_file()
    else:
        print('Error. No scraper type selected.')


if __name__ == '__main__':
    opts = sys.argv
    opts.pop(0)
    main()
