import os
import subprocess
import requests

address_file_path = './config_files/GOST_address.txt'


def get_address_from_file():
    """ Reads and returns the address saved in address_file_path. """
    # dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(address_file_path) as fp:
        new_address = fp.readline()
        return new_address


def set_GOST_address(address=None):
    if not address:
        address = get_address_from_file()
    else:
        f = open(address_file_path, 'w')
        f.writelines([])
        f.close()
        f = os.open(address_file_path, os.O_RDWR)
        os.write(f, bytes(address, 'utf-8'))
        os.fsync(f)
        os.close(f)
    if test_connection(address):  # [:-5]):
        return address
    else:
        return False


def test_connection(server_address, server_username=None, server_password=None):
    """ This function checks if a REST connection is correctly configured.

    :param server_address: The address of the OGC server.
    :param server_username: The username necessary to be authenticated on the server.
    :param server_password: The password related to the given username.
    :return: True if it is possible to establish a connection, False otherwise.
    """

    try:
        if server_username is None and server_password is None:
            r = requests.get(url=server_address)
        else:
            r = requests.get(url=server_address, auth=(server_username, server_password))
        if r.ok:
            print("Network connectivity: VERIFIED. Server "+server_address+" is reachable!")
            return True
        else:
            print("Something wrong during connection!")
            return False

    except Exception as e:
        print(e)
        return False


def old_test_connectivity(address, verbose=False):
    if verbose:
        response = os.system("ping " + address)
    else:
        print("verifying connection...")
        with open(os.devnull, 'w') as DEVNULL:
            try:
                subprocess.check_call(
                    ['ping', '-i', '3', address],
                    stdout=DEVNULL,  # suppress output
                    stderr=DEVNULL
                )
                print("connection available on address " + address)
                response = 0
            except subprocess.CalledProcessError:
                response = 1
    return response == 0
