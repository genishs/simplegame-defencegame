import sys; sys.path.insert(0,".")
from tests.battle_scene_simulator import BattleSceneSimulator

def probe(sid, maxt=185.0, dur=None, k4f=None):
    sim = BattleSceneSimulator(sid); sim.MAX_SIM_TIME=maxt
    scene = sim.build_scene()
    sim.auto_place_strongest_unit()
    # optional endurance retune injected at runtime
    if scene._endurance is not None and (dur or k4f):
        c=scene._endurance.config
        if dur: c.duration_s=dur
        if k4f: c.kills_for_full=k4f
    elapsed=0.0; ticks=0
    while elapsed < sim.MAX_SIM_TIME and not scene._game_over:
        scene.update(sim.DT); ticks+=1
        if scene._game_over: break
        elapsed+=sim.DT
    end=scene._endurance
    print(f"{sid}: game_over={scene._game_over} elapsed={elapsed:.0f}s "
          f"lives={scene.world.get('lives')} goals_reached={scene.world.get('goals_reached')} "
          f"all_clear={scene.wave.all_clear} enemies_left={len(scene.world['enemies'])} "
          f"defeated={scene._enemies_defeated} "
          f"endurance={'fill=%.3f victory=%s'%(end.fill,end.victory) if end else 'N/A'}")

probe("stage_04")
probe("stage_05")
print("--- stage_05 endurance retune trials ---")
probe("stage_05", dur=140, k4f=40)
probe("stage_05", dur=120, k4f=40)
