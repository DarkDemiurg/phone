import subprocess
from time import time

from log import logger
from speaker import SpeakerOff, SpeakerOn

# gplaysound -f /usr/share/sound/ring.mp3 -d pcm_int -r 3


class PlaySound:
    def __init__(
        self,
        command: str = "gplaysound",
        args=["-f", "/usr/share/sound/ring.mp3", "-d", "pcm_int", "-r", "10"],
    ):
        self.command = [command] if isinstance(command, str) else command
        if args:
            self.command += args
        self.process = None
        self.logger = logger

    def start(self):
        """Запуск внешнего процесса"""
        if self.is_running():
            self.logger.warning("Процесс уже запущен")
            return False

        try:
            SpeakerOn()
            self.process = subprocess.Popen(
                self.command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            self.logger.info(f"Процесс запущен [PID: {self.process.pid}]")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка запуска: {str(e)}")
            return False

    def terminate(self):
        """Корректное завершение процесса"""
        if not self.is_running():
            self.logger.warning("Процесс не запущен")
            return False

        try:
            SpeakerOff()
            self.process.terminate()
            self.logger.info("Сигнал завершения отправлен")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка завершения: {str(e)}")
            return False

    def kill(self):
        """Принудительное завершение процесса"""
        if not self.is_running():
            self.logger.warning("Процесс не запущен")
            return False

        try:
            SpeakerOff()
            self.process.kill()
            self.logger.info("Процесс принудительно завершён")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка принудительного завершения: {str(e)}")
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
            self.logger.warning("Таймаут ожидания истёк")
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
