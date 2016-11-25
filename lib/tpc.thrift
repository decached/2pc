struct RFile {
    1: required string filename;
    2: required string content;
}

enum Status {
    NO = 0
    YES = 1
}

enum Order {
    ABORT = 0
    COMMIT = 1
}

service FileStore {
    Status writeFile(1: RFile rFile),
    RFile readFile(1: string filename),
    void commit(1: Order order),
    void abort(1: Order order)
}

service Coordinator {
    Status writeFile(1: RFile rFile),
    RFile readFile(1: string filename),
}
