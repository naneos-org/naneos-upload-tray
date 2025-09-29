import atexit
import socket

DEFAULT_LOCK_PORT = 52721  # fix port for single instance lock


class SingleInstance:
    def __init__(self):
        self.port = DEFAULT_LOCK_PORT
        self.sock = None

    def acquire(self) -> bool:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.bind(("127.0.0.1", self.port))
            s.listen(1)
        except OSError:
            return False
        self.sock = s
        atexit.register(self.release)
        return True

    def release(self):
        if self.sock:
            try:
                self.sock.close()
            except Exception:
                pass
            self.sock = None
