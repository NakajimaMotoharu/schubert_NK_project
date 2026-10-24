"""Bind metric records to public completed manifest source, never to a copied caller literal."""
import hashlib
import json
import re


def bind(records, expected_source):
    if not re.fullmatch(r'[0-9a-f]{40}', expected_source) or not records:
        raise ValueError('explicit source and evidence required')
    output = []
    for path, expected_hash in records:
        if not re.fullmatch(r'[0-9a-f]{64}', expected_hash):
            raise ValueError('exact manifest checksum required')
        content = path.read_bytes()
        if hashlib.sha256(content).hexdigest() != expected_hash:
            raise ValueError('manifest checksum mismatch')
        manifest = json.loads(content)
        if manifest.get('actualExit') != 0 or type(manifest.get('actualExit')) is not int:
            raise ValueError('completed successful proof required')
        if manifest.get('source') != expected_source:
            raise ValueError('metric source must equal actual proof source')
        output.append(dict(path=str(path), sha256=expected_hash, source=expected_source))
    return output
