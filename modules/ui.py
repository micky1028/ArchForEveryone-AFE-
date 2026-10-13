"""Curses front-end for the Etherean wizard.

Stdlib only: it works on a bare TTY (no display server, no pip packages), which is
what a fresh Arch install gives you. Markers are plain ASCII so the Linux console
font renders them correctly. The UI only collects choices; the installation itself
runs afterwards in the normal terminal (see modules/plan.py), so sudo prompts and
pacman/makepkg output behave exactly as they do today.
"""
import curses
import os
import textwrap

from modules.plan import build_plan, is_aur

TITLE = " ETHEREAN - Arch Configuration Wizard"
MIN_W, MIN_H = 64, 16
ENTER = (10, 13, curses.KEY_ENTER)

# key, kind, title, hint. Keys match settings.json (including its spelling).
STEPS = [
    ("drivers", "single", "GPU driver", "Pick the driver for your graphics card."),
    ("desktop_enviroments", "single", "Desktop environment", "The graphical desktop you will log into."),
    ("browsers", "single", "Web browser", "Packages tagged AUR are built from the Arch User Repository."),
    ("shells", "multi", "Shells", "Command-line shells."),
    ("programming_languages", "multi", "Programming languages", "Compilers and runtimes."),
    ("office", "multi", "Office", "Documents, spreadsheets, presentations."),
    ("multimedia", "multi", "Multimedia", "Video, audio, graphics and streaming."),
    ("system_utilities", "multi", "System utilities", "Monitoring, firewall, backups."),
    ("fonts", "multi", "Fonts", "Coding fonts and emoji."),
    ("games", "multi", "Games", "Launchers and gaming platforms."),
]


def wrap(text, width, indent="", sub=None):
    # `width` is the full line width, indent included; package names must not break at "-".
    return textwrap.wrap(text, max(10, width), initial_indent=indent,
                         subsequent_indent=indent if sub is None else sub,
                         break_on_hyphens=False) or [indent]


def put(scr, y, x, text, attr=0):
    h, w = scr.getmaxyx()
    if not (0 <= y < h) or not (0 <= x < w):
        return
    try:
        scr.addnstr(y, x, text, w - x, attr)
    except curses.error:
        pass  # writing the bottom-right cell raises, but the text is drawn


def bar(scr, y, left, right, attr):
    _, w = scr.getmaxyx()
    put(scr, y, 0, (left.ljust(w)[: max(0, w - len(right))] + right)[:w], attr)


def init_attrs():
    a = dict.fromkeys(("header", "hot", "accent", "ok", "warn", "dim", "footer"), 0)
    a.update(header=curses.A_REVERSE | curses.A_BOLD, hot=curses.A_REVERSE,
             accent=curses.A_BOLD, warn=curses.A_BOLD, dim=curses.A_DIM,
             footer=curses.A_REVERSE)
    if curses.has_colors():
        curses.start_color()
        try:
            curses.use_default_colors()
            bg = -1
        except curses.error:
            bg = curses.COLOR_BLACK
        pairs = [(1, curses.COLOR_WHITE, curses.COLOR_BLUE), (2, curses.COLOR_BLACK, curses.COLOR_CYAN),
                 (3, curses.COLOR_CYAN, bg), (4, curses.COLOR_GREEN, bg), (5, curses.COLOR_YELLOW, bg),
                 (6, curses.COLOR_BLACK, curses.COLOR_WHITE)]
        for n, fg, back in pairs:
            curses.init_pair(n, fg, back)
        a.update(header=curses.color_pair(1) | curses.A_BOLD, hot=curses.color_pair(2),
                 accent=curses.color_pair(3) | curses.A_BOLD, ok=curses.color_pair(4),
                 warn=curses.color_pair(5) | curses.A_BOLD, footer=curses.color_pair(6))
    return a


class Wizard:
    """Screens: 0 = welcome, 1..N = one per settings category, N+1 = review."""

    def __init__(self, settings, info, attrs, dry_run=False):
        self.settings, self.info, self.a, self.dry_run = settings, info, attrs, dry_run
        self.steps = [s for s in STEPS if settings.get(s[0])]
        self.pos = 0
        self.cursor = {}   # screen -> highlighted row (or scroll offset on text screens)
        self.top = {}      # screen -> first visible row
        self.single = {}   # key -> chosen item index, None = skip
        self.multi = {}    # key -> set of chosen item indexes
        self.asking_quit = False
        self.page = 10

    # ---- model -------------------------------------------------------------
    @property
    def review_pos(self):
        return len(self.steps) + 1

    def on_list(self):
        return 1 <= self.pos <= len(self.steps)

    def step(self):
        return self.steps[self.pos - 1]

    def rows(self):
        """Labels of the current list screen (single-select gets a Skip row first)."""
        key, kind = self.step()[:2]
        items = list(self.settings[key])
        return ["Skip (install nothing)"] + items if kind == "single" else items

    def selected(self, row):
        key, kind = self.step()[:2]
        if kind == "single":
            return self.single.get(key) == row - 1 if row else self.single.get(key) is None
        return row in self.multi.get(key, set())

    def selection(self):
        out = {}
        for key, kind, _, _ in self.steps:
            items = self.settings[key]
            if kind == "single":
                i = self.single.get(key)
                out[key] = None if i is None else items[i]
            else:
                out[key] = [items[i] for i in sorted(self.multi.get(key, ()))]
        return out

    # ---- input -------------------------------------------------------------
    def go(self, d):
        self.pos = max(0, min(self.review_pos, self.pos + d))
        if self.pos not in self.cursor:
            row = 0
            if self.on_list() and self.step()[1] == "single":
                chosen = self.single.get(self.step()[0])
                row = 0 if chosen is None else chosen + 1
            self.cursor[self.pos] = row

    def move(self, d):
        cur = max(0, self.cursor.get(self.pos, 0) + d)
        if self.on_list():
            cur = min(cur, len(self.rows()) - 1)
        self.cursor[self.pos] = cur  # text screens are clamped while drawing

    def choose(self):
        key, kind = self.step()[:2]
        row = self.cursor[self.pos]
        if kind == "single":
            self.single[key] = None if row == 0 else row - 1
        else:
            s = self.multi.setdefault(key, set())
            s.symmetric_difference_update({row})

    def choose_all(self):
        key, kind = self.step()[:2]
        if kind == "multi":
            n = len(self.settings[key])
            s = self.multi.setdefault(key, set())
            s.clear() if len(s) == n else s.update(range(n))

    def handle(self, ch):
        """Feed one key. Returns 'install', 'quit' or None."""
        if self.asking_quit:
            if ch in (ord("y"), ord("Y")):
                return "quit"
            self.asking_quit = False
            return None
        if ch in (ord("q"), ord("Q"), 27):
            self.asking_quit = True
        elif ch in (curses.KEY_UP, ord("k")):
            self.move(-1)
        elif ch in (curses.KEY_DOWN, ord("j")):
            self.move(1)
        elif ch == curses.KEY_PPAGE:
            self.move(-self.page)
        elif ch == curses.KEY_NPAGE:
            self.move(self.page)
        elif ch in (curses.KEY_HOME, ord("g")):
            self.move(-10 ** 6)
        elif ch in (curses.KEY_END, ord("G")):
            self.move(10 ** 6)
        elif ch in (curses.KEY_LEFT, curses.KEY_BACKSPACE, 127, 8, ord("b"), ord("B")):
            self.go(-1)
        elif ch == ord(" ") and self.on_list():
            self.choose()
        elif ch in (ord("a"), ord("A")) and self.on_list():
            self.choose_all()
        elif ch in ENTER:
            if self.pos == self.review_pos:
                return "install"
            if self.on_list() and self.step()[1] == "single":
                self.choose()
            self.go(1)
        elif ch in (ord(" "), curses.KEY_RIGHT) and self.pos == 0:
            self.go(1)
        return None

    # ---- drawing -----------------------------------------------------------
    def draw(self, scr):
        scr.erase()
        h, w = scr.getmaxyx()
        if h < MIN_H or w < MIN_W:
            put(scr, 0, 0, f"Window too small (need {MIN_W}x{MIN_H})", self.a["warn"])
            scr.refresh()
            return
        bar(scr, 0, TITLE, f"Step {self.pos + 1}/{len(self.steps) + 2} ", self.a["header"])
        top, bottom = 3, h - 1
        self.page = bottom - top
        if self.on_list():
            key, kind, title, hint = self.step()
            put(scr, 1, 2, title, self.a["accent"])
            if kind == "multi":
                n = len(self.multi.get(key, ()))
                tag = f"{n} of {len(self.settings[key])} selected"
                put(scr, 1, w - len(tag) - 2, tag, self.a["dim"])
            put(scr, 2, 2, hint, self.a["dim"])
            self.draw_list(scr, top, bottom, w)
        else:
            title, hint, lines = (("Welcome", "Read this, then press Enter.", self.welcome_lines(w - 6))
                                  if self.pos == 0 else
                                  ("Review", "Check everything before installing.", self.review_lines(w - 6)))
            put(scr, 1, 2, title, self.a["accent"])
            put(scr, 2, 2, hint, self.a["dim"])
            self.draw_text(scr, lines, top, bottom, w)
        self.draw_footer(scr, h)
        if self.asking_quit:
            msg = " Quit without installing anything?  (y = quit, any other key = stay) "
            put(scr, h // 2, max(0, (w - len(msg)) // 2), msg, self.a["warn"] | curses.A_REVERSE)
        scr.refresh()

    def draw_list(self, scr, top, bottom, w):
        key, kind = self.step()[:2]
        rows = self.rows()
        page = bottom - top
        cur = self.cursor[self.pos]
        first = max(min(self.top.get(self.pos, 0), cur), cur - page + 1)
        self.top[self.pos] = first
        for i in range(first, min(len(rows), first + page)):
            y = top + i - first
            sel = self.selected(i)
            mark = ("(*)" if sel else "( )") if kind == "single" else ("[x]" if sel else "[ ]")
            line = f" {'>' if i == cur else ' '} {mark} {rows[i]}"
            attr = self.a["hot"] if i == cur else (self.a["ok"] if sel else 0)
            if kind == "single" and i == 0 and i != cur and not sel:
                attr = self.a["dim"]
            put(scr, y, 0, line.ljust(w), attr)
            real = i - 1 if kind == "single" else i
            if real >= 0 and is_aur(key, rows[i]):
                put(scr, y, len(line) + 2, "[AUR]", attr if i == cur else self.a["warn"])
        self.scroll_marks(scr, top, bottom, w, first > 0, first + page < len(rows))

    def draw_text(self, scr, lines, top, bottom, w):
        page = bottom - top
        off = max(0, min(self.cursor.get(self.pos, 0), len(lines) - page))
        self.cursor[self.pos] = off
        for i, (text, attr) in enumerate(lines[off: off + page]):
            put(scr, top + i, 2, text, attr)
        self.scroll_marks(scr, top, bottom, w, off > 0, off + page < len(lines))

    def scroll_marks(self, scr, top, bottom, w, more_up, more_down):
        if more_up:
            put(scr, top, w - 2, "^", self.a["dim"])
        if more_down:
            put(scr, bottom - 1, w - 2, "v", self.a["dim"])

    def draw_footer(self, scr, h):
        if self.pos == 0:
            keys = "Enter start | Up/Dn scroll | q quit"
        elif self.pos == self.review_pos:
            keys = "Enter INSTALL | b back | Up/Dn scroll | q quit"
        elif self.step()[1] == "single":
            keys = "Space select | Enter pick & next | b back | q quit"
        else:
            keys = "Space toggle | a all/none | Enter next | b back | q quit"
        bar(scr, h - 1, " " + keys, "", self.a["footer"])

    # ---- text screens ------------------------------------------------------
    def welcome_lines(self, w):
        a, i = self.a, self.info
        L = [(t, 0) for t in wrap("This wizard turns a fresh Arch Linux install into a ready-to-use "
                                  "system: drivers, desktop, apps and tools, chosen step by step.", w)]
        L += [("", 0)]
        L += [(t, a["ok"]) for t in wrap("Nothing is installed until you confirm on the final review screen.", w)]
        L += [("", 0), ("System", a["accent"]),
              (f"  Distribution : {i['name']} ({i['id']})", 0),
              (f"  Privileges   : {i['privileges']}", a["warn"] if i["privileges"].startswith("NONE") else 0)]
        if not i["is_arch"]:
            L += [(t, a["warn"]) for t in wrap("This does not look like Arch Linux (no /etc/arch-release). "
                                                "Use --dry-run to preview without installing.", w, "  ")]
        if self.dry_run:
            L += [("  Mode         : DRY RUN - nothing will be changed", a["warn"])]
        s = self.settings
        L += [("", 0), ("Always applied", a["accent"]),
              (f"  {len(s.get('pacman_packages', []))} base pacman packages, "
               f"{len(s.get('aur_packages', []))} AUR, {len(s.get('services', []))} service(s)", 0)]
        return L

    def review_lines(self, w):
        a, s = self.a, self.settings

        def block(label, items):
            text = ", ".join(items)
            ind = f"  {label:<24}"
            return [(t, 0) for t in wrap(text, w, ind, " " * len(ind))]

        sel = self.selection()
        plan = build_plan(s, sel)
        pac = {p for _, k, ps in plan if k == "pacman" for p in ps}
        aur = {p for _, k, ps in plan if k == "aur" for p in ps}
        total = f"Total: {len(pac) + len(aur)} packages ({len(aur)} from the AUR), then a full system upgrade."
        L = [(t, a["ok"]) for t in wrap(total, w)]
        L += [(t, a["ok"]) for t in wrap("Press Enter to install, or b to go back and change something.", w)]
        if self.dry_run:
            L += [("DRY RUN: the plan will be printed, nothing will be changed.", a["warn"])]
        L += [("", 0), ("Your choices", a["accent"])]
        for key, _, title, _ in self.steps:
            val = sel[key]
            items = [val] if isinstance(val, str) else (val or [])
            if items:
                L += block(title, [f"{p} [AUR]" if is_aur(key, p) else p for p in items])
            else:
                L += [(f"  {title:<24}(skipped)", a["dim"])]
        L += [("", 0), ("Always applied", a["accent"])]
        if s.get("pacman_packages"):
            L += block("Base pacman packages", s["pacman_packages"])
        if s.get("aur_packages"):
            L += block("Base AUR packages", s["aur_packages"])
        if s.get("services"):
            L += block("Services", s["services"])
        return L

    # ---- main loop ---------------------------------------------------------
    def loop(self, scr):
        self.go(0)
        while True:
            self.draw(scr)
            ch = scr.getch()
            if ch == curses.KEY_RESIZE:
                continue
            res = self.handle(ch)
            if res == "install":
                return self.selection()
            if res == "quit":
                return None


def run_wizard(settings, info, dry_run=False):

    os.environ.setdefault("ESCDELAY", "25")

    def _main(scr):
        try:
            curses.curs_set(0)
        except curses.error:
            pass
        scr.keypad(True)
        return Wizard(settings, info, init_attrs(), dry_run).loop(scr)

    return curses.wrapper(_main)
