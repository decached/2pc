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
    Status writeFile(1: RFile rFile),
    RFile readFile(1: string filename),
    void commit(1: string filename),
    void abort(1: string filename)
}

service Coordinator {
    void writeFile(1: RFile rFile),
    RFile readFile(1: string filename),
}
