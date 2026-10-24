"""Lossless Caddy token equality for a public fixed template, not TLS/runtime qualification."""
import re

TOKENS=re.compile(r'\#[^\r\n]*|"(?:\\.|[^"\\])*"|`[^`]*`|[^\s{}"`#]+|[{}]')


def tokens(text):
    pieces=[];last=0
    for match in TOKENS.finditer(text):
        if text[last:match.start()].strip():raise ValueError('unparsed Caddy token')
        pieces.append(match.group());last=match.end()
    if text[last:].strip():raise ValueError('unparsed Caddy tail')
    return pieces


def equal(left,right):
    if not tokens(left) or tokens(left)!=tokens(right):raise ValueError('Caddy logical/comment/quoted token changed')
