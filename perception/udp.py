#Send packets to Unity over UDP.
import socket

DEFAULT_HOST = "127.0.0.1"  # localhost: this computer only
DEFAULT_PORT = 5005         # Unity must listen on the same port


class UdpSender:
    def __init__(self, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> None:
        self._address = (host, port)
        # AF_INET = IPv4, SOCK_DGRAM = UDP (SOCK_STREAM would be TCP).
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send(self, data: bytes) -> None:
        # No connection, no reply: fire and forget.
        self._sock.sendto(data, self._address)

    def close(self) -> None:
        self._sock.close()
