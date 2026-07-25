import sys
sys.path.insert(0, ".")
from src.data.loader import load_enemies, load_stage

# 0. data integrity: every spawn/boss type defined?
db = load_enemies()
for sid in ("stage_01","stage_02","stage_03","stage_04","stage_05"):
    st = load_stage(sid)
    missing=[]
    for w in st.waves:
        for sp in w.spawns:
            if sp.type not in db: missing.append(sp.type)
        if w.boss and w.boss not in db: missing.append(w.boss)
    print(f"{sid}: lives={st.lives} missing={sorted(set(missing))}")

# 1. BL-07 auto sim (compressed) for stage_04/05
from src.systems.auto_mode_simulator import StageSimulator
for sid in ("stage_04","stage_05"):
    rs=[StageSimulator(sid, rng_seed=s).run() for s in range(5)]
    cl=sum(r.cleared for r in rs)
    print(f"[BL07] {sid}: cleared {cl}/5  lives={[r.lives_remaining for r in rs]} defeated={[r.enemies_defeated for r in rs]} elapsed={[round(r.elapsed_sim_seconds) for r in rs]}")
