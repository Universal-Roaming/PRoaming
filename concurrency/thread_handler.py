import threading
from concurrent.futures import ThreadPoolExecutor


class ThreadHandler:

    __total_thread_count = 0

    def initiate_task_routine(self, is_daemon: bool, target_function):
        thread = threading.Thread(target=target_function, args=())
        thread.daemon = is_daemon
        self.__total_thread_count = self.__total_thread_count + 1
        thread.start()

    def initiate_service_thread_pool(self, thread_count: int) -> ThreadPoolExecutor:
        self.__total_thread_count = self.__total_thread_count + thread_count
        return ThreadPoolExecutor(max_workers=thread_count)
