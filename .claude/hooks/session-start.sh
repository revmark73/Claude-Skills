#!/bin/bash
#
# SessionStart hook for revmark73/Claude-Skills.
#
# The skills in .agents/skills assume a sandbox that already has their
# toolchain and explicitly tell Claude not to install it. Claude Code on the
# web ships a leaner image, so without this hook those skills start work and
# then die on a missing import. This installs what they expect.
#
# Runs on the web only. Local machines keep whatever they already have.

set -uo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

FAILED=()
INSTALLED=()

note()  { printf '  %s\n' "$1"; }
group() { printf '\n[%s]\n' "$1"; }

run() {
  # run <label> <command...>: record failure, never abort the hook
  local label="$1"; shift
  if "$@" >/tmp/hook-step.log 2>&1; then
    INSTALLED+=("$label")
    note "ok      $label"
  else
    FAILED+=("$label")
    note "FAILED  $label"
    sed 's/^/          /' /tmp/hook-step.log | tail -4
  fi
}

echo "Claude-Skills: preparing the toolchain the bundled skills expect"

# ---------------------------------------------------------------- system ----
# pandoc reads .docx; poppler gives pdftoppm, which docx/pptx use to render a
# result and look at it; tesseract backs the pdf skill's OCR path.
#
# The LibreOffice ones are the easy trap. The image ships libreoffice-core, so
# `soffice` is on PATH and looks fine, but without the per-application filter
# packages it cannot open a single Office document: it just answers "source
# file could not be loaded". That silently breaks the xlsx skill's mandatory
# recalc.py, docx's accept_changes.py, and every render-and-look-at-it step.
group "system packages (apt)"
APT_WANTED=()
command -v pandoc    >/dev/null 2>&1 || APT_WANTED+=(pandoc)
command -v pdftoppm  >/dev/null 2>&1 || APT_WANTED+=(poppler-utils)
command -v tesseract >/dev/null 2>&1 || APT_WANTED+=(tesseract-ocr)
for lo in libreoffice-calc libreoffice-writer libreoffice-impress; do
  dpkg-query -W -f='${Status}' "$lo" 2>/dev/null | grep -q "ok installed" \
    || APT_WANTED+=("$lo")
done

if [ ${#APT_WANTED[@]} -eq 0 ]; then
  note "ok      already present: pandoc, poppler, tesseract, LibreOffice filters"
else
  export DEBIAN_FRONTEND=noninteractive
  apt-get update -qq >/dev/null 2>&1 || true   # blocked PPAs are expected here
  run "apt: ${APT_WANTED[*]}" apt-get install -y -qq "${APT_WANTED[@]}"
fi

# LibreOffice builds a user profile on first launch, which can outlast the
# default timeout in recalc.py and make a working setup look broken. Pay that
# cost here instead of in the middle of someone's spreadsheet.
if command -v soffice >/dev/null 2>&1; then
  timeout 120 soffice --headless --terminate_after_init >/dev/null 2>&1 \
    && note "ok      LibreOffice profile warmed" \
    || note "        LibreOffice warm-up skipped (not fatal)"
fi

# ---------------------------------------------------------------- python ----
group "python packages (pip)"
PIP=(python3 -m pip install --quiet --disable-pip-version-check)
python3 -m pip install --help 2>/dev/null | grep -q -- --break-system-packages \
  && PIP+=(--break-system-packages)

# Installed in separate runs on purpose: pip treats a run as one transaction,
# so a single unresolvable package would otherwise take the whole set with it.
#
# xlsx: openpyxl writes the workbook, pandas moves bulk data
# pdf: pypdf edits, pdfplumber extracts, pdf2image + pytesseract do OCR,
#      reportlab creates from scratch
# pptx/docx: defusedxml and lxml parse OOXML without corrupting namespaces
# slack-gif-creator: pillow draws frames, imageio and numpy assemble them
run "pip: document + data libraries" "${PIP[@]}" \
  openpyxl pandas \
  pypdf pdfplumber pdf2image reportlab pytesseract \
  pillow imageio imageio-ffmpeg numpy \
  defusedxml lxml pyyaml

# markitdown is how the xlsx and pptx skills take a quick look at a file
run "pip: markitdown" "${PIP[@]}" "markitdown[docx,pptx,xlsx,pdf]"

# mcp-builder's evaluation harness imports these. mcp wants a newer PyJWT than
# the one apt put in /usr/lib, and pip cannot uninstall a distro package
# (no RECORD file), so let it install its own copy alongside instead.
run "pip: mcp-builder harness" "${PIP[@]}" --ignore-installed PyJWT anthropic mcp

# ------------------------------------------------------------ playwright ----
# The image ships browsers at $PLAYWRIGHT_BROWSERS_PATH and forbids
# `playwright install`. A mismatched pip release looks for a browser build
# that isn't there, so take the version from the node package that was pinned
# against these exact browsers.
group "playwright (pinned to the image's chromium)"
PW_FALLBACK="1.56.0"
PW_NODE=$(npm ls -g playwright --depth=0 2>/dev/null | grep -oE 'playwright@[0-9]+\.[0-9]+\.[0-9]+' | head -1 | cut -d@ -f2)
if [ -n "$PW_NODE" ]; then
  PW_PIN="${PW_NODE%.*}.0"          # python releases track the x.y line
  note "        node playwright $PW_NODE -> pinning python playwright $PW_PIN"
else
  PW_PIN="$PW_FALLBACK"
  note "        no global node playwright found, falling back to $PW_PIN"
fi

PW_HAVE=$(python3 -c "import importlib.metadata as m; print(m.version('playwright'))" 2>/dev/null)
if [ "$PW_HAVE" = "$PW_PIN" ]; then
  note "ok      playwright $PW_PIN already installed"
else
  run "pip: playwright==$PW_PIN" "${PIP[@]}" "playwright==$PW_PIN"
fi

# Prove it can actually reach a browser. A green pip install means nothing here.
if python3 - <<'PYCHECK' >/tmp/hook-pw.log 2>&1
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    b.new_page().set_content("<b>ok</b>")
    b.close()
PYCHECK
then
  note "ok      chromium launches"
else
  FAILED+=("playwright cannot launch chromium")
  note "FAILED  chromium does not launch"
  note "        the image's browser build and the pip release disagree;"
  note "        do NOT run 'playwright install', pin a different version instead"
  sed 's/^/          /' /tmp/hook-pw.log | tail -4
fi

# ------------------------------------------------------------------ node ----
# The docx and pptx skills `require()` these from whatever directory the
# generated script lives in, so they go global and NODE_PATH points at them.
group "node packages (npm, global)"
NPM_ROOT=$(npm root -g 2>/dev/null)
NPM_WANTED=()
for pkg in docx pptxgenjs sharp react react-dom react-icons; do
  [ -d "$NPM_ROOT/$pkg" ] || NPM_WANTED+=("$pkg")
done

if [ ${#NPM_WANTED[@]} -eq 0 ]; then
  note "ok      already present: docx, pptxgenjs, sharp, react, react-dom, react-icons"
else
  run "npm: ${NPM_WANTED[*]}" npm install -g --no-fund --no-audit "${NPM_WANTED[@]}"
fi

if [ -n "$NPM_ROOT" ] && [ -n "${CLAUDE_ENV_FILE:-}" ]; then
  echo "export NODE_PATH=\"$NPM_ROOT\"" >> "$CLAUDE_ENV_FILE"
  note "ok      NODE_PATH -> $NPM_ROOT"
fi

# --------------------------------------------------------------- summary ----
printf '\n'
if [ ${#FAILED[@]} -eq 0 ]; then
  echo "Toolchain ready. ${#INSTALLED[@]} step(s) completed."
else
  echo "Toolchain mostly ready, but ${#FAILED[@]} step(s) failed:"
  for f in "${FAILED[@]}"; do echo "  - $f"; done
  echo "The skills that depend on those will not work this session."
fi

# Always succeed. A missing dependency should degrade a skill, not stop the
# session from starting.
exit 0
