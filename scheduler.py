import time
import multiprocessing
from loguru import logger
from conf.settings import CYCLE_TESTER, ENABLE_TESTER, CYCLE_GETTER, ENABLE_GETTER, ENABLE_SERVER

from proxypool.processors.getter import Getter
from proxypool.processors.tester import Tester
from server.app import Server

tester_process, getter_process, server_process = None, None, None


class Scheduler(object):
    def run_tester(self, cycle=CYCLE_TESTER):
        if not ENABLE_TESTER:
            logger.info("Tester not enabled, exit")
            return
        tester = Tester()
        loop = 0
        while True:
            logger.debug(f"Tester Loop({loop}) start...")
            tester.run()
            loop += 1
            time.sleep(cycle)

    def run_getter(self, cycle=CYCLE_GETTER):
        if not ENABLE_GETTER:
            logger.info("Getter not enabled, exit")
            return
        getter = Getter()
        loop = 0
        while True:
            logger.debug(f"Getter Loop({loop}) start...")
            getter.run()
            loop += 1
            time.sleep(cycle)

    def run_server(self):
        Server().run()

    def run(self):
        global tester_process, getter_process, server_process
        try:
            if ENABLE_TESTER:
                tester_process = multiprocessing.Process(target=self.run_tester)
                logger.info(f"start tester, Pid({tester_process.pid})...")
                tester_process.start()

            if ENABLE_GETTER:
                getter_process = multiprocessing.Process(target=self.run_getter)
                logger.info(f"start getter, Pid({getter_process.pid})...")
                getter_process.start()

            if ENABLE_SERVER:
                server_process = multiprocessing.Process(target=self.run_server)
                logger.info(f"start server, Pid({server_process.pid})...")
                server_process.start()

            tester_process and tester_process.join()
            getter_process and getter_process.join()
            server_process and server_process.join()

        except KeyboardInterrupt:
            logger.info('received keyboard interrupt signal')
            tester_process and tester_process.terminate()
            getter_process and getter_process.terminate()
            server_process and server_process.terminate()
        finally:
            # must call join method before calling is_alive
            tester_process and tester_process.join()
            getter_process and getter_process.join()
            server_process and server_process.join()
            logger.info(
                f'tester is {"alive" if tester_process.is_alive() else "dead"}')
            logger.info(
                f'getter is {"alive" if getter_process.is_alive() else "dead"}')
            logger.info(
                f'server is {"alive" if server_process.is_alive() else "dead"}')
            logger.info('proxy terminated')


