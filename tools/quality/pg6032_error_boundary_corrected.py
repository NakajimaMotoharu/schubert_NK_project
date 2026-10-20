"""New-source necessary965 after BUG1526; preserve original failed6026, never replay it."""
import inspect
import pg6026_error_boundary_selected as previous


def driver_source():
    raw = inspect.getsource(previous.main)
    old = "'pg6026-error-boundary-selected965-v1'"
    if raw.count(old) != 1:
        raise ValueError('one separate new-only corrective965 namespace')
    raw = raw.replace(old, "'pg6032-error-boundary-selected965-v1'", 1)
    compile(raw, '<same approved profile,new corrected source>', 'exec')
    return raw


def main():
    scope = dict(vars(previous))
    exec(compile(driver_source(), '<necessary corrective PT,not refused operation>', 'exec'), scope)
    return scope['main']()


if __name__ == '__main__':
    raise SystemExit(main())
