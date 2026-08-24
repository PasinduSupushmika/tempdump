import socket
import threading
import time
import struct

state = {
    "rotor_speed": 1064,
    "reported_speed": 1064
}


def handle_client(conn, addr):
    print(f"[+] Connection received from {addr}")

    try:
        data = conn.recv(1024)

        print(f"[DEBUG] Received: {data!r}")

        if data.startswith(b"READ"):
            response = struct.pack(
                ">HH",
                state["rotor_speed"],
                state["reported_speed"]
            )

            print(
                f"[PLC] Sending: "
                f"Rotor={state['rotor_speed']} | "
                f"HMI={state['reported_speed']}"
            )

            conn.sendall(response)

        elif data.startswith(b"WRITE"):
            payload = data[5:]

            if len(payload) >= 4:
                target_speed, spoofed_speed = struct.unpack(
                    ">HH",
                    payload[:4]
                )

                state["rotor_speed"] = target_speed
                state["reported_speed"] = spoofed_speed

                print(
                    f"[PLC] WRITE received: "
                    f"Rotor={target_speed} Hz | "
                    f"HMI={spoofed_speed} Hz"
                )

                conn.sendall(b"ACK")

        else:
            print(f"[!] Unknown request: {data!r}")

    except Exception as e:
        print(f"[!] Client handler error: {type(e).__name__}: {e}")

    finally:
        try:
            conn.close()
        except Exception:
            pass

        print(f"[-] Connection closed: {addr}")


def display_loop():
    while True:
        print(
            f"[PLC State] "
            f"Centrifuge Rotor: {state['rotor_speed']} Hz | "
            f"HMI Telemetry: {state['reported_speed']} Hz"
        )

        time.sleep(2)


def main():

    server = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    server.setsockopt(
        socket.SOL_SOCKET,
        socket.SO_REUSEADDR,
        1
    )

    server.bind(("0.0.0.0", 102))

    server.listen(5)

    print("[*] Natanz Cascade PLC Active.")
    print("[*] Listening on TCP port 102...")
    print("=" * 60)

    display_thread = threading.Thread(
        target=display_loop,
        daemon=True
    )

    display_thread.start()

    try:

        while True:

            conn, addr = server.accept()

            client_thread = threading.Thread(
                target=handle_client,
                args=(conn, addr),
                daemon=True
            )

            client_thread.start()

    except KeyboardInterrupt:

        print("\n[*] PLC shutting down...")

    except Exception as e:

        print(
            f"[!] Server error: "
            f"{type(e).__name__}: {e}"
        )

    finally:

        server.close()


if __name__ == "__main__":
    main()