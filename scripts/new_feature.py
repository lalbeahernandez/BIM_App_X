import re, sys
from pathlib import Path

if len(sys.argv) < 3:
    raise SystemExit('usage: python scripts/new_feature.py FEATURE-ID "Feature title"')
feature_id, title = sys.argv[1], sys.argv[2]
slug = re.sub(r'[^a-z0-9]+','-', title.lower()).strip('-')
path = Path(__file__).resolve().parents[1] / 'specs' / 'features' / f'{feature_id.lower()}-{slug}.md'
path.write_text(f'# {feature_id}: {title}\n\n## Outcome\n\n## Non-goals\n\n## Acceptance criteria\n\n- [ ] \n\n## Data/contract impact\n\n## Test plan\n')
print(path)
