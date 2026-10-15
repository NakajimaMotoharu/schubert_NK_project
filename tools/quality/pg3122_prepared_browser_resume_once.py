"""One reserved new activation; consume full PG3106 post and preserve native16."""
import inspect
import json
import pg2984_current_resume_once as previous
import pg3106_full_native_resume_post as post
from pg3120_prepared_browser_observer import namespace, SOURCE, BOM
from pg1446_current_cold_stage import W
from pg2360_current_completed_resume_once import body as proven_body

SLOT = 'pg3122-prepared-browser-resume-once-v1'


def body():
    proof = json.loads((W / post.SLOT / 'manifest.safe.json').read_bytes())
    if proof['actualExit'] != 0 or not proof['normalResumePrepared'] or proof['productionSource'] != SOURCE:
        raise ValueError('complete current finite preparation required')
    raw = proven_body()
    replacements = [
        ('pg2358', 'pg3120'), ('pg2360-current-completed-resume-once-v1', SLOT),
        ('3b7f3567b54f91f3a9dbeb859e8dd77e8353a2c8', SOURCE),
        ('62213f357c9dab3b00b557549426b091a03ace6557a62f4410999a02028a332c', BOM),
        ('PG2126', 'PG2802'),
        ('91f5484b-9702-4c7c-97f3-dd5110a853f9', '0dc63b79-3f9a-450c-b2a6-56f86272d272'),
        ('6873c5eb138bbd3dbd6a8e00398738b837dca149325db0ff555d0901bd1b10ec', proof['preparedAfterSha256']),
        ('9bf72ad074cbe798ef6082d31f25be89fe7cf3e3d31be484a997ce4b0b82c955', proof['nativeCanonicalSha256']),
        ("accepted_before={**after,'configuration':dict(current_view)}", 'accepted_before=after'),
        ('require(len(records)==10)', 'require(len(records)==16)'),
    ]
    for old, new in replacements:
        if old not in raw:
            raise ValueError('missing exact reserved-start binding: ' + old[:40])
        raw = raw.replace(old, new)
    return raw


def payload(hashes):
    ns = {**previous.__dict__, 'post': post, 'body': body}
    exec(compile(inspect.getsource(previous.payload), '<complete all11 native16 Root-before>', 'exec'), ns)
    return ns['payload'](hashes)


def main():
    from pg3138_browser_cohort_ready import require_ready
    require_ready()
    raw = inspect.getsource(previous.main).replace('pg2982', 'pg3120')
    ns = {**previous.__dict__, 'post': post, 'namespace': namespace, 'payload': payload, 'SLOT': SLOT}
    exec(compile(raw, '<single new browser-cohort Root>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
