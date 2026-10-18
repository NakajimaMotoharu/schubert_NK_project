"""All42 bootstrap suites plus all25 storage/related Root under one fixed snapshot, no VM change."""
import pg5148_native_fd_selected as selected

EXTRA_BOOTSTRAP_SUITES=set()


def validate_inventory(result,extra):
    if len(result)!=42+len(extra) or not extra<=result.keys():
        raise ValueError('all42 original bootstrap suites plus explicitly registered new suites required')
    return result


def bootstrap_suites():
    folder=selected.ROOT/'src/schubert-nk-bootstrap/src/test/java'
    result={}
    for path in sorted(folder.rglob('*Test.java')):
        if path.is_symlink():raise ValueError('physical test source only')
        if '@Test' in path.read_text():
            result[path.relative_to(folder).with_suffix('').as_posix().replace('/','.')] = 'bootstrap'
    return validate_inventory(result,EXTRA_BOOTSTRAP_SUITES)


def main():
    selected.EXTRA_CHANGED={'bootstrap:dev/codex/schubert/nk/bootstrap/NativeCoveragePrivateFile.class'}
    return selected.main(stem_override='pg5156-native-coverage',version_override='v2',
                         extra_suites=bootstrap_suites())


if __name__=='__main__':raise SystemExit(main())
