"""Host complete fifteen-source owned stop ABI after actual current whole seal."""
import inspect
import pg2555_strict_current_owned_compile as previous
from pg2708_operation_owned_sources import sources,context,SOURCE,TOOLS,bind


def main():
    raw=bind(inspect.getsource(previous.main))
    ns={**previous.__dict__,'sources':sources,'context':context,'SOURCE':SOURCE,'TOOLS':TOOLS}
    exec(compile(raw,'<new complete owned ABI>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
