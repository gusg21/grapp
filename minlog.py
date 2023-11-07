MINLOG_APP_NAME = ""
MINLOG_OLD_PRINT = print

def set_minlog_app_name(name):
    MINLOG_APP_NAME = name

def log(text, level="info"):
    MINLOG_OLD_PRINT(f"[{MINLOG_APP_NAME}] [{level}] {text}")

print = log