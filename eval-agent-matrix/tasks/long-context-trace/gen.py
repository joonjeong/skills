"""Generate a deterministic 300-module maze with one true call chain and decoys."""
import os, random, sys
root = sys.argv[1]  # argv[2] = hidden answer path (outside the workdir)
rnd = random.Random(41)
N = 300
os.makedirs(f"{root}/svc", exist_ok=True)
open(f"{root}/svc/__init__.py", "w").write("")
open(f"{root}/svc/audit.py", "w").write("class _A:\n    def write(self, m):\n        pass\nAUDIT = _A()\n")
chain = rnd.sample(range(N), 7)
mods = {i: [] for i in range(N)}
for i in range(N):
    for k in range(5):
        mods[i].append(f"def f_{k}(x):\n    return x  # noop {rnd.random():.6f}\n")
# decoys that write the audit log but are unreachable
for d in rnd.sample([i for i in range(N) if i not in chain], 4):
    mods[d][4] = f"from svc.audit import AUDIT\ndef f_4(x):\n    AUDIT.write(x)\n    return x\n"
for pos, m in enumerate(chain):
    k = rnd.randrange(5)
    if pos == len(chain) - 1:
        mods[m][k] = f"from svc.audit import AUDIT\ndef f_{k}(x):\n    AUDIT.write(x)\n    return x\n"
        answer = f"svc.m{m:03d}.f_{k}"
    else:
        nxt = chain[pos + 1]; nk = None
        mods[m][k] = None  # filled after next k known
        mods[m].append((k, nxt))
    chain[pos] = (m, k)
# resolve forward calls
for pos in range(len(chain) - 1):
    m, k = chain[pos]; nm, nk = chain[pos + 1]
    body = f"import svc.m{nm:03d} as nxt\ndef f_{k}(x):\n    return nxt.f_{nk}(x)\n"
    if pos == 0:
        body += f"def handle_refund(req):\n    return f_{k}(req)\n"
    mods[m][k] = body
for i in range(N):
    parts = [p for p in mods[i] if isinstance(p, str)]
    open(f"{root}/svc/m{i:03d}.py", "w").write("\n\n".join(parts))
open(sys.argv[2], "w").write(answer)
