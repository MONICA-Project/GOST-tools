import os
import subprocess
import requests
import GUI.gui_utilities as gui_ut
import GUI.start_gui as gui
address_file_path = './config_files/GOST_address.txt'


def get_address_from_file():
    """ Reads and returns the address saved in address_file_path. """
    # dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(address_file_path) as fp:
        new_address = fp.readline()
        return new_address


def set_GOST_address(address=None):
    """To set the new GOST address"""
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
    if test_connection(address, verbose=False):
        return address
    else:
        return False


def test_connection(server_address, server_username=None, server_password=None, verbose=True):
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
            if verbose:
                print("Network connectivity: VERIFIED. Server "+server_address+" is reachable!")
            return True
        else:
            print("Something wrong during connection!")
            return False

    except Exception as e:
        print(e)
        return False


def try_port(self=None, port=None, address=None, b=None, take=None):
    if not address:
        address = get_address_from_file()
    x = address.split(":")
    y = x[2].split("/")
    if take:
        return y[0]
    y[0] = port
    first = "/".join(y)
    x[2] = first
    complete = ":".join(x)
    if test_connection(complete):
        set_GOST_address(complete)
        if not b:
            indexes_to_delete = []
            for index, val in enumerate(self.view_elements):
                if "name" in val:
                    if val["name"] in ["address_preview", "new_port_entry", "Confirm changes", "new_port_button", "Insert a new port number", "address_preview"]:
                        indexes_to_delete.append(index)
            for i in sorted(indexes_to_delete, reverse=True):
                self.view_elements[i]["item"].grid_forget()
                del self.view_elements[i]
            # self.address_preview.configure(text="Insert a new address\n(format: http[s]://x.x.x.x:port_number/v1.0)")
            self.port_button = gui_ut.Button(self.top_bar, text="Change port number",
                                             command=lambda: gui.change_port_number(self), bg=gui_ut.change_address_color)
            self.port_button.grid(row=0, column=4)
        else:
            self.confirm_port_button.configure(text="To change port, insert a new port\nand click here")
    else:
        gui_ut.messagebox.showinfo("Error", "invalid Port number")
        self.address_preview.configure(text="Invalid port, insert a new port")