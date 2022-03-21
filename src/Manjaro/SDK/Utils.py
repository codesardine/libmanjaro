import re
import threading
import multiprocessing


def glib_date_to_string(date):
    try:
        d = date.format("%A %B %e %H:%M")
    except AttributeError:
        d = ""
    return d


def strip_html(html):
        regex = re.compile('<.*?>')
        text = re.sub(regex, '', html)
        return text


def convert_bytes_to_human(bytes):
        if bytes >= 1073741824:
            v = bytes / 1024/1024/1024
            size = f"{round(v, 1) } GB"
        elif bytes >= 1048576:
            v = bytes / 1024/1024
            size = f"{round(v, 1) } MB"
        elif bytes >= 1024:
            v = bytes / 1024
            size = f"{round(v, 1) } KB"
        else:
            size = f"{round(bytes, 1) } Bytes"
        return f"{size}"


def _async(func):
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        thread.daemon = True
        thread.start()
        return thread
    return wrapper


def idle(func):
    def wrapper(*args):
        GLib.idle_add(func, *args)
    return wrapper


def process(func):
    def wrapper(*args):
        proc = multiprocessing.Process(target=func(args))
        proc.start()
        proc.join()  
        return proc      
    return wrapper
