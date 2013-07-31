def total_seconds(delta):
    """
    Backport timedelta.total_seconds() from Python 2.7
    """
    return delta.days * 86400.0 + delta.seconds + delta.microseconds * 1e-6
