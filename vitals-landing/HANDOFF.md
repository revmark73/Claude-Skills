# Vitals landing page, handoff for the next session

Branch: `claude/beautiful-cerf-iog0w2`. Live preview: https://claude.ai/artifact/4ZdyF3kms26C9gH3ttrYP9 (publish `vitals-landing/index.html` to that URL).

## What Mark asked for
Bring the cinematic, AI-graphic, scroll-driven intro from his Catalyst Bible College site into the Vitals landing page. That site was built with the 10K Websites skill, which lives in the public repo `revmark73/10k_CBC_Website` (`SKILL.md` on `main`; the finished CBC build is on branch `claude/catalyst-bible-college-site-brnel1`, see `docs/assets/js/hero.js` for the hero video code). Follow that skill.

## Decisions already made
- All features are treated as built. No "coming soon" anywhere.
- No $99 standalone coaching price on the page.
- Time saved: "8 to 10 hours a week", worded as what Vitals is built to give.
- Nav "Try a month" button text is white.
- Hero film concept chosen: **The heartbeat.** A crimson pulse of light races through dark space, spikes into heartbeats, then the lines come together into a cross of light (Mark changed this from a heart).
- Church still: a modern church in an ordinary town or city, not a quaint country chapel.
- Captions over the film: "Sunday ends." then "Monday is already waiting." then "Vitals keeps the heartbeat steady." Then the headline and buttons appear.
- Writing rules: no em dashes, no rule-of-three constructions, Mark's plain voice.

## Higgsfield work done (5.5 credits spent)
| Piece | Job id | Model |
|---|---|---|
| Start frame | 16f6e63a-e16e-47db-a2ee-77fb35fa9ea7 | gpt_image_2_5, 16:9, 2k, high |
| End frame | bdccd636-29fe-462a-80b4-f17888c60a22 | gpt_image_2_5, 16:9, 2k, high |

Files sit on `d8j0ntlcm91z4.cloudfront.net`. The first session could not download them because the environment's network policy blocked that host. A new session should confirm it can reach it before anything else.

## Next steps
1. Download both frames and inspect them (no text, no logos, heart reads as abstract light, not anatomical). Get Mark's yes.
2. Video: `kling3_0`, mode `pro`, sound `off`, 6 seconds, 16:9, start_image = start frame job, end_image = end frame job. Preflighted at 10.5 credits.
3. Three supporting stills in the same world for lower sections (about 2.75 credits each).
4. ffmpeg: re-encode the video for scroll scrubbing with a short keyframe interval, make a poster and an end still, compress stills for web.
5. Rebuild the hero as a scroll-driven film (video plays forward on scroll down, backward on scroll up) with the captions above, settling into the current headline, Monday note, and readouts. Phones and reduced motion get the end still. Add scroll movement to the new stills in lower sections.
6. Publish the artifact with the video and images passed through `files`, commit, and push.

## Update: final Higgsfield set (50.75 credits spent in total)
| Piece | Job id | Use |
|---|---|---|
| Film, seven lines merge to one heartbeat then a cross | b1e01aa8-6de4-407b-81d7-9a6fd41fb5f3 | assets/hero.mp4 |
| Cross end frame | e7db629d-f352-48eb-a1e5-9a58492474ad | reference only |
| Desk still | 70c7d14d-a5e2-4cec-a424-03e528b73170 | assets/still-desk.jpg |
| Seven lines still | 15a9f4cd-823d-46bb-8436-8dcf54b91a20 | assets/still-lines.jpg |
| Modern town church still | 055e32a7-4de7-44ad-bc73-d87283c2aee5 | assets/still-church.jpg |

Superseded, do not use: single-line cross film 1d2aa6ed-74fe-4ce5-90ef-17bc304620f4, heart film a7481933-d28e-4e03-8ec5-c069e5a0cb7c, heart end frame bdccd636, country church 58ae0d8c.

The page code for the scroll film and parallax stills is already in index.html and expects the files named in the Use column. Since cloudfront.net stays blocked, Mark uploads the downloads to vitals-landing/assets on this branch through github.com. Then: pull, run the ffmpeg prep (scrub encode with keyframe every 4 frames, start and end jpg stills from the video, stills to 1920 wide jpg), inspect every file, publish with files, commit, push.

## Done 2026-09-26
Assets processed into vitals-landing/assets (hero.mp4 H.264 and hero.webm VP9 fallback, both with a keyframe every 4 frames; start and end stills; three section stills at 1920 wide). Raw uploads moved to vitals-review/ (git-ignored). Page published as version 6 of the artifact with all assets passed through `files`.
