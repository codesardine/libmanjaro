def glib_date_to_string(date):
    try:
        d = date.format("%A %B %e %H:%M")
    except AttributeError:
        d = ""
    return d
