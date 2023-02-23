import subprocess
import sys
from time import sleep

from load import loadSite


def reload():
    loadSite("https://intern.gymnasium-donauwoerth.de/verplan-schueler/heute/schueler_heute.html", "stemmeen",
             "yfNvbqeuTSTPmkCObyaRyWZyHMoaJZZqTRedlXKhtRmwohYobmbGCVFvyXlmKjMFieGTA@")
    loadSite("https://intern.gymnasium-donauwoerth.de/verplan-schueler/morgen/schueler_morgen.html", "stemmeen",
             "yfNvbqeuTSTPmkCObyaRyWZyHMoaJZZqTRedlXKhtRmwohYobmbGCVFvyXlmKjMFieGTA@")

    proc = subprocess.Popen(args=["python3.10", "-u", "./bot.py"], text=True, stdout=sys.stdout, stderr=sys.stderr, start_new_session=False)

    sleep(1800)
    proc.kill()


if __name__ == '__main__':
    print("starting...")
    while True:
        reload()
