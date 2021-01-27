from enum import Enum, auto
import datetime
import csv
from ipaddress import ip_interface


class ErrorState(Enum):
    """Enumerate class of error state
    """
    START = auto()
    END = auto()
    CONTINUE = auto()
    NORMAL = auto()


class ErrorStateManager:
    """Error state management class
    """
    state: ErrorState

    def __init__(self):
        self.state = ErrorState.NORMAL

    def transit(self, error: bool) -> None:
        """transits the error state according to the given error flag

        Args:
            error (bool): the current error flag

        """
        if self.state == ErrorState.NORMAL:
            if error:
                self.state = ErrorState.START
            else:
                self.state = ErrorState.NORMAL

        elif self.state == ErrorState.START:
            if error:
                self.state = ErrorState.CONTINUE
            else:
                self.state = ErrorState.END

        elif self.state == ErrorState.END:
            if error:
                self.state = ErrorState.START
            else:
                self.state = ErrorState.NORMAL

        elif self.state == ErrorState.CONTINUE:
            if error:
                self.state = ErrorState.CONTINUE
            else:
                self.state = ErrorState.END


class Response:
    """Response info class

    Args:
        date (str): date string of the response
        time (str): time string of the response

    """
    date: str
    time: str
    date_dt: datetime.datetime
    error: bool

    def __init__(self, date: str, time: str):
        self.date = date
        self.time = time
        self.date_dt = datetime.datetime.strptime(date, '%Y%m%d%H%M%S')
        self.error = True if time == '-' else False

    def __repr__(self):
        return 'Response(date: \'{0}\', time: \'{1}\')'.format(self.date, self.time)


def read_server_address_dict(path: str):
    """Read an input file and format as a dictionary

    An input file should be csv format, and each row includes date (index 0), server address (index 1),
    and response time data (index 2), such as '20201019133124,10.20.30.1/16,2'.

    Args:
        path (str): input file path

    Returns:
        dict[str, list[Response]]: a dictionary of address string keys to list of response info values

    """

    address_dict = dict()
    print('Opening {} ...'.format(path))
    with open(path) as f:
        reader = csv.reader(f)
        for row in reader:
            res_list = address_dict.get(row[1], [])     # get a value if the address key exists else an empty list
            res_list.append(Response(row[0], row[2]))
            address_dict[row[1]] = res_list

    return address_dict


def read_subnet_address_dict(path: str):
    """Read an input file and format as a dictionary

    An input file should be csv format, and each row includes date (index 0), server address (index 1),
    and response time data (index 2), such as '20201019133124,10.20.30.1/16,2'.

    Args:
        path (str): input file path

    Returns:
        dict[str, dict[str, list[Response]]]: a dictionary of subnet address string keys to dictionary values of
            network address string keys to response info values

    """

    address_dict = dict()
    with open(path) as f:
        reader = csv.reader(f)
        for row in reader:
            nw_address = str(ip_interface(row[1]).network)

            addr_dict = address_dict.get(nw_address, dict())

            res_list = addr_dict.get(row[1], [])
            res_list.append(Response(row[0], row[2]))
            addr_dict[row[1]] = res_list

            address_dict[nw_address] = addr_dict

    return address_dict
