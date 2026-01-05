#!/usr/bin/env bash
find repos/dem2 -type f | grep -Ev '(extractor_output/|pdf_tests/medical_records/|medical-agent/tests/(reports|dumps)/|\.git|\bnode_modules\b|\.venv|\.mypy_cache|\.ruff_cache|\.pytest_cache|\.pyc)\b' | grep -E '\.(py|sh|js|ts|yml|md)$' | sed 's/^.*$/edit &/' > /tmp/edit.vim && vim -c 'so /tmp/edit.vim'
