import sys

from utils import (
    read_server_address_dict,
    ErrorState,
    ErrorStateManager
)


addr_dict = read_server_address_dict(sys.argv[1])
N = int(sys.argv[2])

for addr, response_list in addr_dict.items():
    # per address
    print('Server Address', addr)

    count_error = 0     # the total number of errors
    len_error = 0       # the length of errors in progress
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
                print('Error[{0}] {1} - {2} ({3}[s])'.format(
                    count_error,
                    dt_start,
                    res.date_dt,
                    (res.date_dt - dt_start).total_seconds()
                ))
            len_error = 0

    # Result
    if manager.state == ErrorState.CONTINUE:
        count_error += 1
        print('Error[{0}] {1} - continue'.format(
            count_error,
            dt_start
        ))

    print(count_error, 'error(s)')
