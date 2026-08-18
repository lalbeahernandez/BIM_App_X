#!/usr/bin/env python3
from pathlib import Path
import yaml
p=Path(__file__).resolve().parents[1]/"codex"/"tasks.yaml"
d=yaml.safe_load(p.read_text(encoding="utf-8"))
tasks={t["id"]:t for t in d["tasks"]}
missing=[]
for tid,t in tasks.items():
    for dep in t.get("depends_on",[]):
        if dep not in tasks: missing.append((tid,dep))
if missing:
    raise SystemExit(f"Missing dependencies: {missing}")
# cycle detection
seen=set(); active=set()
def dfs(n):
    if n in active: raise SystemExit(f"Dependency cycle at {n}")
    if n in seen: return
    active.add(n)
    for d in tasks[n].get("depends_on",[]): dfs(d)
    active.remove(n); seen.add(n)
for n in tasks: dfs(n)
print(f"OK: {len(tasks)} tasks, dependencies valid, no cycles")
