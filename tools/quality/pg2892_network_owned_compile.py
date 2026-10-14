"""Actual currenta9 full fifteen-source ownedstop ABI compilation, no Main rebuild."""
import inspect
import pg2710_operation_owned_compile as prior
from pg2890_network_owned_sources import sources,context,SOURCE,TOOLS,bind


def main():
    raw=bind(inspect.getsource(prior.previous.main))
    ns={**prior.previous.__dict__,'sources':sources,'context':context,'SOURCE':SOURCE,'TOOLS':TOOLS}
    exec(compile(raw,'<complete actual a9 ownedstop ABI>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
