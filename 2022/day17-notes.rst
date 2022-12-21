
AOC 2022 Day 17 Notes
=====================

example - there is a cycle with a period of 53.
input - there is a cycle with a period of 2702. 


example
-------

Q: Height after 2022 rocks?

Highest rock at 3068.
Jet cycle size: 40
Found cycle from 3008 to 3061.
Cycle start: 25
Cycle size: 53
Rock number associated with cycle start: 15
Rock number associated with cycle end: 50
Size of cycle in rocks: 35
- Rock cycle table -
Cycle offset        0: rock offset        0
Cycle offset        1: rock offset        1
Cycle offset        4: rock offset        2
Cycle offset        7: rock offset        3
Cycle offset       11: rock offset        5
Cycle offset       12: rock offset        6
Cycle offset       14: rock offset        7
Cycle offset       17: rock offset        9
Cycle offset       18: rock offset       10
Cycle offset       19: rock offset       11
Cycle offset       22: rock offset       12
Cycle offset       24: rock offset       13
Cycle offset       26: rock offset       16
Cycle offset       28: rock offset       17
Cycle offset       31: rock offset       18
Cycle offset       35: rock offset       20
Cycle offset       36: rock offset       21
Cycle offset       38: rock offset       22
Cycle offset       39: rock offset       23
Cycle offset       41: rock offset       25
Cycle offset       42: rock offset       26
Cycle offset       44: rock offset       27
Cycle offset       45: rock offset       28
Cycle offset       47: rock offset       30
Cycle offset       48: rock offset       31
Cycle offset       51: rock offset       32

Determine the number of complete and partial cycles required.

15 rocks before cycles start.
35 rocks per cycle

15 rocks + 35 rocks/cycle * x cycles == 2022 rocks
(2022 rocks - 15 rocks) / 35 rocks/cycle == 57 cycles
2022 rocks - (15 rocks + 35 rocks/cycle * 57 cycles) == 12 rocks required
Consulting offset table, 12 rocks == 22 height

total height == 25 lines + 53 lines/cycle * 57 cycles + 22 lines

25 + 53 * 57 + 22 == 3068

