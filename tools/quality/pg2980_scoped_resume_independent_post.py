"""BUG1262: isolate whole inserted oracle, explicitly export only three bindings."""
import types
import pg2978_current_resume_post_exports as previous

SLOT = 'pg2980-scoped-resume-independent-post-v1'


def payload(seals):
    raw = previous.payload(seals).replace(previous.SLOT, SLOT).replace('PG2978', 'PG2980')
    marker = "import sys\nsys.path.insert(0,'/var/lib/pgpt-s1-preservation/pg2970-current-cold-resume-tools-v1')\n"
    if raw.count(marker) != 1:
        raise ValueError('one complete inserted oracle scope required')
    start = raw.index(marker)
    end = raw.index('\nbus = dbus.SystemBus(private=True)\n', start)
    block = raw[start:end]
    scoped = 'def independent_resume_delta(after):\n' + '\n'.join('    ' + line if line else '' for line in block.splitlines()) + '\n    return after,fresh_private,exec_record\nafter,fresh_private,exec_record=independent_resume_delta(after)\n'
    raw = raw[:start] + scoped + raw[end:]
    compile(raw, '<whole independent local scope>', 'exec')
    return raw


def entry():
    fn = previous.entry()
    return types.FunctionType(fn.__code__, {**fn.__globals__, 'SLOT': SLOT, 'payload': payload}, 'scoped_current_resume_post')


if __name__ == '__main__':
    raise SystemExit(entry()())
