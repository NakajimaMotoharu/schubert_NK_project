"""Current read/refusal/proof/qualification summaries only. No full image or secret export."""
import inspect
import pg4352_publish_current_partial_preparation as previous


def main():
    raw = inspect.getsource(previous.main)
    start = "['pg4336-current-unknown-read-v1', 'pg4346-current-partial-tools-v1-stage',\n                 'pg4346-current-partial-tools-v1-proof', 'pg4350-current-partial-qualification-v1']"
    slots = ['pg4354-current-reference-delta-v1', 'pg4356-current-pool-witness-v1',
             'pg4366-pool-bound-tools-v1-proof', 'pg4366-pool-bound-tools-v2-stage',
             'pg4366-pool-bound-tools-v3-stage', 'pg4366-pool-bound-tools-v3-proof', 'pg4370-pool-bound-qualification-v1']
    if raw.count(start) != 1:
        raise ValueError('exact bounded summary list first')
    raw = raw.replace(start, repr(slots))
    raw = raw.replace('PG4352-current-partial-preparation-v1', 'PG4372-pool-bound-preparation-v1')
    raw = raw.replace('pg4350-current-partial-qualification-v1/host-tests.log', 'pg4370-pool-bound-qualification-v1/host-tests.log')
    raw = raw.replace('f9600af73555fb002fc98ddd0af0dea4c0e686b6', '6eae971276832c6d0cc9e29fbc18c5090d3cf6ad').replace("'designPR': 138", "'designPR': 139")
    ns = dict(vars(previous))
    exec(compile(raw, '<current bounded receipt publisher>', 'exec'), ns)
    ns['main']()


if __name__ == '__main__':
    main()
