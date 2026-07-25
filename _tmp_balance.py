import sys; sys.path.insert(0,".")
from dataclasses import replace
from src.data.loader import EnemyDef
import src.systems.auto_mode_simulator as A

# candidate stat sets to try: (hp, armor, speed, dmg, gold)
CAND = {
  "tang_heavy_infantry":   (150, 2, 42, 2, 16),
  "tang_cavalry":          (100, 1,105, 2, 12),
  "tang_siege_tower":      (260, 2, 26, 3, 28),
  "tang_elite_guard":      (200, 2, 58, 3, 24),
  "tang_elite_battering_ram":(500,2,24, 6, 80),
  "tang_taizong":          (800, 3, 34, 6,200),
}
def make_db(scale_hp=1.0, scale_armor=1.0):
    db = A.load_enemies()
    for k,(hp,ar,sp,dm,gd) in CAND.items():
        db[k]=EnemyDef(id=k,name=k,hp=int(hp*scale_hp),speed=sp,armor=max(0,int(ar*scale_armor)),
                       damage_to_castle=dm,gold_drop=gd,sprite="x",is_boss=("ram" in k or "taizong" in k))
    return db

orig = A.StageSimulator.__init__
def patched(self, stage_id, rng_seed=0, _scale=(1.0,1.0)):
    orig(self, stage_id, rng_seed)
    self._enemies_db = make_db(*_scale)

for label,scale in [("base",(1.0,1.0)),("hp80%",(0.8,1.0)),("hp60%",(0.6,0.7)),("hp50%",(0.5,0.5))]:
    A.StageSimulator.__init__ = lambda s,sid,rng_seed=0,sc=scale: patched(s,sid,rng_seed,sc)
    for sid in ("stage_04","stage_05"):
        rs=[A.StageSimulator(sid,rng_seed=s).run() for s in range(3)]
        cl=sum(r.cleared for r in rs); lv=[r.lives_remaining for r in rs]; el=[round(r.elapsed_sim_seconds) for r in rs]
        print(f"{label:6} {sid}: cleared {cl}/3 lives={lv} elapsed={el} defeated={[r.enemies_defeated for r in rs]}")
