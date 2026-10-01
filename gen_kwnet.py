# -*- coding: utf-8 -*-
"""Hero graphic: the existing site's word-cloud keywords laid out as nodes of a
brain-shaped network, with edges between them. Emits SVG + label positions."""
import json, math, random

random.seed(11)

POLY_SRC = [
    (62, 248), (66, 196), (84, 146), (118, 104), (166, 70), (226, 46), (294, 34),
    (362, 36), (428, 52), (486, 82), (530, 122), (556, 172), (566, 226), (556, 276),
    (534, 304), (548, 330), (548, 366), (524, 396), (478, 408), (436, 396), (410, 380),
    (404, 446), (374, 452), (368, 382), (330, 366), (270, 356), (212, 346), (160, 334),
    (124, 314), (104, 290), (82, 276),
]
S, OX, OY = 1.04, 20, 50
POLY = [(OX + x * S, OY + y * S) for x, y in POLY_SRC]
W, H = 820, 790

# keywords come from data/keywords.csv so the lab can edit the list without code
import csv as _csv, os as _os

KEYWORDS, MICRO_KEYWORDS = [], []
with open(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "data", "keywords.csv")) as fh:
    for row in _csv.DictReader(l for l in fh if not l.startswith("#")):
        item = (row["word"].strip(), int(row["size"]))
        (MICRO_KEYWORDS if row.get("scale", "macro").strip() == "micro" else KEYWORDS).append(item)

def inside(p, poly=POLY):
    x, y = p
    c = False
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        if (y1 > y) != (y2 > y):
            xi = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
            if x < xi:
                c = not c
    return c


def box_inside(cx, cy, w, h, m=5):
    hw, hh = w / 2 + m, h / 2 + m
    pts = [(cx - hw, cy - hh), (cx + hw, cy - hh), (cx - hw, cy + hh), (cx + hw, cy + hh),
           (cx, cy - hh), (cx, cy + hh), (cx - hw, cy), (cx + hw, cy)]
    return all(inside(p) for p in pts)


def overlaps(a, b, pad=9):
    return (abs(a["cx"] - b["cx"]) * 2 < a["w"] + b["w"] + pad * 2 and
            abs(a["cy"] - b["cy"]) * 2 < a["h"] + b["h"] + pad * 2)


# ---- place labels, biggest first -------------------------------------------
labels, dropped = [], []
xs = [p[0] for p in POLY]; ys = [p[1] for p in POLY]
for i, (text, size) in enumerate(KEYWORDS):
    w = len(text) * size * 0.54
    h = size * 1.06
    placed = False
    for attempt in range(6000):
        cx = random.uniform(min(xs), max(xs))
        cy = random.uniform(min(ys), max(ys))
        if not box_inside(cx, cy, w, h):
            continue
        cand = {"cx": cx, "cy": cy, "w": w, "h": h}
        if any(overlaps(cand, l) for l in labels):
            continue
        labels.append({"id": "k%d" % i, "text": text, "size": size,
                       "cx": cx, "cy": cy, "w": w, "h": h})
        placed = True
        break
    if not placed:
        dropped.append(text)

# ---- background mesh (avoids the label boxes) ------------------------------
mesh = []
tries = 0
while len(mesh) < 150 and tries < 60000:
    tries += 1
    p = (random.uniform(min(xs), max(xs)), random.uniform(min(ys), max(ys)))
    if not inside(p):
        continue
    if any(abs(p[0] - l["cx"]) * 2 < l["w"] + 16 and abs(p[1] - l["cy"]) * 2 < l["h"] + 16 for l in labels):
        continue
    if any(math.dist(p, q) < 22 for q in mesh):
        continue
    mesh.append(p)

mesh_edges = set()
for i, p in enumerate(mesh):
    near = sorted((math.dist(p, q), j) for j, q in enumerate(mesh) if j != i)
    for _, j in near[:2]:
        if near[0][0] < 70:
            mesh_edges.add(tuple(sorted((i, j))))

# ---- keyword edges ---------------------------------------------------------
kw_edges = set()
for i, a in enumerate(labels):
    near = sorted((math.dist((a["cx"], a["cy"]), (b["cx"], b["cy"])), j)
                  for j, b in enumerate(labels) if j != i)
    for _, j in near[:2]:
        kw_edges.add(tuple(sorted((i, j))))
# a few long-range links between the biggest keywords
hubs = list(range(min(9, len(labels))))
longs = set()
while len(longs) < 7:
    a, b = random.sample(hubs, 2)
    if math.dist((labels[a]["cx"], labels[a]["cy"]), (labels[b]["cx"], labels[b]["cy"])) > 210:
        longs.add(tuple(sorted((a, b))))
kw_edges -= longs


def clip_to_box(p, q, box, pad=7):
    """point where segment p->q leaves box (centred on box)"""
    px, py = p; qx, qy = q
    dx, dy = qx - px, qy - py
    hw, hh = box["w"] / 2 + pad, box["h"] / 2 + pad
    t = 1.0
    for half, d, c, o in ((hw, dx, box["cx"], px), (hh, dy, box["cy"], py)):
        if abs(d) < 1e-6:
            continue
        for sgn in (-1, 1):
            tt = (c + sgn * half - o) / d
            if 0 < tt < t:
                # only accept if the other axis is within the box at tt
                nx, ny = px + dx * tt, py + dy * tt
                if (abs(nx - box["cx"]) <= hw + .6) and (abs(ny - box["cy"]) <= hh + .6):
                    t = tt
    return px + dx * t, py + dy * t


def f(v):
    return "%.1f" % v


out = ['<svg viewBox="0 0 %d %d" width="%d" height="%d" preserveAspectRatio="xMidYMid meet" aria-hidden="true">' % (W, H, W, H)]
out.append('<g class="mesh-e">')
for i, j in mesh_edges:
    out.append('<line x1="%s" y1="%s" x2="%s" y2="%s"></line>' % (f(mesh[i][0]), f(mesh[i][1]), f(mesh[j][0]), f(mesh[j][1])))
out.append('</g><g class="mesh-n">')
for x, y in mesh:
    out.append('<circle cx="%s" cy="%s" r="%s"></circle>' % (f(x), f(y), random.choice(["1.4", "1.8", "2.2"])))
out.append('</g>')

out.append('<g class="kw-e">')
for i, j in sorted(kw_edges):
    a, b = labels[i], labels[j]
    p = clip_to_box((a["cx"], a["cy"]), (b["cx"], b["cy"]), a)
    q = clip_to_box((b["cx"], b["cy"]), (a["cx"], a["cy"]), b)
    out.append('<line data-a="%s" data-b="%s" x1="%s" y1="%s" x2="%s" y2="%s"></line>'
               % (a["id"], b["id"], f(p[0]), f(p[1]), f(q[0]), f(q[1])))
out.append('</g><g class="kw-arc">')
for i, j in sorted(longs):
    a, b = labels[i], labels[j]
    p = clip_to_box((a["cx"], a["cy"]), (b["cx"], b["cy"]), a)
    q = clip_to_box((b["cx"], b["cy"]), (a["cx"], a["cy"]), b)
    mx, my = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2
    dx, dy = q[0] - p[0], q[1] - p[1]
    L = math.hypot(dx, dy)
    nx, ny = -dy / L, dx / L
    bend = L * 0.2
    cx, cy = mx + nx * bend, my + ny * bend
    if cy > my:
        cx, cy = mx - nx * bend, my - ny * bend
    out.append('<path data-a="%s" data-b="%s" d="M%s %s Q%s %s %s %s"></path>'
               % (a["id"], b["id"], f(p[0]), f(p[1]), f(cx), f(cy), f(q[0]), f(q[1])))
out.append('</g>')

# node dot for every keyword (small, sits under the word)
out.append('<g class="kw-n">')
for l in labels:
    out.append('<circle data-n="%s" cx="%s" cy="%s" r="%s"></circle>'
               % (l["id"], f(l["cx"]), f(l["cy"] + l["h"] / 2 + 6), "2.6" if l["size"] >= 18 else "2"))
out.append('</g>')


# ---- micro inset (neurons) -------------------------------------------------
def neurons(cx, cy, R, count=7):
    o, somas, tries = [], [], 0
    while len(somas) < count and tries < 5000:
        tries += 1
        a = random.uniform(0, 2 * math.pi)
        rr = R * math.sqrt(random.uniform(0.02, 0.62))
        p = (cx + rr * math.cos(a), cy + rr * math.sin(a))
        if all(math.dist(p, q) > R * 0.36 for q in somas):
            somas.append(p)
    o.append('<g class="dend">')
    for sx, sy in somas:
        for b in range(random.randint(4, 6)):
            ang = 2 * math.pi * b / 5 + random.uniform(-0.4, 0.4)
            x, y, seg = sx, sy, [(sx, sy)]
            for s in range(random.randint(5, 9)):
                ang += random.uniform(-0.45, 0.45)
                nx_, ny_ = x + random.uniform(5, 9) * math.cos(ang), y + random.uniform(5, 9) * math.sin(ang)
                if math.dist((nx_, ny_), (cx, cy)) > R - 6:
                    break
                x, y = nx_, ny_
                seg.append((x, y))
            if len(seg) > 1:
                o.append('<polyline points="%s"></polyline>' % " ".join("%s,%s" % (f(a), f(b)) for a, b in seg))
    o.append('</g><g class="syn">')
    for i in range(len(somas)):
        for j in range(i + 1, len(somas)):
            if math.dist(somas[i], somas[j]) < R * 0.75:
                o.append('<line x1="%s" y1="%s" x2="%s" y2="%s"></line>'
                         % (f(somas[i][0]), f(somas[i][1]), f(somas[j][0]), f(somas[j][1])))
    o.append('</g><g class="soma">')
    for sx, sy in somas:
        o.append('<circle cx="%s" cy="%s" r="4.4"></circle>' % (f(sx), f(sy)))
    o.append('</g>')
    return "".join(o), somas


# focus circle: the emptiest spot in the upper-right of the brain
cands = [(x, y)
         for x in range(int(min(xs)) + 40, int(max(xs)) - 40, 8)
         for y in range(int(min(ys)) + 40, int(max(ys)) - 40, 8)
         if inside((x, y)) and x > (min(xs) + max(xs)) / 2]
def clearance(p):
    return min(min(math.dist(p, (l["cx"], l["cy"])) - max(l["w"], l["h"]) / 2 for l in labels),
               min(math.dist(p, (q[0], q[1])) for q in POLY))
hx, hy = max(cands, key=clearance) if cands else (OX + 430 * S, OY + 150 * S)
icx, icy, iR = 648, 612, 150
L = math.hypot(icx - hx, icy - hy)
sx_, sy_ = hx + (icx - hx) / L * 30, hy + (icy - hy) / L * 30
ex_, ey_ = icx - (icx - hx) / L * iR, icy - (icy - hy) / L * iR
out.append('<circle class="focus" cx="%s" cy="%s" r="30"></circle>' % (f(hx), f(hy)))
out.append('<line class="leader" x1="%s" y1="%s" x2="%s" y2="%s"></line>' % (f(sx_), f(sy_), f(ex_), f(ey_)))
out.append('<circle class="inset" cx="%d" cy="%d" r="%d"></circle>' % (icx, icy, iR))
neuron_svg, somas = neurons(icx, icy, iR, count=9)
out.append(neuron_svg)

# keyword labels inside the micro circle, wired to the nearest cell bodies
micro_labels = []
for i, (text, size) in enumerate(MICRO_KEYWORDS):
    w, h = len(text) * size * 0.54, size * 1.06
    for attempt in range(8000):
        a = random.uniform(0, 2 * math.pi)
        rr = (iR - 26) * math.sqrt(random.uniform(0, 1))
        cx, cy = icx + rr * math.cos(a), icy + rr * math.sin(a)
        if math.hypot(cx - icx, cy - icy) + max(w, h) / 2 > iR - 16:
            continue
        cand = {"cx": cx, "cy": cy, "w": w, "h": h}
        if any(overlaps(cand, l, pad=12) for l in micro_labels):
            continue
        if any(abs(cx - s[0]) * 2 < w + 16 and abs(cy - s[1]) * 2 < h + 16 for s in somas):
            continue
        micro_labels.append({"id": "m%d" % i, "text": text, "size": size,
                             "cx": cx, "cy": cy, "w": w, "h": h})
        break

out.append('<g class="kw-e kw-e--micro">')
for l in micro_labels:
    near = sorted(somas, key=lambda s: math.dist((l["cx"], l["cy"]), s))[:2]
    for s in near:
        p = clip_to_box((l["cx"], l["cy"]), s, l, pad=5)
        out.append('<line data-a="%s" data-b="soma" x1="%s" y1="%s" x2="%s" y2="%s"></line>'
                   % (l["id"], f(p[0]), f(p[1]), f(s[0]), f(s[1])))
out.append('</g>')
labels_all = labels + micro_labels
out.append('</svg>')

json.dump({
    "svg": "\n".join(out),
    "labels": [{"id": l["id"], "text": l["text"], "size": l["size"], "micro": l["id"].startswith("m"),
                "x": round(l["cx"] / W * 100, 3), "y": round(l["cy"] / H * 100, 3)} for l in labels_all],
    "W": W, "H": H, "dropped": dropped,
}, open("kwnet.json", "w"))
print("macro", len(labels), "micro", len(micro_labels), "dropped", dropped)
