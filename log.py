import logging
import logging.handlers

green = "\033[92m"
bold = "\033[1m"
blue = "\033[94m"
end = "\033[0m"

logger = logging.getLogger("logger")

stream_handler = logging.StreamHandler()
file_handler = logging.FileHandler(filename="bs.log", encoding="utf-8")

logger.setLevel(logging.DEBUG)
stream_handler.setLevel(logging.INFO)
file_handler.setLevel(logging.DEBUG)

stream_formatter = logging.Formatter(f"{blue}[%(asctime)s]{end} {bold}%(levelname)s{end} {green}%(message)s{end}")
file_formatter = logging.Formatter(f"[%(asctime)s] %(levelname)s %(message)s")

stream_handler.setFormatter(stream_formatter)
file_handler.setFormatter(file_formatter)

logger.addHandler(stream_handler)
logger.addHandler(file_handler)

if __name__ == '__main__':
    logger.debug("debug")
    logger.info("info")
    logger.warning("warning")
    logger.error("error")
    logger.critical("critical")