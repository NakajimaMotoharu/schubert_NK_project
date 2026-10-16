"""SSC292 exact current handoff, five unissued stops and independent post; no replay."""
import inspect
import pg4188_exact_partial_recover as previous
import pg4346_current_partial_coordinator as staged
import pg4338_current_partial_sources as sources

OUT = previous.W / 'pg4348-current-partial-recover-v1'
DESIGN_MAIN = 'f9600af73555fb002fc98ddd0af0dea4c0e686b6'


def original_receipt(receipt):
    if type(receipt) is not dict or type(receipt.get('actualExit')) is not int:
        raise ValueError('original exact transport receipt required')
    if not 1 <= receipt['actualExit'] <= 255:
        raise ValueError('actual nonzero SSH failure remains failure, never normal')
    if receipt.get('source') != '7bb25aa9c8a1d1af04525ec51beb1c4b7268aa9e' or receipt.get('payloadSha256') != '87ef52f80156a0c83ae1451a08f1b20508797c6072c9b86263af90b163569182':
        raise ValueError('same original failed artifact/source required')
    if receipt.get('oldParentNormal') is not False or receipt.get('formalAccepted') is not False:
        raise ValueError('original UNKNOWN not normalized')
    return receipt


def bootstrap(name, hashes):
    ns = {**vars(previous), 'GUEST': staged.GUEST}
    exec(compile(inspect.getsource(previous.bootstrap), '<current staged envelope>', 'exec'), ns)
    return ns['bootstrap'](name, hashes)


def remote_args(name, hashes, mode=None):
    ns = {**vars(previous), 'bootstrap': bootstrap}
    exec(compile(inspect.getsource(previous.remote_args), '<current phase transport>', 'exec'), ns)
    return ns['remote_args'](name, hashes, mode)


def main_source():
    raw = inspect.getsource(previous.main)
    replacements = [
        ('SSC288', 'SSC292'), ('PG4152', 'PG4328'),
        ('pg4152-exact-failed-done-recover-v1', 'pg4316-current-failed-dispatch-v1-recover'),
        ("recover_result['old4152Normal']", "recover_result['original58917Normal']"),
        ("'old4152Exit':143", "'original58917Exit':receipt['actualExit']"),
        ("'old4152Normal':False", "'original58917Normal':False"),
    ]
    for old, new in replacements:
        if old not in raw:
            raise ValueError('complete current operational binding required: ' + old)
        raw = raw.replace(old, new)
    return raw


def main():
    # Original outcome is written by the unmodified original4328 wrapper after
    # its SSH terminates. Do not fabricate it from guest signal expectations.
    if (OUT / 'start.safe.json').exists():
        raise ValueError('one original current partial job only; never replay')
    raw = main_source()
    ns = {**vars(previous), 'OUT': OUT, 'DESIGN_MAIN': DESIGN_MAIN,
          'TOOLS': staged.SLOT, 'GUEST': staged.GUEST, 'owner': staged.owner,
          'files': sources.files, 'remote_args': remote_args, 'original_receipt': original_receipt}
    # previous.private captures its defining globals, so bind its OUT explicitly.
    exec(compile(inspect.getsource(previous.private), '<current durable receipt>', 'exec'), ns)
    exec(compile(raw, '<current one-shot partial handoff>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
