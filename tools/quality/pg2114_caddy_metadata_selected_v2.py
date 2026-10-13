"""Corrected explicit four-module reactor; preserve failed PG2112, no VM operations."""
import inspect
import pg2112_caddy_metadata_selected as old

def server():
    raw=old.SERVER.replace('PG2112','PG2114').replace("'-am',",'')
    compile(raw,'<explicit four module Caddy selected>','exec')
    return raw

def main():
    raw=inspect.getsource(old.main).replace('PG2112','PG2114').replace('pg2112','pg2114')
    ns={**old.__dict__,'SERVER':server()}
    exec(compile(raw,'<new-only current explicit reactor entry>','exec'),ns)
    return ns['main']()

if __name__=='__main__':raise SystemExit(main())
