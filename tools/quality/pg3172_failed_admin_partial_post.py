"""Independent three-Login/one-UDT prefix, reusing only proved readonly capture mechanics."""
import inspect
import pg3162_failed_menu_partial_post as previous
from pg3170_auth_admin_prefix_oracle import qualify

SLOT = 'pg3172-failed-admin-auth-read-post-v1'


def main():
    raw = inspect.getsource(previous.main).replace('pg3140-browser-business-actual-v1', 'pg3164-browser-business-actual-v2').replace("manifest['passedCases'] != 1", "manifest['passedCases'] != 3")
    ns = {**previous.__dict__, 'SLOT': SLOT, 'qualify': qualify}
    exec(compile(raw, '<actual readonly failed ADMIN cohort prefix>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
