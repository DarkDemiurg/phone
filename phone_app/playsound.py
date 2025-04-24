import os
import subprocess
import threading
from queue import Empty, Queue
from time import sleep, time

from log import logger
from speaker import LedOff, LedOn, SpeakerOff, SpeakerOn

# gplaysound -f /usr/share/sound/ring.mp3 -d pcm_int -r 3


class PlaySound:
    def __init__(self, command: str = "gplaysound", args=None, capture_output=True):
        self.command = [command] if isinstance(command, str) else command
        if args:
            self.command += args
        self.process = None
        self.capture_output = capture_output
        self.output_queue: Queue = Queue()
        self._output_threads: list = []

    def start(self):
        """Запуск внешнего процесса"""
        if self.is_running():
            logger.warning("Процесс уже запущен")
            return False

        try:
            os.system("killall -9 gplaysound")
            sleep(0.5)
            LedOn()
            SpeakerOn()

            stdout = subprocess.PIPE if self.capture_output else subprocess.DEVNULL
            stderr = subprocess.PIPE if self.capture_output else subprocess.DEVNULL

            self.process = subprocess.Popen(
                self.command,
                stdout=stdout,
                stderr=stderr,
                text=True,
                bufsize=1,
                universal_newlines=True,
            )

            if self.capture_output:
                self._start_output_thread("stdout")
                self._start_output_thread("stderr")

            logger.info(f"Процесс запущен [PID: {self.process.pid}] {self.command=}")

            return True
        except Exception as e:
            logger.error(f"Ошибка запуска: {str(e)}")
            return False

    def _start_output_thread(self, stream_name):
        """Запуск потока для чтения вывода"""

        def reader():
            stream = getattr(self.process, stream_name)
            for line in iter(stream.readline, ""):
                self.output_queue.put((stream_name, line.strip()))
            stream.close()

        thread = threading.Thread(target=reader, daemon=True)
        thread.start()
        self._output_threads.append(thread)

    def get_output(self, timeout=0.1):
        """Получение накопленного вывода"""
        outputs = {"stdout": [], "stderr": []}
        while True:
            try:
                stream, line = self.output_queue.get(timeout=timeout)
                outputs[stream].append(line)
            except Empty:
                break
        return outputs

    def get_output_lines(self):
        """Генератор для получения вывода в реальном времени"""
        while self.is_running() or not self.output_queue.empty():
            try:
                yield self.output_queue.get_nowait()
            except Empty:
                pass

    def terminate(self, speaker_off=True):
        """Корректное завершение процесса"""
        if not self.is_running():
            logger.warning("Процесс не запущен")
            return False

        try:
            if speaker_off:
                SpeakerOff()
            LedOff()
            self.process.terminate()
            logger.info("Сигнал завершения отправлен")
            return True
        except Exception as e:
            logger.error(f"Ошибка завершения: {str(e)}")
            return False

    def kill(self, speaker_off=True):
        """Принудительное завершение процесса"""
        if not self.is_running():
            logger.warning("Процесс не запущен")
            return False

        try:
            if speaker_off:
                SpeakerOff()
            LedOff()
            self.process.kill()
            logger.info("Процесс принудительно завершён")
            os.system("killall -9 gplaysound")
            return True
        except Exception as e:
            logger.error(f"Ошибка принудительного завершения: {str(e)}")
            return False

    def is_running(self):
        """Проверка активности процесса"""
        return self.process and (self.process.poll() is None)

    def wait(self, timeout=None):
        """Ожидание завершения процесса"""
        if not self.process:
            return False
        try:
            self.process.wait(timeout=timeout)
            return True
        except subprocess.TimeoutExpired:
            logger.warning("Таймаут ожидания истёк")
            return False

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.is_running():
            SpeakerOff()
            self.terminate()
            time.sleep(1)
            if self.is_running():
                self.kill()
        self.process = None

    def __del__(self):
        self.__exit__(None, None, None)
