"""Actual whole emitted Java/Python ABI before any current resume stop."""
import inspect
import pg3492_outbox_owned_compile as template
import pg3876_current_resume_owned_sources as role


def main():
    raw=role.bind(inspect.getsource(template.old.previous.main))
    values={**template.old.previous.__dict__,'sources':role.sources,'context':role.context,'SOURCE':role.SOURCE,'TOOLS':role.TOOLS}
    exec(compile(raw,'<current resume whole emitted owned ABI>','exec'),values);return values['main']()


if __name__=='__main__':raise SystemExit(main())
