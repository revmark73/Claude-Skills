"""Build the full print wrap (back, spine, front) for Vital Signs.

Units are print pixels at 300 dpi. Change SPINE_IN once the final page
count and paper are confirmed with Acutrack, then run this again.
"""
import re
import random

DPI = 300
TRIM_W, TRIM_H = 6.0, 9.0
BLEED = 0.125
PAGES = 160
PAPER_IN_PER_PAGE = 0.0025  # 60# white offset, confirm with Acutrack
SPINE_IN = round(PAGES * PAPER_IN_PER_PAGE, 3)

px = lambda inches: inches * DPI
B = px(BLEED)
PANEL = px(TRIM_W)
S = px(SPINE_IN)
W = B + PANEL + S + PANEL + B
H = B + px(TRIM_H) + B
BACK_X = B
SPINE_X = B + PANEL
FRONT_X = B + PANEL + S
SAFE = px(0.25)
HORIZON = B + 1860

# ---------- front world, lifted from the approved front cover ----------
front = open("cover.template.html").read()
gen = open("gen.txt").read().split("\n")
sec, cur = {}, None
for line in gen:
    if line in ("PARTS", "GRID", "LEFT", "RIGHT"):
        cur = line
        sec[cur] = []
    else:
        sec[cur].append(line)
for k in sec:
    front = front.replace(f"__{k}__", "\n".join(sec[k]).strip())

svg = re.search(r'<svg class="world"[^>]*>(.*?)</svg>', front, re.S).group(1)
defs = re.search(r"<defs>(.*?)</defs>", svg, re.S).group(1)
body = svg.split("</defs>", 1)[1]
# stretch the front's backgrounds into the bleed
body = body.replace('<rect width="1800" height="2700"', '<rect x="-60" y="-60" width="1920" height="2820"')
body = body.replace('y2="2700"', 'y2="2760"')
body = body.replace('<rect x="0" y="1860" width="1800" height="840"', '<rect x="-60" y="1860" width="1920" height="900"')
defs = defs.replace('<rect width="1800" height="2700" fill="url(#fogBand)"/>',
                    '<rect x="-60" y="-60" width="1920" height="2820" fill="url(#fogBand)"/>')

front_css = re.search(r"<style>(.*?)</style>", front, re.S).group(1)
front_type = re.search(r'<div class="type">(.*?)</div>\s*</div>\s*</body>', front, re.S).group(1)

# ---------- back world ----------
random.seed(21)
back_parts = []
for _ in range(60):
    x = random.uniform(0, PANEL + B)
    y = random.uniform(0, H)
    r = random.choice([2, 2.5, 3, 3.5, 4, 6])
    o = random.uniform(.15, .55)
    back_parts.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r}" fill="#FF5468" opacity="{o:.2f}"/>')

html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Vital Signs Wrap</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@500&family=Schibsted+Grotesk:wght@700;800;900&family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;1,8..60,400&display=block">
<style>
{front_css}
  .wrap {{ position:relative; width:{W}px; height:{H}px; overflow:hidden; background:#060C0E; }}
  .wrap > svg {{ position:absolute; left:0; top:0; }}
  .front {{ position:absolute; left:{FRONT_X}px; top:{B}px; width:1800px; height:2700px; }}
  .front .type {{ position:absolute; inset:0; }}

  .back {{ position:absolute; left:{BACK_X}px; top:{B}px; width:{PANEL}px; height:{px(TRIM_H)}px; color:var(--ink); }}
  .back .cat {{ position:absolute; left:170px; top:190px; margin:0;
    font-family:"IBM Plex Mono", monospace; font-weight:500; font-size:30px;
    letter-spacing:.14em; color:var(--trace); opacity:.8; }}
  .back h2 {{ position:absolute; left:170px; right:170px; top:270px; margin:0;
    font-family:"Schibsted Grotesk", sans-serif; font-weight:800;
    font-size:96px; line-height:1.02; letter-spacing:-.005em; }}
  .back h2 em {{ font-style:normal; color:var(--accent); }}
  .back .blurb {{ position:absolute; left:170px; right:170px; top:610px; }}
  .back .blurb p {{ margin:0 0 34px; font-family:"Source Serif 4", serif;
    font-size:47px; line-height:1.42; color:#D7E1DE; }}
  .back .blurb p.close {{ font-style:italic; color:var(--ink); }}
  .back .rule {{ position:absolute; left:170px; top:1560px; width:120px; height:4px;
    margin-left:0; background:var(--accent); border-radius:2px; box-shadow:0 0 18px rgba(240,90,112,.7); }}
  .back .photo {{ position:absolute; left:170px; top:1640px; width:420px; height:464px;
    background:url(author.jpg) center/cover; border-radius:6px;
    box-shadow:0 0 0 3px #C21F3A, 0 0 40px rgba(240,90,112,.35); }}
  .back .bio {{ position:absolute; left:650px; right:170px; top:1632px; margin:0;
    font-family:"Source Serif 4", serif; font-size:37px; line-height:1.42; color:#C3D0CD; }}
  .back .bio b {{ font-family:"Schibsted Grotesk", sans-serif; font-weight:800;
    letter-spacing:.08em; color:var(--ink); font-size:36px; }}
  .back .bio .fill {{ color:#FFB3BE; background:rgba(194,31,58,.25); padding:0 6px; border-radius:4px; }}
  .barcode {{ position:absolute; right:{SAFE}px; bottom:{SAFE}px; width:600px; height:360px; background:#fff; }}

  .spine {{ position:absolute; left:{SPINE_X}px; top:{B}px; width:{S}px; height:{px(TRIM_H)}px;
    display:flex; flex-direction:column; align-items:center; }}
  .spine .t {{ writing-mode:vertical-rl; margin-top:230px;
    font-family:"Schibsted Grotesk", sans-serif; font-weight:900; font-size:{min(66, S*0.55):.0f}px;
    letter-spacing:.06em; color:var(--ink); white-space:nowrap; }}
  .spine .a {{ writing-mode:vertical-rl; position:absolute; top:2010px;
    font-family:"Schibsted Grotesk", sans-serif; font-weight:800; font-size:{min(44, S*0.38):.0f}px;
    letter-spacing:.16em; color:var(--ink); white-space:nowrap; }}
  .spine svg {{ position:absolute; top:2440px; left:50%; transform:translateX(-50%); overflow:visible; }}

  .guides {{ position:absolute; inset:0; pointer-events:none; display:none; }}
  .proof .guides {{ display:block; }}
  .guides div {{ position:absolute; }}
  .g-trim {{ left:{B}px; top:{B}px; right:{B}px; bottom:{B}px; outline:3px solid #00E5FF; }}
  .g-fold {{ top:0; bottom:0; width:0; border-left:3px dashed #00E5FF; }}
  .g-safe {{ outline:2px dashed #FFE14D; }}
  .g-label {{ font:500 30px "IBM Plex Mono", monospace; color:#111; background:#FFE14D; padding:4px 10px; }}
</style>
</head>
<body>
<div class="wrap">
  <svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">
    <defs>
      {defs}
      <radialGradient id="backSky" cx="40%" cy="38%" r="75%">
        <stop offset="0" stop-color="#132A31"/>
        <stop offset=".5" stop-color="#0B171B"/>
        <stop offset="1" stop-color="#060C0E"/>
      </radialGradient>
      <linearGradient id="carry" x1="{SPINE_X - 160}" x2="{FRONT_X}" y1="0" y2="0" gradientUnits="userSpaceOnUse">
        <stop offset="0" stop-color="#5FE3B0" stop-opacity="0"/>
        <stop offset="1" stop-color="#5FE3B0" stop-opacity=".55"/>
      </linearGradient>
      <linearGradient id="backFogBand" x1="0" x2="0" y1="0" y2="1">
        <stop offset=".35" stop-color="#fff" stop-opacity="0"/>
        <stop offset=".62" stop-color="#fff" stop-opacity=".8"/>
        <stop offset=".75" stop-color="#fff" stop-opacity=".9"/>
        <stop offset="1" stop-color="#fff" stop-opacity=".3"/>
      </linearGradient>
      <mask id="backFogMask"><rect x="0" y="0" width="{FRONT_X + 2}" height="{H}" fill="url(#backFogBand)"/></mask>
      <filter id="carryGlow" filterUnits="userSpaceOnUse" x="0" y="{HORIZON - 80}" width="{W}" height="160">
        <feGaussianBlur in="SourceGraphic" stdDeviation="12" result="a"/>
        <feMerge><feMergeNode in="a"/><feMergeNode in="SourceGraphic"/></feMerge>
      </filter>
      <filter id="backFog" x="0" y="0" width="100%" height="100%">
        <feTurbulence type="fractalNoise" baseFrequency="0.0024 0.006" numOctaves="4" seed="4"/>
        <feColorMatrix values="0 0 0 0 0.16  0 0 0 0 0.36  0 0 0 0 0.38  0 0 0 1.1 -0.5"/>
      </filter>
    </defs>

    <!-- back and spine -->
    <rect x="0" y="0" width="{FRONT_X + 2}" height="{H}" fill="url(#backSky)"/>
    <rect x="0" y="0" width="{FRONT_X + 2}" height="{H}" filter="url(#backFog)" mask="url(#backFogMask)" opacity=".6"/>
    <g>{''.join(back_parts)}</g>

    <!-- front -->
    <g transform="translate({FRONT_X} {B})">
      {body}
    </g>
    <!-- spine panel, so the fold lines up with a clean edge -->
    <rect x="{SPINE_X}" y="0" width="{S}" height="{H}" fill="#091215"/>
    <!-- the heartbeat carries across the spine and fades out on the back -->
    <rect x="{SPINE_X - 160}" y="{HORIZON - 2.5}" width="{160 + S + 10}" height="5" fill="url(#carry)" filter="url(#carryGlow)"/>
  </svg>

  <div class="back">
    <p class="cat">RELIGION / CHRISTIAN MINISTRY / PASTORAL RESOURCES</p>
    <h2>Every church takes on the pulse <em>of the one who leads it.</em></h2>
    <div class="blurb">
      <p>When a church is struggling, we usually treat the church. Attendance dips, so we change the service. Volunteers wear out, so we recruit harder. The symptoms ease for a season and then come right back, because the trouble started somewhere else.</p>
      <p>Vital Signs starts with the leader. Mark Merrill traces how a pastor is formed and how that formation, healthy or not, shows up in the life of a congregation. Then he lays out a way back to health that begins in the leader&rsquo;s own soul and moves outward into the church.</p>
      <p class="close">For pastors who are tired of treating symptoms, and for the elders and boards who want to help them get well.</p>
    </div>
    <div class="rule"></div>
    <div class="photo" role="img" aria-label="Mark Merrill"></div>
    <p class="bio"><b>MARK MERRILL, DMin</b><br>is the founder of Vitals, a ministry platform built to keep a church&rsquo;s heartbeat steady from one Sunday to the next. He has served in pastoral ministry for <span class="fill">[__ years]</span> and lives in <span class="fill">[city, state]</span> with <span class="fill">[family]</span>.</p>
    <div class="barcode"></div>
  </div>

  <div class="spine">
    <div class="t">VITAL SIGNS</div>
    <div class="a">MERRILL</div>
    <svg width="40" height="80" viewBox="-20 -40 40 80"><g stroke="#FF4A5E" stroke-width="6" stroke-linecap="round" filter="url(#lineGlow)"><path d="M0,-36 V36 M-18,-14 H18" fill="none"/></g></svg>
  </div>

  <div class="front">
    <div class="type">{front_type}</div>
  </div>

  <div class="guides">
    <div class="g-trim"></div>
    <div class="g-fold" style="left:{SPINE_X}px"></div>
    <div class="g-fold" style="left:{FRONT_X}px"></div>
    <div class="g-safe" style="left:{BACK_X + SAFE}px; top:{B + SAFE}px; width:{PANEL - 2*SAFE}px; height:{px(TRIM_H) - 2*SAFE}px"></div>
    <div class="g-safe" style="left:{FRONT_X + SAFE}px; top:{B + SAFE}px; width:{PANEL - 2*SAFE}px; height:{px(TRIM_H) - 2*SAFE}px"></div>
    <div class="g-label" style="top:{H - B - SAFE - 420}px; left:{BACK_X + PANEL - SAFE - 600}px">ISBN BARCODE 2 x 1.2 in</div>
    <div class="g-label" style="left:{B + 20}px; top:{B + 20}px">BACK 6 x 9 | TRIM (blue) | SAFE 0.25 in (yellow) | BLEED 0.125 in</div>
    <div class="g-label" style="left:{FRONT_X + 20}px; top:{B + 20}px">FRONT | SPINE {SPINE_IN} in ({PAGES} pp)</div>
  </div>
</div>
</body>
</html>
"""
open("wrap.html", "w").write(html)
print(f"wrap {W/DPI:.3f} x {H/DPI:.3f} in, {W:.0f} x {H:.0f} px, spine {SPINE_IN} in")
