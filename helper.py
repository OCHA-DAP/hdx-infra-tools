"""tool to setup and configure some aspects of docker-compose stack."""

import docohelper
import os

def main():
    """show a use-case."""
    #
    s = docohelper.DockerHelper.fromcontainer()
    ssh_folder = '/root/.ssh'
    ssh_key = '/'.join([ssh_folder, 'id_rsa'])
    ssh_pub = '.'.join([ssh_key, 'pub'])
    if not os.path.isdir(ssh_folder):
        os.makedirs(ssh_folder)

    s.create_special_file(ssh_pub, 'HDX_SSH_PUB', private=False)
    s.create_special_file(ssh_key, 'HDX_SSH_KEY', private=True)

if __name__ == '__main__':
    main()
