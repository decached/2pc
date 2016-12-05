typedef i32 TransactionID
typedef string ParticipantID

struct RFile {
    1: required string filename;
    2: required string content;
}

/* Status: Defines the reply of the servers whether the file CAN be written to
 * the disk or not. */ 
enum Status {
    NO = 0
    YES = 1
}

service FileStore {
    void ping(), // Used to check if the server is online.
    oneway void writeFile(1: TransactionID tID, 2: RFile rFile),
    RFile readFile(1: string filename),
    Status canCommit(1: TransactionID tID, 2: bool recover),
    oneway void doCommit(1: TransactionID tID),
    oneway void doAbort(1: TransactionID tID)
}

service Coordinator {
    void ping(),
    Status writeFile(1: RFile rFile),
    RFile readFile(1: string filename),
    Status getDecision(1: TransactionID tID),
}

service TestFileStore {
    void say(1: string word),
    void test(1: i32 testCase),
    void start(1: i32 testCase, 2: i32 pid),
    void clean(),
    void kill(),
}

service TestCoordinator {
    void say(1: string word),
    void test(1: i32 testCase),
    void clean(),
    void kill(),
}
