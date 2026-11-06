"""Reproduction of the PG20902 inline oracle, saved after that run; not reexecuted for confirmation.

Only public synthetic AES-GCM vectors, never a credential/live session/key file/Product call.
Output goes to stdout, and does not overwrite the original timestamped manifest.
"""
import hashlib
import json
import struct
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

version = 'fixture-v1'
result = {}
for owner in (1, 7, 999999999999):
    fields = ['SCHUBERT-NK-AUTHCTX-v1', 'schubert.auth_sessions',
              '00000000-0000-4000-8000-000000000007', str(owner), '1', version]
    aad = b''.join(struct.pack('>I', len(v.encode('ascii'))) + v.encode('ascii') for v in fields)
    nonce = bytes([0x11]) * 12
    body = AESGCM(bytes(32)).encrypt(nonce, b'a' * 64, aad)
    envelope = b'NKENC1' + bytes([1, len(version)]) + version.encode('ascii') + nonce + body
    result[str(owner)] = dict(aadFields=fields, aadHex=aad.hex(), envelopeHex=envelope.hex(),
                              envelopeBytes=len(envelope), envelopeSha256=hashlib.sha256(envelope).hexdigest())
print(json.dumps(dict(syntheticPublicOnly=True, actualCredential=False, vectors=result), indent=2))
