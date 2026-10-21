"""Read genuine original4054 only, with one exact independently reviewed branchless owner."""
import inspect
import json
import types
import pg6198_original4024_artifacts as prior
from pg6414_web_frame_pending_qualification import original_source
from pg6402_web_frame_order import KEY

OLD = 'c34159083bfec296fd929ec9b2fbdbb80831c05c'
ORDER_SHA = 'bb031e69484777959914caf0dc499a34464b063d86377b4426b56d05ae3d1cac'


def definitions():
    scope = {**vars(prior), 'OLD': OLD, 'original_source': original_source}
    for name in ('new_case_identities', 'main'):
        raw = inspect.getsource(getattr(prior, name))
        for before, after in (
            ('!=36', '!=2'), ('exact36', 'exact2'), ('len(owners)!=13', 'len(owners)!=1'), ('exact13', 'exact1'),
            ('pg6196-management-ownership-six-v1', 'pg6408-web-frame-six-v1'), ('PG6196-six-v1', 'PG6408-six-v1'), ('PG6196', 'PG6408'),
            ('PG6118-current3988-cases', 'PG6386-current4052-cases'),
            ('c9b2daa72b7f1fd2fbf73c545103890592ef1cbeacfa0ae4050d1b56e692fd23', '5b42051bf7ca435c44e3f7caa2fb0fca245faae9c32c3fda4b508ee40a4314b4'),
            ('fcc0ae3b3056dafed7e2cc1c0b076aaab5e8cda7c8f6f86a58da9e97c70aea47', '88be94dae853d88c108c45dc4ad6f83251c870188b5b3247b8092aaa3f2b1314'),
            ('PG6193-management-primary-qualification-v2', 'PG6414-web-frame-pending-qualification-v1'),
            ('pg6193-management-primary-qualification-v2', 'pg6414-web-frame-pending-qualification-v1'),
            ('(60,20)', '(26,12)'), ('source60', 'source26'), ('[4024,605,1667]', '[4054,610,1667]'),
            ('pg6198-original4024-artifacts-v1', 'pg6410-original4054-artifacts-v1'),
            ('PG6198-original4024-v1', 'PG6410-original4054-v1'), ('PG6408-current4024-cases', 'PG6408-current4054-cases')):
            raw = raw.replace(before, after)
        exec(compile(raw, '<original4054 '+name+'>', 'exec'), scope)
    return scope


def new_case_identities(source): return definitions()['new_case_identities'](source)


def branchless_proof(source):
    path = prior.BASE/'PG6402-web-frame-order-v1/manifest.json'
    if ORDER_SHA is None or prior.sha(path) != ORDER_SHA:
        raise ValueError('pin final original26 JVM ownership/branch proof first')
    value = json.loads(path.read_bytes())
    if value['actualExit'] != 0 or value['source'] != source or not value['ownershipReviewed'] or set(value['branchlessOwnerProofs']) != {KEY}:
        raise ValueError('exact one source/class instruction applicability proof')
    return value['branchlessOwnerProofs']


def main():
    function = definitions()['main']
    def collect(data, path, slot, remote, public_name):
        data['branchlessOwnerProofs'] = branchless_proof(data['source'])
        return prior.reader.collect(data, path, slot, remote, public_name)
    namespace = {**function.__globals__, 'reader': types.SimpleNamespace(
        collect=collect, production_source_inputs=prior.reader.production_source_inputs)}
    return types.FunctionType(function.__code__, namespace)()


if __name__ == '__main__':
    main()
