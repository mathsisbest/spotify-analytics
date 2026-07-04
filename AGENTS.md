# Agent workflow for spotify-analytics

## Per-wave process

1. **Architect pass** — I read the codebase, produce `TASKS.md` with numbered, file-disjoint tasks and locked contracts (function signatures + return shapes). No code written.
2. **Spawn wave** — One subagent per task. Each agent:
   - Owns its files — no overlap with other tasks in the same wave
   - Implements the contract from `TASKS.md`
   - Installs deps with `make install` (or `pip install -e ".[dev]"`)
   - Self-gates with `make ci` (ruff → mypy → pytest)
   - Opens a PR with evidence block (commands run + output)
3. **Review & merge** — I review each PR adversarially, run the gate myself to confirm, then squash-merge to main.
4. **Next wave** — Repeat.

## Task isolation rules
- Same-wave tasks never share a file.
- If two tasks need the same file, they are one task or two waves.
- Locked contracts (function signatures + return types) freeze before spawning.

## Gate (must pass before PR)
```bash
make install && make ci
```
