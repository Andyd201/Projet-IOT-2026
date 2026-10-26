import argparse
import threading

from distance import surveiller_distance
from joystick import executer_joystick
from moteurs_serie import executer_moteurs


def executer(args):
    """Lance le joystick, la distance et les moteurs en parallèle."""
    stop_event = threading.Event()
    services = [
        ("joystick", executer_joystick, (args.joystick_port, args.joystick_baud)),
        ("distance", surveiller_distance, ()),
        ("moteurs", executer_moteurs, (args.moteurs_port,)),
    ]
    threads = []

    for nom, fonction, arguments in services:
        thread = threading.Thread(
            name=nom,
            target=fonction,
            args=(*arguments, stop_event),
        )
        thread.start()
        threads.append(thread)

    print("[MAIN] Joystick, distance et moteurs démarrés. Ctrl+C pour arrêter.")

    try:
        while all(thread.is_alive() for thread in threads):
            stop_event.wait(0.5)
    except KeyboardInterrupt:
        print("\n[MAIN] Arrêt demandé.")
    finally:
        stop_event.set()
        for thread in threads:
            thread.join()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Lance ensemble le joystick, la distance et les moteurs."
    )
    parser.add_argument("--joystick-port", default="/dev/ttyACM1")
    parser.add_argument("--joystick-baud", type=int, default=9600)
    parser.add_argument("--moteurs-port", default="/dev/ttyACM0")
    executer(parser.parse_args())
