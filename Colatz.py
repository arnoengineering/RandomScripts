#!/usr/bin/python
print("Collatz conjecture Calculator")
usr_in = input("input number: ")
usr = int(usr_in) ** 1000000

count = 0  # how many time it takes to get to one
# print('loop')
while usr > 1:
    if usr % 2 == 0:
        usr = usr // 2
    else:
        usr = 3 * usr + 1
    count += 1

print("Steps: ", c