"""Six real-FD Transfer tests including root security and calendar boundaries."""
import inspect
import pg3046_transfer_counter_selected as previous


def server():
    raw = previous.server().replace('PG3046', 'PG3048')
    raw = raw.replace("'nullInvalidIdentityAndRootModeRefuseWithoutMutation'", "'transfer3048001RootIdentityAclAndReadOnlyRefuseBeforeDeletingAnyByte','transfer3048002CalendarLowerUpperBoundaryAndYearZeroAreIndependent','nullInvalidIdentityAndRootModeRefuseWithoutMutation'")
    return raw.replace('dev/codex/schubert/nk/batch/file/TransferCleanup$Outcome', 'dev/codex/schubert/nk/batch/file/TransferCleanup')


def main():
    raw = inspect.getsource(previous.main).replace('pg3046-transfer-counter-selected-v1', 'pg3048-transfer-security-selected-v1').replace('PG3046-candidate-v1', 'PG3048-candidate-v1')
    ns = {**previous.__dict__, 'server': server}
    exec(compile(raw, '<six current Transfer security input>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
