"""Freeze all current fifteen-file owned-stop ABI phases before VM ownership."""
import inspect
import pg2031_fresh_normal_warning_stop_compile as previous
from pg2090_current_newrun_owned_stop_sources import sources,context,SOURCE,TOOLS


def main():
    raw=inspect.getsource(previous.main).replace('Pg2030','Pg2090').replace('pg2031','pg2091')
    ns={**previous.__dict__,'sources':sources,'context':context,'SOURCE':SOURCE,'TOOLS':TOOLS}
    exec(compile(raw,'<actual current newrun owned ABI>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
