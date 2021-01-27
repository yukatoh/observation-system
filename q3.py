import sys

from utils import (
    read_server_address_dict,
    ErrorState,
    ErrorStateManager
)


addr_dict = read_server_address_dict(sys.argv[1])
m = int(sys.argv[2])
t = int(sys.argv[3])

for addr, response_list in addr_dict.items():
    # per address
    print('Server Address', addr)

    count_error = 0  # the total number of errors
    manager = ErrorStateManager()
    for i, res in enumerate(response_list):
        # per response

        # Classify whether the server is overload
        if i < m - 1:
            # In case the total number of response indices 0-i is smaller than M
            over = res.error
        else:
            # Error list of the latest M responses
            error_hist = [r.error for r in response_list[i - m + 1:i + 1]]
            if any(error_hist):
                # In case error_hist has error
                over = True
            else:
                # Time list in the latest M responses
                time_hist = [int(r.time) for r in response_list[i - m + 1:i + 1]]
                # Whether mean of time_hist is larger than T
                over = sum(time_hist) > t * len(time_hist)

        manager.transit(over)  # transit the state

        # Operate according to the current state
        if manager.state == ErrorState.START:
            dt_start = res.date_dt
        elif manager.state == ErrorState.END:
            count_error += 1
            print('Overload[{0}] {1} - {2} ({3}[s])'.format(
                count_error,
                dt_start,
                res.date_dt,
                (res.date_dt - dt_start).total_seconds()
            ))

    # Result
    if manager.state == ErrorState.CONTINUE:
        count_error += 1
        print('Overload[{0}] {1} - continue'.format(
            count_error,
            dt_start
        ))

    print(count_error, 'overload(s)')
