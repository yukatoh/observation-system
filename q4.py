import sys
from collections import deque

from utils import (
    read_subnet_address_dict,
    ErrorState,
    ErrorStateManager
)


sub_addr_dict = read_subnet_address_dict(sys.argv[1])
N = int(sys.argv[2])

for sub_addr, _addr_dict in sub_addr_dict.items():
    print('Subnet Address', sub_addr)

    sub_errors = []     # a list of `error_terms` per subnet
    for addr, response_list in _addr_dict.items():
        print('Network Address', addr, end=' ')

        count_error = 0     # the total number of errors
        len_error = 0       # the length of errors in progress
        error_terms = []    # a error list of tuple of start and end datetime per server
        manager = ErrorStateManager()
        for res in response_list:
            # per response

            manager.transit(res.error)  # transit the state

            # Operate according to the current error state
            if manager.state == ErrorState.START:
                dt_start = res.date_dt
                len_error += 1
            elif manager.state == ErrorState.CONTINUE:
                len_error += 1
            elif manager.state == ErrorState.END:
                if len_error > N:
                    count_error += 1
                    error_terms.append((dt_start, res.date_dt))
                len_error = 0

        if manager.state == ErrorState.CONTINUE:
            count_error += 1
            error_terms.append((dt_start, 'continue'))

        sub_errors.append(error_terms)
        print(count_error, 'error(s)')

    sub_error_terms = deque(sub_errors.pop(0))
    if all(len(err) > 0 for err in sub_errors):
        # In case all servers have errors
        sub_error_terms = sub_errors.pop(0)
        for terms in sub_errors:
            error_terms = []
            for sub_term in sub_error_terms:
                for term in terms:
                    if term[1] == sub_term[1] == 'continue':
                        if sub_term[0] < term[0]:
                            error_terms.append((term[0], 'continue'))
                        else:
                            error_terms.append((sub_term[0], 'continue'))
                    elif term[1] == 'continue':
                        if sub_term[0] <= term[0] <= sub_term[1]:
                            error_terms.append((term[0], sub_term[1]))
                        elif term[0] <= sub_term[0]:
                            error_terms.append(sub_term)
                    elif sub_term[1] == 'continue':
                        if sub_term[0] <= term[0] <= term[1]:
                            error_terms.append(term)
                        elif term[0] <= sub_term[0] <= term[1]:
                            error_terms.append((sub_term[0], term[1]))
                    else:
                        if sub_term[0] <= term[0] <= sub_term[1] <= term[1]:
                            error_terms.append((term[0], sub_term[1]))
                        elif sub_term[0] <= term[0] <= term[1] <= sub_term[1]:
                            error_terms.append(term)
                        elif term[0] <= sub_term[0] <= term[1] <= sub_term[1]:
                            error_terms.append((sub_term[0], term[1]))
                        elif term[0] <= sub_term[0] <= sub_term[1] <= term[1]:
                            error_terms.append(sub_term)

            sub_error_terms = error_terms
            if len(sub_error_terms) == 0:
                break

    # Result
    for i, term in enumerate(sub_error_terms):
        if term[1] == 'continue':
            print('Error[{0}] {1} - continue'.format(
                i + 1,
                term[0]
            ))
        else:
            print('Error[{0}] {1} - {2} ({3}[s])'.format(
                i + 1,
                term[0],
                term[1],
                (term[1] - term[0]).total_seconds()
            ))

    print(len(sub_error_terms), 'error(s)')
