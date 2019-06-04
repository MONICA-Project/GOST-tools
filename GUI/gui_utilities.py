from checking_functions import *
from ogc_utility import *

def populate(elements_list):
    for i in elements_list:
        i["item"].grid(column=i["column"], row=i["row"])


def restore(self):
    populate(self.main_view_elements)