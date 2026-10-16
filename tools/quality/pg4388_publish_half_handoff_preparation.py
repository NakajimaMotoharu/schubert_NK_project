"""Publish only safe exact remaining-owner read/proof/qualification summaries."""
import inspect
import pg4352_publish_current_partial_preparation as previous


def main():
    raw = inspect.getsource(previous.main)
    start = "['pg4336-current-unknown-read-v1', 'pg4346-current-partial-tools-v1-stage',\n                 'pg4346-current-partial-tools-v1-proof', 'pg4350-current-partial-qualification-v1']"
    slots = ['pg4374-current-half-handoff-read-v1', 'pg4376-scoped-half-handoff-read-v1',
             'pg4382-half-handoff-tools-v1-stage', 'pg4382-half-handoff-tools-v1-proof', 'pg4386-half-handoff-qualification-v1']
    if raw.count(start) != 1: raise ValueError('exact summary list required')
    raw = raw.replace(start, repr(slots)).replace('PG4352-current-partial-preparation-v1', 'PG4388-half-handoff-preparation-v1')
    raw = raw.replace('pg4350-current-partial-qualification-v1/host-tests.log', 'pg4386-half-handoff-qualification-v1/host-tests.log')
    raw = raw.replace('f9600af73555fb002fc98ddd0af0dea4c0e686b6', 'd6c8b23fdcec49e6cc086a0dd435a895b2bf2ce9').replace("'designPR': 138", "'designPR': 140")
    ns = dict(vars(previous)); exec(compile(raw, '<remaining-owner public receipt publisher>', 'exec'), ns); ns['main']()


if __name__ == '__main__':
    main()
