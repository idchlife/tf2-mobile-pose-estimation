"""Just lightweight wrapper for logging, which can be used later with
some library replacement for actuall logging (if needed)
"""
import os

# Shamelessly taken from https://stackoverflow.com/a/54955094/2739103

os.system("")


class TerminalColors:
  BLACK = "\033[30m"
  RED = "\033[31m"
  GREEN = "\033[32m"
  YELLOW = "\033[33m"
  BLUE = "\033[34m"
  MAGENTA = "\033[35m"
  CYAN = "\033[36m"
  WHITE = "\033[37m"
  UNDERLINE = "\033[4m"
  RESET = "\033[0m"


def log_error(msg):
	print(f"{TerminalColors.RED}{msg}{TerminalColors.RESET}")

def log_warning(msg):
	print(f"{TerminalColors.YELLOW}{msg}{TerminalColors.RESET}")

def log_success(msg):
	print(f"{TerminalColors.GREEN}{msg}{TerminalColors.RESET}")

def log_info(msg):
	print(f"{TerminalColors.CYAN}{msg}{TerminalColors.RESET}")

def log(msg):
	print(msg)
