"""Strict measured-byte contract; explicit larger SQL cap, never partial success."""
def accepted(returncode, size, limit):
    return (type(returncode) is int and returncode==0 and type(size) is int and size>=0
            and type(limit) is int and limit>0 and size<=limit)
