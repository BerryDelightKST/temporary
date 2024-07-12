import time
from time import sleep
from threading import Thread
import queue

from server import run_server, initialize_database


def main():
    # initialize the database
    initialize_database() # TODO: make this only run once
    # start the dashboard
    run_server()


if __name__ == '__main__':
    main()