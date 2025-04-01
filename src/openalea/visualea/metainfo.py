"""Configuration file"""

__license__ = "Cecill-C"
__revision__ = " $Id$"


def get_version():

    from importlib.metadata import version
    return version("openalea.visualea")

url = "http://openalea.rtfd.io"

def get_copyright():

    return "Copyright \xa9 2006-2023 inria/CIRAD/INRAE\n"
