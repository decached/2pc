struct RFile {
    1: required string filename;
    2: required string content;
}

enum Status {
    FAIL = 0
    READY = 1
}

service FileStore {
    Status writeFile(1: RFile rFile),
    RFile readFile(1: string filename),
    void commit(1: string filename),
    void abort(1: string filename)
}
