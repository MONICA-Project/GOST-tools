import os
import subprocess

address_file_path = 'config_files/GOST_address.txt'


def get_address_from_file():
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
    if test_connection(address[:-5]):
        return address
    else:
        return False


def test_connection(address, verbose=False):
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
