import paramiko
from os.path import expanduser
import os
from user_definition import *
import time


# Assumption : Anaconda, Git (configured)
def ssh_client():
    """Return ssh client object"""
    print("Configuring SSH Client")
    return paramiko.SSHClient()


def ssh_connection(ssh, ec2_address, user, key_file):
    """Connect to ssh and return ssh connect object"""
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    time.sleep(10)
    # ssh.connect(ec2_address, username=user,
    #             key_filename=expanduser("~") + key_file)
    ssh.connect(ec2_address, username=user,
                key_filename=expanduser(".") + key_file)

    print("SSH Connection Established")
    return ssh


# def create_or_update_environment(ssh):
#     """Build environment from .yml file """
#     print('Installing Environment . . . This may take a few minutes')
#     stdin, stdout, stderr = \
#         ssh.exec_command("conda env create -f "
#                          "~/" + git_repo_name + "/venv/env.yml")
#     # print(stderr.read())
#     if (b'already exists' in stderr.read()):
#         stdin, stdout, stderr = \
#             ssh.exec_command("conda env update -f "
#                              "~/" + git_repo_name + "/venv/env.yml")


# def git_clone(ssh):
#     """Clone or pull git repo"""
#     print('Pulling files from github')
#     git_oauth = "296a5a48dcf2f4377455599deca2ecb0a3489768"
#     stdin, stdout, stderr = ssh.exec_command("git --version")
#     if (b"" is stderr.read()):
#         git_clone_command = "git clone " + \
#                             "https://" + \
#                             git_oauth + \
#                             "@github.com/" + \
#                             git_repo_owner + "/" + git_repo_name + ".git"
#         stdin, stdout, stderr = ssh.exec_command(git_clone_command)
#         # print(stderr.read())
#
#     if (b'already exists' in stderr.read()):
#         stdin, stdout, stderr = ssh.exec_command("cd " + git_repo_name +
#                                                  "; git pull")


# def set_cronjob(ssh):
#     """Set cronjob executing code from git repo"""
#     print('Launching Cronjob got to IP:5001/upload to check that '
#           'Aligned page is up and running')
#     stdin, stdout, stderr = \
#         ssh.exec_command('crontab -l ;'
#                          ' echo "* * * * * ~/.conda/envs/MSDS603/bin/python '
#                          '/home/ec2-user/' + git_repo_name + '/code' +
#                          '/calculate_driving_time.py")'
#                          ' | sort - | uniq - | crontab -')


def run_flask(ssh):
    """Initiate the flask route"""
    # print('\n\nLaunching flask - go to
    # https://34.215.178.90:5000/ to check that'
    #      'Aligned page is up and running \n')

    transport = ssh.get_transport()
    channel = transport.open_session()
    # channel.set_combine_stderr(1)
    print('Transport Channel Working')

    channel.exec_command('source ~/env/bin/activate \n cd ' +
                         git_repo_name +
                         '/code/aligned/ \n' +
                         'flask run --host=0.0.0.0 ' +
                         '--cert ' + cert + ' --key ' + key +
                         ' > /dev/null 2>&1 &')
    # 'python upload_flask.py > /dev/null 2>&1 &')

    print('\n\nLaunching flask - go to https://34.215.178.90:5000/ to check '
          'Aligned page is up and running \n')


def main():
    """Main driver function"""
    ssh = ssh_client()
    ssh_connection(ssh, ec2_address, user, key_file)
    # git_clone(ssh)
    # create_or_update_environment(ssh)
    run_flask(ssh)
    print('Logging out')
    ssh.close()

    print('Done')


if __name__ == '__main__':
    main()
