"""All42 bootstrap suites plus all25 storage/related Root under one fixed snapshot, no VM change."""
import pg5148_native_fd_selected as selected


def bootstrap_suites():
    folder=selected.ROOT/'src/schubert-nk-bootstrap/src/test/java'
    result={}
    for path in sorted(folder.rglob('*Test.java')):
        if path.is_symlink():raise ValueError('physical test source only')
        if '@Test' in path.read_text():
            result[path.relative_to(folder).with_suffix('').as_posix().replace('/','.')] = 'bootstrap'
    if len(result)!=42:raise ValueError('actual all42 bootstrap suites')
    return result


def main():
    selected.EXTRA_CHANGED={'bootstrap:dev/codex/schubert/nk/bootstrap/NativeCoveragePrivateFile.class'}
    return selected.main(stem_override='pg5156-native-coverage',version_override='v2',
                         extra_suites=bootstrap_suites())


if __name__=='__main__':raise SystemExit(main())
