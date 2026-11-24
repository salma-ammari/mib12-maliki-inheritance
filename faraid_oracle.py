"""
Copyright (c) 2026 Salma Ammari. Licensed under CC BY-NC 4.0 (see LICENSE).

faraid_oracle.py  -  Madhab-parameterized reference engine (test oracle)
for the Maliki Inheritance Benchmark (MIB-12).

Scope: the heirs and rules needed by the benchmark (spouses, parents,
paternal grandfather, grandmothers, son/daughter, full siblings,
uterine siblings, daughter's son as dhu rahim) with the juristic
switches on which the schools differ.  Exact rational arithmetic.
"""
from fractions import Fraction as F
from math import lcm
from dataclasses import dataclass

@dataclass(frozen=True)
class Profile:
    name: str
    mushtaraka_share: bool          # full brothers share the uterine third
    zayd_grandfather: bool          # grandfather shares with siblings (Zayd)
    radd: bool                      # surplus returned to sharers (not spouses)
    dhawu_arham: bool               # distant kindred inherit
    grandmothers: str               # 'two' | 'three' | 'all'
    accidental_killer_inherits: bool

PROFILES = {
  "Maliki (later / fatwa practice)": Profile("MAL", True,  True,  True,  True,  "two",   True),
  "Maliki (early, Bayt al-Mal)":     Profile("MAL0",True,  True,  False, False, "two",   True),
  "Hanafi":                          Profile("HAN", False, False, True,  True,  "all",   False),
  "Hanbali":                         Profile("HNB", False, True,  True,  True,  "three", False),
}

GM_DEG3 = {"MMM", "FMM", "FFM"}
GM_ALLOWED = {"two": {"MM", "FM", "MMM", "FMM"},
              "three": {"MM", "FM", "MMM", "FMM", "FFM"},
              "all": {"MM", "FM", "MMM", "FMM", "FFM"}}

def solve(h: dict, p: Profile, killer: dict | None = None):
    """h: counts of heirs, e.g. {'wife':1,'son':1}. killer: {heir: 'intentional'|'accidental'}"""
    h = {k: v for k, v in h.items() if v}
    trace = []
    for heir, kind in (killer or {}).items():
        if kind == "intentional" or not p.accidental_killer_inherits:
            h.pop(heir, None); trace.append(f"{heir} excluded (killing: {kind})")
        else:
            trace.append(f"{heir} inherits from the estate, not from the diya (accidental killing)")
    g = lambda k: h.get(k, 0)
    desc = g("son") + g("daughter")
    male_desc = g("son")
    sib_full = g("full_brother") + g("full_sister")
    uterine = g("uterine")
    all_sibs = sib_full + uterine
    father, gf = g("father"), g("grandfather") and not g("father")
    share = {}
    # ---------- spouses
    if g("husband"): share["husband"] = F(1, 4) if desc else F(1, 2)
    if g("wife"):    share["wife"] = F(1, 8) if desc else F(1, 4)
    spouse = sum(share.values())
    # ---------- mother (incl. al-'Umariyyatan)
    umariyya = g("mother") and father and not desc and all_sibs < 2 and not gf \
        and set(h) <= {"husband", "wife", "father", "mother"} and spouse > 0
    if g("mother"):
        if desc or all_sibs >= 2: share["mother"] = F(1, 6)
        elif umariyya: share["mother"] = (1 - spouse) / 3; trace.append("al-'Umariyya: mother takes 1/3 of remainder")
        else: share["mother"] = F(1, 3)
    # ---------- grandmothers
    if not g("mother"):
        gms = [k for k in ("MM", "FM", "MMM", "FMM", "FFM") if g(k)]
        if father: gms = [k for k in gms if k.startswith("M")]
        if any(k in ("MM", "FM") for k in gms): gms = [k for k in gms if k not in GM_DEG3]
        gms_ok = [k for k in gms if k in GM_ALLOWED[p.grandmothers]]
        for k in set(gms) - set(gms_ok): trace.append(f"{k} does not inherit under this school")
        for k in gms_ok: share[k] = F(1, 6) / len(gms_ok)
    # ---------- uterine siblings
    ut_blocked = desc or father or gf
    if uterine and not ut_blocked:
        share["uterine"] = F(1, 6) if uterine == 1 else F(1, 3)
    # ---------- daughters
    if g("daughter") and not g("son"):
        share["daughter"] = F(1, 2) if g("daughter") == 1 else F(2, 3)
    # ---------- father with daughters only
    if father: share["father"] = F(1, 6) if desc else F(0)
    # ---------- siblings / grandfather
    sibs_blocked = male_desc or father or (gf and not p.zayd_grandfather)
    if gf and not father:
        share["grandfather"] = F(1, 6) if desc else F(0)
    # Akdariyya
    akdariyya = (gf and p.zayd_grandfather and set(h) == {"husband", "mother", "grandfather", "full_sister"}
                 and g("full_sister") == 1)
    if akdariyya:
        share.update({"grandfather": F(1, 6), "full_sister": F(1, 2)})
        tot = sum(share.values())                      # 9/6 -> 'awl to 9
        for k in share: share[k] = share[k] / tot
        pool = share["grandfather"] + share["full_sister"]
        share["grandfather"], share["full_sister"] = pool * 2 / 3, pool / 3
        trace.append("al-Akdariyya: 'awl to 9, then grandfather and sister share 2:1 -> 27")
        return finish(share, trace, h)
    fixed = sum(v for v in share.values())
    rest = 1 - fixed
    if sib_full and not sibs_blocked and not desc:
        if gf:   # Zayd: best of muqasama, 1/3 (of rest or whole), 1/6
            heads = 2 + 2 * g("full_brother") + g("full_sister")
            others = fixed > 0
            opts = {"muqasama": rest * 2 / heads,
                    "third": rest / 3 if others else F(1, 3)}
            if others: opts["sixth"] = F(1, 6)
            best = max(opts, key=opts.get)
            share["grandfather"] = opts[best]
            trace.append(f"grandfather with siblings (Zayd): {best} = {opts[best]}")
            rest = 1 - sum(share.values())
            if rest > 0: residue(share, rest, g("full_brother"), g("full_sister"), "full_brother", "full_sister")
        elif g("full_brother"):
            if rest > 0:
                residue(share, rest, g("full_brother"), g("full_sister"), "full_brother", "full_sister")
            elif p.mushtaraka_share and "uterine" in share:
                n = uterine + sib_full
                third = share.pop("uterine")
                share["uterine"] = third * uterine / n
                share["full_brother"] = third * g("full_brother") / n
                if g("full_sister"): share["full_sister"] = third * g("full_sister") / n
                trace.append("al-Mushtaraka: full brothers share the uterine third per head")
            else:
                trace.append("full brothers excluded (residue exhausted)")
        else:
            share["full_sister"] = F(1, 2) if g("full_sister") == 1 else F(2, 3)
    # ---------- residue to descendants / male ascendant
    tot = sum(share.values())
    if tot < 1:
        r = 1 - tot
        if g("son"): residue(share, r, g("son"), g("daughter"), "son", "daughter", replace=True)
        elif father: share["father"] += r
        elif gf and not (sib_full and not sibs_blocked): share["grandfather"] += r
        elif g("full_brother") and not sibs_blocked and "full_brother" not in share:
            residue(share, r, g("full_brother"), g("full_sister"), "full_brother", "full_sister")
    tot = sum(share.values())
    if tot > 1:
        trace.append(f"'awl: claims {tot} > 1")
        for k in share: share[k] /= tot
    elif tot < 1:
        r = 1 - tot
        sharers = {k: v for k, v in share.items() if k not in ("husband", "wife") and v}
        if sharers and p.radd:
            s = sum(sharers.values())
            for k in sharers: share[k] += r * sharers[k] / s
            trace.append("radd to sharers other than spouses")
        elif not sharers and g("daughter_son") and p.dhawu_arham:
            share["daughter_son"] = r; trace.append("dhu rahim (daughter's son) takes the remainder")
        else:
            share["bayt_al_mal"] = r; trace.append("remainder to Bayt al-Mal")
    return finish(share, trace, h)

def residue(share, r, males, females, km, kf, replace=False):
    units = 2 * males + females
    if replace: share.pop(km, None); share.pop(kf, None)
    share[km] = share.get(km, 0) + r * 2 * males / units
    if females: share[kf] = share.get(kf, 0) + r * females / units

def finish(share, trace, h):
    share = {k: v for k, v in share.items() if v}
    per_head = {k: v / h.get(k, 1) for k, v in share.items()}
    base = lcm(*[x.denominator for x in per_head.values()])
    units = {k: int(v * base) for k, v in share.items()}
    return {"shares": share, "base": base, "units": units, "trace": trace}

# ----------------------------------------------------------------- MIB-12
CASES = [
 ("C1", "al-'Umariyya I",            {"husband":1,"father":1,"mother":1}, None),
 ("C2", "al-'Umariyya II",           {"wife":1,"father":1,"mother":1}, None),
 ("C3", "al-Mushtaraka",             {"husband":1,"mother":1,"uterine":2,"full_brother":1}, None),
 ("C4", "Grandfather + siblings",    {"grandfather":1,"full_brother":1,"full_sister":1}, None),
 ("C5", "Wife + grandfather + brother", {"wife":1,"grandfather":1,"full_brother":1}, None),
 ("C6", "al-Akdariyya",              {"husband":1,"mother":1,"grandfather":1,"full_sister":1}, None),
 ("C7", "'Awl to 10 (control)",      {"husband":1,"mother":1,"full_sister":2,"uterine":2}, None),
 ("C8", "Radd",                      {"wife":1,"daughter":1}, None),
 ("C9", "Dhawu al-arham",            {"wife":1,"daughter_son":1}, None),
 ("C10","Three grandmothers",        {"son":1,"MMM":1,"FMM":1,"FFM":1}, None),
 ("C11","Accidental killer",         {"wife":1,"son":1,"full_brother":1}, {"son":"accidental"}),
 ("C12","Intentional killer (control)", {"wife":1,"son":1,"full_brother":1}, {"son":"intentional"}),
]

# Authoritative Maliki solutions (later/fatwa practice), entered by hand
# from the classical sources, independently of the engine: (base, units)
EXPECTED_MALIKI = {
 "C1": (6,  {"husband":3,"mother":1,"father":2}),
 "C2": (4,  {"wife":1,"mother":1,"father":2}),
 "C3": (18, {"husband":9,"mother":3,"uterine":4,"full_brother":2}),
 "C4": (5,  {"grandfather":2,"full_brother":2,"full_sister":1}),
 "C5": (8,  {"wife":2,"grandfather":3,"full_brother":3}),
 "C6": (27, {"husband":9,"mother":6,"grandfather":8,"full_sister":4}),
 "C7": (10, {"husband":3,"mother":1,"full_sister":4,"uterine":2}),
 "C8": (8,  {"wife":1,"daughter":7}),
 "C9": (4,  {"wife":1,"daughter_son":3}),
 "C10":(12, {"son":10,"MMM":1,"FMM":1}),
 "C11":(8,  {"wife":1,"son":7}),
 "C12":(4,  {"wife":1,"full_brother":3}),
}

def fmt(res):
    return ", ".join(f"{k} {res['units'][k]}" for k in res["units"]) + f"  (base {res['base']})"

if __name__ == "__main__":
    mal = list(PROFILES.values())[0]
    ok = 0
    for cid, name, heirs, kill in CASES:
        r = solve(heirs, mal, kill)
        exp_base, exp_units = EXPECTED_MALIKI[cid]
        exp = {k: F(v, exp_base) for k, v in exp_units.items()}
        match = r["shares"] == exp
        ok += match
        print(f"{cid:4} {name:30} {'PASS' if match else 'FAIL'}  {fmt(r)}")
    print(f"\nOracle validation: {ok}/{len(CASES)} cases match the hand-derived Maliki solutions\n")
    print("Madhab-sensitivity matrix (1 = differs from the Maliki fatwa-practice solution):")
    names = list(PROFILES)
    for cid, name, heirs, kill in CASES:
        base = solve(heirs, mal, kill)["shares"]
        row = [int(solve(heirs, PROFILES[n], kill)["shares"] != base) for n in names[1:]]
        print(cid, row)
