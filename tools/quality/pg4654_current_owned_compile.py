"""Compile all generated normal owned-stop tools against current signed JAR ABI."""
import inspect
import pg4044_literal_invariant_owned_compile as previous
import pg4652_current_owned_sources as role


def main():
    ns={**vars(previous),'role':role}
    exec(compile(inspect.getsource(previous.main),'<current normal stop ABI graph>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
