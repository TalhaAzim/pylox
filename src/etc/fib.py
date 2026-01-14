#!/usr/bin/env python3

def fib(a):
    stack = [a]
    memo = {0: 0, 1: 1}

    failsafe_enabled = False
    c = 0
    while stack:
        n = stack.pop()

        if n not in memo:
            print(f"fib({n}) not in memo. Adding {n} to stack.")
            stack.append(n)
        
        print(f"Checking for fib({n - 1}) in memo.")
        
        if n - 1 not in memo:
            print(f"fib({n - 1}) not in memo. Adding {n - 1} to stack.")
            stack.append(n - 1)
            continue

        '''
        For some reason this breaks the function, but finally practicing stack based
        stuff broke my brain for a bit so I'll trace out why later. I'm guessing it
        has something to do with the `continue` statement above.

        # print(f"Checking for fib({n - 2}) in memo.")

        # if n - 2 not in memo:
        #     print(f"fib({n - 2}) not in memo. Adding {n - 2} to stack.")
        #     stack.append(n - 2)
        #     continue'''
        
        memo[n] = memo[n - 1] + memo[n -2]

        c += 1
        if c > 16 and failsafe_enabled:
            print("Failsafe triggered")
            return stack
    return memo[a]

print(fib(1000))