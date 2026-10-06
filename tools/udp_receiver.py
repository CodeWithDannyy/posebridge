"""Debug receiver: listens for PoseBridge packets and prints stats. Ctrl+C to quit.

Proves the Python side works before Unity is involved.
"""
import socket
import statistics
import time

from perception.packet import decode_packet
from perception.udp import DEFAULT_HOST, DEFAULT_PORT


def main() -> None:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((DEFAULT_HOST, DEFAULT_PORT))
    # A timeout lets Ctrl+C work: on Windows a socket blocked forever ignores it.
    sock.settimeout(1.0)
    print(f"Listening on {DEFAULT_HOST}:{DEFAULT_PORT} ...")

    last_frame = None
    dropped = 0
    window_latencies: list[float] = []
    window_tracked = 0
    window_start = time.time()
    try:
        while True:
            try:
                data, _ = sock.recvfrom(65535)  # max UDP datagram size
            except socket.timeout:
                print("waiting for packets...")
                continue

            packet = decode_packet(data)
            now_ms = time.time() * 1000
            window_latencies.append(now_ms - packet["t_capture_ms"])
            window_tracked += packet["tracked"]

            # A jump in the frame counter means packets were lost.
            if last_frame is not None and packet["frame"] > last_frame + 1:
                dropped += packet["frame"] - last_frame - 1
            last_frame = packet["frame"]

            if time.time() - window_start >= 1.0:
                print(
                    f"{len(window_latencies):3d} packets/s | "
                    f"tracked {window_tracked:3d} | dropped total {dropped} | "
                    f"python->receiver latency median {statistics.median(window_latencies):.1f} ms, "
                    f"max {max(window_latencies):.1f} ms"
                )
                window_latencies.clear()
                window_tracked = 0
                window_start = time.time()
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        sock.close()


if __name__ == "__main__":
    main()
