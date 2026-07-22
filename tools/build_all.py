#!/usr/bin/env python3
"""Regenerate every embedded dataset, then run the pre-flight checks.

Exists because CODEX did not have a build step and had drifted 44 tables behind
data/tables.json -- index additions were silently not reaching the app, and a
description fixed in the JSON was still null in two shipped builds. Every
dataset now has a step, and this runs all of them so nobody has to remember.
"""
import subprocess, sys, pathlib
root = pathlib.Path(__file__).resolve().parent
STEPS = ['build_codex.py', 'build_fk.py', 'build_sfmap.py', 'build_clusters.py']
for s in STEPS:
    print(f'── {s}')
    r = subprocess.run([sys.executable, str(root / s)], capture_output=True, text=True)
    print('   ' + (r.stdout.strip() or r.stderr.strip()))
    if r.returncode:
        sys.exit(f'FAILED: {s}')
print('── check_styles.py')
r = subprocess.run([sys.executable, str(root / 'check_styles.py')], capture_output=True, text=True)
print('   ' + (r.stdout.strip() or r.stderr.strip()))
sys.exit(r.returncode)
