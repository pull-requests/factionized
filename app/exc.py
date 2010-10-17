class FactionizeError(Exception):
    # base exception for the factionize code
    pass

class NoAvailableGameSlotsError(FactionizeError):
    pass

class FactionizeTaskException(FactionizeError):
    # base exception of task level errors
    pass


