import datetime
import os

class Debug:
    def __init__(self, enable=True, log_to_file=True, log_dir="debug_logs"):
        self.enable = enable
        self.log_to_file = log_to_file
        self.log_dir = log_dir

        if self.log_to_file:
            os.makedirs(log_dir, exist_ok=True)
            self.log_file = os.path.join(log_dir, f"debug_{datetime.date.today()}.log")

    def _write(self, level, color_code, *args, sep=' ', end='\n'):
        if not self.enable:
            return

        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        message = sep.join(map(str, args))

        formatted_console = f"\033[{color_code}m[{timestamp}][{level.upper()}]\033[0m {message}"
        print(formatted_console, end=end)

        if self.log_to_file:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(f"[{timestamp}][{level.upper()}] {message}{end}")

    def debug(self, *args, **kwargs):
        self._write("debug", "92", *args, **kwargs)   # 绿色

    def info(self, *args, **kwargs):
        self._write("info", "94", *args, **kwargs)    # 蓝色

    def warn(self, *args, **kwargs):
        self._write("warn", "93", *args, **kwargs)    # 黄色

    def error(self, *args, **kwargs):
        self._write("error", "91", *args, **kwargs)   # 红色


# 创建全局实例
logger = Debug()

# 快捷函数（你也可以直接用 logger.debug() 这种方式）
debug = logger.debug
info = logger.info
warn = logger.warn
error = logger.error
