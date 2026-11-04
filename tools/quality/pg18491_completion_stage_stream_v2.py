"""Bounded in-memory public planning transfer. No files are written by this tool."""
import contextlib
import hashlib
import io
import json
import sys
import termios
import pg18490_completion_stage_reconciliation_v1 as original

MAXIMUM = 24000


def part(files, request):
    name, offset = request['file'], request['offset']
    if name not in files or type(offset) is not int or not 0 <= offset <= len(files[name]):
        raise ValueError('known planning file and bounded integer offset required')
    value = files[name]
    return dict(file=name, offset=offset, text=value[offset:offset + MAXIMUM],
                nextOffset=min(offset + MAXIMUM, len(value)), total=len(value))


def main():
    # Disable echo on this tool's own PTY only; never inspect external processes.
    if sys.stdin.isatty():
        attrs = termios.tcgetattr(sys.stdin)
        attrs[3] &= ~termios.ECHO
        termios.tcsetattr(sys.stdin, termios.TCSANOW, attrs)
    draft = io.StringIO()
    with contextlib.redirect_stdout(draft):
        original.main()
    files = {name: json.dumps(value, ensure_ascii=False, separators=(',', ':')) + '\n'
             for name, value in json.loads(draft.getvalue()).items()}
    for bad in [dict(file='../private', offset=0), dict(file=next(iter(files)), offset=-1),
                dict(file=next(iter(files)), offset=True),
                dict(file=next(iter(files)), offset=len(next(iter(files.values()))) + 1)]:
        try:
            part(files, bad)
        except ValueError:
            pass
        else:
            raise ValueError('transfer boundary accepted')
    print(json.dumps(dict(files=[dict(name=name, total=len(value),
        sha256=hashlib.sha256(value.encode()).hexdigest()) for name, value in files.items()],
        transportBoundaryVectors=4, targetProductExecuted=False)), flush=True)
    for line in sys.stdin:
        if line.strip() == 'DONE':
            print(json.dumps(dict(transferClosed=True, actualExit=0)), flush=True)
            return
        print(json.dumps(part(files, json.loads(line)), ensure_ascii=False), flush=True)
    raise ValueError('explicit transfer completion required')


if __name__ == '__main__':
    main()
