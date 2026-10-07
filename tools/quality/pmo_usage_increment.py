"""Execution-owned, forward-only export of numeric Codex usage metadata.

Never exports conversation text. Initialize at EOF, then poll at work checkpoints.
The monitor reads only the sanitized output, never the private source stream.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import uuid
from datetime import datetime
from zoneinfo import ZoneInfo

DEFAULT_OUTPUT = Path('/home/mini/codex/project1/work/PMO/pgpt-execution-metrics')
MAX_POLL_BYTES = 16 * 1024 * 1024


def now():
    return datetime.now(ZoneInfo('Asia/Tokyo')).isoformat(timespec='seconds')


def normalize(record):
    """Select the explicit per-response usage record; no cumulative fallbacks."""
    payload = record.get('payload', {})
    if not isinstance(payload, dict) or payload.get('type') != 'token_usage_record':
        return None
    usage = payload.get('usage')
    response_id = payload.get('response_id')
    if not isinstance(usage, dict) or not isinstance(response_id, str) or not response_id:
        raise ValueError('USAGE_SCHEMA_UNKNOWN')
    keys = ['input_tokens', 'cached_input_tokens', 'output_tokens', 'reasoning_output_tokens']
    values = {k: usage.get(k) for k in keys}
    if any(type(v) is not int or v < 0 for v in values.values()):
        raise ValueError('USAGE_COUNTER_MISSING_OR_INVALID')
    if values['cached_input_tokens'] > values['input_tokens'] or values['reasoning_output_tokens'] > values['output_tokens']:
        raise ValueError('USAGE_SUBSET_INVALID')
    timestamp = record.get('timestamp')
    if not isinstance(timestamp, str):
        raise ValueError('USAGE_TIMESTAMP_MISSING')
    datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
    digest = hashlib.sha256(response_id.encode()).hexdigest()
    return {'responseKey': digest, 'recordedAt': timestamp, **values,
            'N': values['input_tokens'] - values['cached_input_tokens'] + values['output_tokens'],
            'T': values['input_tokens'] + values['output_tokens']}


def scan(path, offset, seen):
    """Read only newly appended complete lines; preserve incomplete tail offset."""
    with path.open('rb') as handle:
        handle.seek(offset)
        block = handle.read(MAX_POLL_BYTES)
    complete_end = block.rfind(b'\n') + 1
    complete = block[:complete_end]
    rows, issues = [], []
    for line in complete.splitlines():
        if b'"token_usage_record"' not in line:
            continue
        try:
            parsed = normalize(json.loads(line))
            if parsed is None:
                continue
            key = parsed['responseKey']
            counters = [parsed[k] for k in ['input_tokens', 'cached_input_tokens', 'output_tokens', 'reasoning_output_tokens']]
            if key in seen:
                if seen[key] != counters:
                    issues.append('CONFLICTING_RESPONSE_USAGE')
                continue
            seen[key] = counters
            rows.append(parsed)
        except (ValueError, TypeError, KeyError):
            issues.append('UNREADABLE_OR_UNKNOWN_USAGE_METADATA')
    end = offset + complete_end
    return end, rows, sorted(set(issues)), path.stat().st_size > end


def atomic_save(path, data):
    temp = path.with_suffix('.tmp')
    with temp.open('w') as handle:
        json.dump(data, handle, ensure_ascii=False)
        handle.write('\n'); handle.flush(); os.fsync(handle.fileno())
    temp.replace(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['init', 'poll'])
    parser.add_argument('--thread-id', required=True)
    parser.add_argument('--role', required=True, choices=['PGPT', 'REVIEW', 'PMO'])
    parser.add_argument('--output-dir', type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    thread_id = str(uuid.UUID(args.thread_id))
    destination = args.output_dir.resolve()
    destination.mkdir(parents=True, exist_ok=True)
    cursor_path = destination / f'usage-state-{args.role}-{thread_id}.json'
    # Only discover the explicitly supplied thread by filename, never its history.
    matches = list((Path.home() / '.codex/sessions').glob(f'**/*{thread_id}.jsonl'))
    state = json.loads(cursor_path.read_text()) if cursor_path.exists() else None
    if args.mode == 'init' and state is not None:
        print(json.dumps({'status': 'EXISTING_CURSOR_PRESERVED', 'role': args.role}))
        return
    timestamp = now()
    if len(matches) != 1:
        result = {'eventType': 'USAGE_POLL', 'measurementId': str(uuid.uuid4()), 'timeJST': timestamp,
                  'role': args.role, 'threadId': thread_id, 'status': 'USAGE_SOURCE_UNAVAILABLE',
                  'N': None, 'T': None, 'recordCount': 0, 'coverage': 'UNKNOWN'}
    else:
        path = matches[0]; stat = path.stat(); identity = [stat.st_dev, stat.st_ino]
        if state is None:
            state = {'schemaVersion': 1, 'identity': identity, 'offset': stat.st_size,
                     'startedAtJST': timestamp, 'previousPollAtJST': timestamp, 'seen': {}}
            atomic_save(cursor_path, state)
            result = {'eventType': 'USAGE_POLL', 'measurementId': str(uuid.uuid4()), 'timeJST': timestamp,
                      'role': args.role, 'threadId': thread_id, 'status': 'BASELINE_AT_EOF',
                      'N': None, 'T': None, 'recordCount': 0, 'coverage': 'PRE_CURSOR_UNCAPTURED'}
        elif identity != state['identity'] or stat.st_size < state['offset']:
            # Do not silently replay a new stream or lose a truncated segment.
            result = {'eventType': 'USAGE_POLL', 'measurementId': str(uuid.uuid4()), 'timeJST': timestamp,
                      'role': args.role, 'threadId': thread_id, 'status': 'SOURCE_CHANGED_REBIND_REQUIRED',
                      'N': None, 'T': None, 'recordCount': 0, 'coverage': 'UNKNOWN'}
        else:
            start = state['offset']; end, rows, issues, backlog = scan(path, start, state['seen'])
            measurement = hashlib.sha256(f'{thread_id}:{identity}:{start}:{end}'.encode()).hexdigest()
            result = {'eventType': 'USAGE_POLL', 'measurementId': measurement, 'timeJST': timestamp,
                      'fromPollJST': state['previousPollAtJST'], 'role': args.role, 'threadId': thread_id,
                      'status': 'OBSERVED_RESPONSE_USAGE' if rows else 'NO_NEW_EXPLICIT_USAGE_RECORD',
                      'N': sum(row['N'] for row in rows) if rows else None,
                      'T': sum(row['T'] for row in rows) if rows else None,
                      'recordCount': len(rows), 'issues': issues, 'backlog': backlog,
                      'coverage': 'OBSERVED_RECORDS_ONLY; SCHEMA/FLUSH/UNRECORDED_RESPONSES_NOT_PROVEN_COMPLETE'}
            # Stable response keys make a crash after append/before cursor-save deduplicable.
            with (destination / 'usage.jsonl').open('a') as handle:
                for row in rows:
                    handle.write(json.dumps({'eventType': 'RESPONSE_USAGE', 'measurementId': measurement,
                                             'role': args.role, 'threadId': thread_id, **row}) + '\n')
                handle.write(json.dumps(result) + '\n'); handle.flush(); os.fsync(handle.fileno())
            state.update(offset=end, previousPollAtJST=timestamp)
            atomic_save(cursor_path, state)
            print(json.dumps(result)); return
    with (destination / 'usage.jsonl').open('a') as handle:
        handle.write(json.dumps(result) + '\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
