"""Supplemental TEXT checks for hash-pinned, already-reviewed JDBC fixture sources; never permissions."""
from pure_jdbc_fixture_scope_v1 import FORBIDDEN

def eligible(texts,required):
    if not isinstance(texts,dict) or not isinstance(required,dict) or not 1<=len(required)<=8 or set(texts)!=set(required):
        return False
    if any(not isinstance(n,str) or not n or not isinstance(v,str) for n,v in texts.items()):
        return False
    if any(not isinstance(v,(tuple,list)) or not v or any(not isinstance(s,str) or not s for s in v) for v in required.values()):
        return False
    return not any(term in text for text in texts.values() for term in FORBIDDEN) and all(all(s in texts[n] for s in terms) for n,terms in required.items())
