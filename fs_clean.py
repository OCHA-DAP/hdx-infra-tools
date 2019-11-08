import psycopg2
import os
import time

SQL = dict(
    HOST='dbckan',
    PORT='5432',
    DB=str(os.getenv('HDX_CKANDB_DB')),
    USER=str(os.getenv('HDX_CKANDB_USER')),
    PASSWORD=str(os.getenv('HDX_CKANDB_PASS'))    
)
FSDIR = os.getenv('HDX_FILESTORE')

def get_resource_list(host=SQL['HOST'], port=SQL['PORT'], dbname=SQL['DB'], user=SQL['USER'], password=SQL['PASSWORD']):
    try:
        con = psycopg2.connect(host=host, port=port, database=dbname, user=user, password=password)
        cur = con.cursor()
        # q = 'SELECT COUNT(id) from resource'
        q = "SELECT id FROM resource WHERE state='active'"
        cur.execute(q)
        lines = cur.fetchall()
        resource_list = [l[0] for l in lines]
    except:
        print("I am unable to connect to the database, exiting.")
    return resource_list

def get_file_list(basedir=FSDIR):
    resource_dir = os.path.join(basedir, 'resources')
    file_list = []
    for root, dirs, files in os.walk(resource_dir):
        prefix = root.replace(resource_dir, '').replace('/', '')
        for file in files:
            # print(root.replace(resource_dir, '').replace('/', ''), file)
            # print('%s%s' % (prefix, file))
            file_list.append(prefix + file)
            # time.sleep(.5)
    return file_list

def remove_file(file=None):
    if not file:
        return
    print('I will remove this file:', file)

if __name__ == '__main__':
    print('Getting the resource list from db...')
    start_time = time.time()
    resources = get_resource_list()
    print('Done in', time.time() - start_time)

    print('Getting the file list from disk...')
    start_time = time.time()
    files = get_file_list()
    print('Done in', time.time() - start_time)

    print('Building to list of files to be removed...')
    start_time = time.time()
    files_to_remove = [file for file in files if file not in resources]
    print('Done in', time.time() - start_time)
    
    print('About to remove the extra files...')
    print(files_to_remove)
    print(len(files_to_remove))
