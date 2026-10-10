"""Metadata-only lifetime scope; never grants startup/DB/M-A ownership."""
def with_references(manager,bus,names,body):
    held=[]
    try:
        for name in names:
            manager.LoadUnit(name);manager.RefUnit(name);held.append(name)
        return body()
    finally:
        failures=[]
        for name in reversed(held):
            try:manager.UnrefUnit(name)
            except Exception as failure:failures.append(failure)
        try:bus.close()
        except Exception as failure:failures.append(failure)
        if failures:raise failures[0]
