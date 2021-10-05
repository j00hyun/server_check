# -*- coding: utf-8 -*-
import os
import logging
import logging.config
from logging import Logger
from http import HTTPStatus
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from . import loader


class LoggerFactory(object):
    def __init__(self):
        self._format_loader = {
            '.yml': loader.YamlLoader,
            '.json': loader.JsonLoader}

    def __str__(self):
        for name in logging.Logger.manager.loggerDict:
            print('logger name:', name, ', handlers:',
                  logging.getLogger(name).handlers)
        return 'Done'

    @property
    def show_loggers(self):
        """
        만들어진 Logger 보기
        Returns:
        """
        return logging.Logger.manager.loggerDict

    def _set_formatter(self, source, level, format):
        """
        handler의 formatter 설정
        Args:
            source (handler): logging 또는 logging.handlers 에서 온 프로세서
            level(int): 등급
            format(str): 포멧 설정
        Return:
            source: 설정된 handler
        """
        source.setLevel(level)
        formatter = logging.Formatter(format)
        source.setFormatter(formatter)
        return source

    def _check_extension(self, path: str):
        support_extension = ['.yml', '.json']
        for extension in support_extension:
            if path.endswith(extension):
                return extension
        raise Exception('Non-Support Format')

    def _check_logging_path_dir(self, content: dict):
        handlers = content["handlers"]
        for name, settings in handlers.items():
            if "filename" in settings.keys():
                pathdir = os.path.dirname(settings["filename"])
                if not os.path.exists(pathdir):
                    os.makedirs(pathdir)

    def load_config(self, path: str) -> None:
        """
        이미 정의된 Logger 설정 파일 불러온 후 초기화
        json과 yaml 형식 지원
        Args:
            path (str): 파일 원본 위치
        Raises:
            Exception: 불러오는데 실패
        """

        try:
            ext = self._check_extension(path)
            content = self._format_loader[ext].load(path)
            # 불러온 yaml 형식에 있는 모든 filename에 경로가 있는지 확인
            self._check_logging_path_dir(content)
            logging.config.dictConfig(content)
        except Exception as err:
            raise Exception('Load Failure :' + repr(err))

    def get_logger(self, name: str) -> Logger:
        return logging.getLogger(name)

    def make_console(self, name, level, format) -> Logger:
        logger = logging.getLogger(name)
        if logging.StreamHandler not in logger.handlers:
            # 미리 설정된 StreamHandler를 logger.handlers에서 만듦
            handler = logging.StreamHandler()
            handler = self._set_formatter(handler, level, format)
            logger.addHandler(handler)
        return logger

    def make_file(self, name, filepath, level, format):
        logger = logging.getLogger(name)
        if logging.FileHandler not in logger.handlers:
            handler = logging.FileHandler(filepath)
            handler = self._set_formatter(handler, level, format)
            logger.addHandler(handler)
        return logger

    def make_rotating_file(self,
                           name,
                           filepath,
                           level,
                           format,
                           max_bytes=128,
                           backup_count=0) -> Logger:
        """
        addHandler를 통해 RotatingFileHandler 생성
        RotatingFileHandler Logger가 이미 구축되어 있는지 판단
        Args:
            max_bytes(int, optional): 파일 최대 쓰기 bytes。
                backup_count 설정이 없다면 같은 파일에 계속 append
                e.g backup = 2, 이때는 original 빼고 제외
            backup_count(int, optional): 입력학 백업파일 수량 e.g backup = 2, original 외, size 가 부족할 때 사용, file.1 과 file.2 생성

            만약 max_bytes 에 backup_count >=1 이라면，해당 파일이 max_bytes 초과했을 때，backup_count 수에 따라 만듦，
            e.g backup_count = 2, max_byte = 18, log가 총 3 건，각각 18 bytes, 총 54 bytes 라면， original을 제외하고，순서대로 file당 max_bytes는 18 bytes
            순서대로 file.1, file.2가 만들어짐

            단，log의 내용이 많고，backup도 부족할 경우, 다시 덮어쓰기를 반복한다.
            e.g backup_count = 2, max_byte = 18, log 총 5 건，각각 18 bytes 총 90 bytes 라면,
            1. 18 bytes -> original
            2. 18 bytes -> file.1
            3. 18 bytes -> file.2
            4. 18 bytes -> backup = 2 이므로, 다시 original에 덮어쓰기
            5. 18 bytes -> file.1

            마지막을 보면， original은  4번째 log, file.1은 5번째, file.2는 3번째 log가 담겼다.
        Returns:
            Logger: logger를 되돌려줌
        """
        logger = logging.getLogger(name)
        if RotatingFileHandler not in logger.handlers:
            handler = RotatingFileHandler(
                filepath,
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding='utf8')
            handler = self._set_formatter(handler, level, format)
            logger.addHandler(handler)
        return logger

    def make_time_rotating_file(self,
                                name,
                                filepath,
                                level,
                                format,
                                backup_count=0,
                                when='s',
                                interval=60) -> Logger:
        """
        파일 형태로 로그를 남길 수 있는 핸들러 중 일정 시간이 되면 자동으로 로그 파일에 날짜가 추가됨
        핸들러는 사용자가 설정한 특정 시간 간격의 디스크 로그 파일 회전을 지원
        addHandler를 통해，TimeRotatingFileHandler를 생성
        TimeRotatingFileHandler Logger가 있는지 판단, 있다면 반환
        Args:
            backup_count(int, optional): 최대 백업할 로그 파일의 개수
            when(string, optional): interval의 유형 지정
                S: 초, M: 분, H: 시, D: 일, W:  W0 - W6 (요일 0=Monday), midnight: 자정
                로그를 저장할 때，%Y-%m-%d_%H-%M-%S 형식으로 저장
            interval(int, optional): 시간 간격，when과 함께 사용
                when = s, interval = 30 라면, 30초 마다 backup_count 에서 허용하는 수 만큼 새 로그 파일을 기록
                when = w， interval = 0 - 6 요일을 나타냄, when = w0 - w6 라면, interval 작동 안함
        Returns:
            Logger: logger 반환
        """
        logger = logging.getLogger(name)
        if TimedRotatingFileHandler not in logger.handlers:
            handler = TimedRotatingFileHandler(
                filepath,
                when=when,
                interval=interval,
                backupCount=backup_count,
                encoding='utf8')
            handler = self._set_formatter(handler, level, format)
            logger.addHandler(handler)
        return logger
