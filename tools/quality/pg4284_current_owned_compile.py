"""Compile all generated owned-stop ABI only after genuine current composite/projection."""
import inspect
import pg4044_literal_invariant_owned_compile as previous
import pg4282_current_owned_sources as role


def main():
    ns={**vars(previous),'role':role}
    exec(compile(inspect.getsource(previous.main),'<actual new owned ABI composer>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
