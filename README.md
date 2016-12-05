Project 3   : Two-Phase Commit
CS557       : Intro to Distributed Systems
Author1     : Akash Kothawale <akothaw1@binghamton.edu>
BNumber     : B00655581
Author2     : Jaydeep Ingle <jingle1@binghamton.edu>
BNumber     : B00671052


## Installation

`$ make`

## Execution

`$ ./test_coordinator 8081  # Run on Coordinator machine`

`$ ./test_server 8082  # Run on Server machine`

`$ ./test_client test-coordinator.com 8081 test-server.com 8082 InputFile`


## Report

#### Note
P = Participant(s)
C = Coordinator

#### Structure Code

a. Our code in structured in the following way:

1. server.py      - Handles the functionality of durable read/write. Provides read/write interface to coordinator.
2. coordinator.py - Handles the functionality of two-phase commits. Provides "pseudo" read/write interface to client.
3. client.py      - Use the interface provided by coordinator.py to read/write.

4. test_server.py      - Creates 2 servers (participants) for our tests.
5. test_coordinator.py - Creates coordinator to interface with server(s) and client(s).
6. test_client.py      - Executes all test-cases described below.

7. pX/flog.json   - Write-Ahead Log to store meta information about two-phase commits on P.
8. coor/tlog.json - Write-Ahead Log to store meta information about two-phase commits on Coordinator.

b. RPC interface exposed by P to C: Available in `lib/tpc.thrift`

c. Failures are reflected to client by either sending Status = YES/NO (defined as `enum` in `lib/tpc.thrift`)

d. We've explored the following test cases:

1   - Durability: Files are persistent on the Disk even after the participant is 'dead'.
2   - Concurrency: Two writes on the same filename at P at the same time will abort the 2nd one.
3.1 - C fails before voting. C recovers before P timeout. C reinitiates voting. C makes decision.
3.2 - C fails before voting. P abort on timeout. C sees that P aborted.
4.1 - C fails after partial voting. P wait for decision. C reinitiates voting. C makes decision.
4.2 - C fails after complete voting. P wait for decision. C makes decision.
5   - P fails after it votes. When P recovers it asks C for decision and continues accordingly.
