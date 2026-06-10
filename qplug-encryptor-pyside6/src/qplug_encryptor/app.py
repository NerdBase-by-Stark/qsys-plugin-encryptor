"""
Q-SYS Plugin Encryptor - polished desktop GUI around QSC's plugin_tool_release.exe.

Drag a .qplug on, hit Encrypt, get a .qplugx. The GUI only ever shells out to:

    plugin_tool_release.exe encrypt  In.qplug  Out.qplugx

Runs on Windows (the only place the .exe runs) but is fully importable/constructible
on Linux/macOS for headless testing.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from PySide6.QtCore import Qt, QThread, Signal, QSettings
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication, QFileDialog, QFrame, QHBoxLayout, QLabel, QLineEdit,
    QMainWindow, QMessageBox, QPlainTextEdit, QPushButton, QSizePolicy,
    QVBoxLayout, QWidget,
)

try:
    from qplug_encryptor import __version__
except Exception:  # running app.py directly / frozen
    __version__ = "1.0.0"

TOOL_NAME = "plugin_tool_release.exe"
IS_WIN = sys.platform.startswith("win")

# --- Windows: hide the child console window so encrypting doesn't flash a cmd box.
_NO_WINDOW = 0
if IS_WIN:
    _NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)


# --------------------------------------------------------------------------- #
#  Tool location
# --------------------------------------------------------------------------- #
def app_dir() -> Path:
    """Folder the app lives in (next to the frozen .exe, or this source file)."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def icon_path() -> Path | None:
    """Locate icon.ico, whether running from source, onedir, or onefile (_MEIPASS)."""
    candidates = []
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        candidates.append(Path(meipass) / "icon.ico")
    candidates += [
        app_dir() / "icon.ico",
        Path(__file__).resolve().parent.parent.parent / "assets" / "icon.ico",
    ]
    for c in candidates:
        if c.is_file():
            return c
    return None


def bundled_tool() -> str | None:
    """QSC's plugin_tool_release.exe bundled inside the app, if this is a
    self-contained build. Resolves whether frozen (onefile _MEIPASS / onedir)
    or run from source with a populated vendor/ dir."""
    candidates = []
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        candidates.append(Path(meipass) / "tool" / TOOL_NAME)
    candidates += [
        app_dir() / "tool" / TOOL_NAME,
        Path(__file__).resolve().parent.parent.parent / "vendor" / "plugin-tool" / TOOL_NAME,
    ]
    for c in candidates:
        if c.is_file():
            return str(c.resolve())
    return None


def find_tool_quick(saved: str | None) -> str | None:
    """Fast, deterministic lookup - no slow disk walk."""
    here = app_dir()
    candidates = [
        saved,
        here / TOOL_NAME,
        here / "release" / TOOL_NAME,
        here.parent / TOOL_NAME,
        here.parent / "release" / TOOL_NAME,
    ]
    for c in candidates:
        if c and Path(c).is_file():
            return str(Path(c).resolve())
    return None


def find_tool_deep() -> str | None:
    """Opt-in (button-triggered) search of the usual download/desktop spots."""
    home = Path.home()
    roots = [
        home / "Desktop",
        home / "Downloads",
        home / "Documents",
        home,
    ]
    seen: set[str] = set()
    for root in roots:
        if not root.is_dir() or str(root) in seen:
            continue
        seen.add(str(root))
        try:
            base_depth = len(root.parts)
            for dirpath, dirnames, filenames in os.walk(root):
                # cap recursion depth to keep it snappy
                if len(Path(dirpath).parts) - base_depth > 4:
                    dirnames[:] = []
                    continue
                if TOOL_NAME in filenames:
                    return str((Path(dirpath) / TOOL_NAME).resolve())
        except (OSError, PermissionError):
            continue
    return None


# --------------------------------------------------------------------------- #
#  Worker - runs the encrypt subprocess off the UI thread (Rule 9: a real
#  QThread, signals emitted from run() are delivered safely to the UI thread).
# --------------------------------------------------------------------------- #
class EncryptWorker(QThread):
    log = Signal(str)
    result = Signal(bool, str)  # (success, message)

    def __init__(self, tool: str, infile: str, outfile: str) -> None:
        super().__init__()
        self.tool = tool
        self.infile = infile
        self.outfile = outfile

    def run(self) -> None:  # executes on the worker thread
        cmd = [self.tool, "encrypt", self.infile, self.outfile]
        self.log.emit("> " + subprocess.list2cmdline(cmd))
        try:
            proc = subprocess.run(
                cmd,
                cwd=str(Path(self.tool).parent),  # so adjacent OpenSSL DLLs load
                capture_output=True,
                text=True,
                errors="replace",
                creationflags=_NO_WINDOW,
            )
        except Exception as exc:  # noqa: BLE001 - surface anything to the user
            self.log.emit(f"ERROR: {exc}")
            self.result.emit(False, f"Could not run the tool: {exc}")
            return

        if proc.stdout:
            self.log.emit(proc.stdout.rstrip())
        if proc.stderr:
            self.log.emit(proc.stderr.rstrip())
        self.log.emit(f"[exit code {proc.returncode}]")

        out = Path(self.outfile)
        if out.is_file():
            size = out.stat().st_size
            self.log.emit(f"Wrote {out} ({size} bytes).")
            self.result.emit(True, f"Encrypted -> {out.name}  ({size} bytes)")
        else:
            self.result.emit(
                False,
                f"Failed - no output produced (exit code {proc.returncode}). See log.",
            )


# --------------------------------------------------------------------------- #
#  Main window
# --------------------------------------------------------------------------- #
QSS = """
* { font-family: "Segoe UI", "Inter", sans-serif; }
QWidget#root { background: #f4f6fb; }

QLabel#title    { color: #1f2430; font-size: 22px; font-weight: 700; }
QLabel#subtitle { color: #6b7280; font-size: 12px; }
QLabel          { color: #1f2430; font-size: 12px; }

QLabel#toolStatus[state="ok"]  { color: #16a34a; font-weight: 600; }
QLabel#toolStatus[state="err"] { color: #dc2626; font-weight: 600; }

QLabel#statusLine[state="info"] { color: #6b7280; font-size: 12px; }
QLabel#statusLine[state="busy"] { color: #2563eb; font-size: 12px; font-weight: 600; }
QLabel#statusLine[state="ok"]   { color: #16a34a; font-size: 12px; font-weight: 600; }
QLabel#statusLine[state="err"]  { color: #dc2626; font-size: 12px; font-weight: 600; }

QFrame#card { background: #ffffff; border: 1px solid #e6e9f0; border-radius: 12px; }

QFrame#dropZone { background: #f8fafc; border: 2px dashed #c7d2e0; border-radius: 12px; }
QFrame#dropZone[dragActive="true"] { background: #eaf2ff; border: 2px dashed #2563eb; }
QLabel#dropTitle { color: #475569; font-size: 15px; font-weight: 600; }
QLabel#dropHint  { color: #94a3b8; font-size: 11px; }

QLineEdit { background: #ffffff; color: #1f2430; border: 1px solid #d6dbe6;
            border-radius: 8px; padding: 6px 8px; font-size: 12px; }
QLineEdit[readOnly="true"] { background: #f3f5f9; color: #3a4150; }

QPushButton { background: #ffffff; color: #1f2430; border: 1px solid #d6dbe6;
              border-radius: 8px; padding: 6px 12px; font-size: 12px; }
QPushButton:hover { background: #eef2fb; }
QPushButton:pressed { background: #e2e8f5; }

QPushButton#primary { background: #2563eb; color: #ffffff; border: none;
                      border-radius: 10px; padding: 13px; font-size: 15px; font-weight: 700; }
QPushButton#primary:hover    { background: #1d4ed8; }
QPushButton#primary:pressed  { background: #1e40af; }
QPushButton#primary:disabled { background: #9bb4e8; color: #eef2ff; }

QPlainTextEdit#log { background: #0f172a; color: #cbd5e1; border: 1px solid #1e293b;
                     border-radius: 10px; font-family: Consolas, "Cascadia Mono", monospace;
                     font-size: 11px; padding: 8px; }
"""


def _repolish(w: QWidget) -> None:
    w.style().unpolish(w)
    w.style().polish(w)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(f"Q-SYS Plugin Encryptor  v{__version__}")
        self.setMinimumSize(660, 600)
        self.setAcceptDrops(True)

        self._settings = QSettings("StarkRecords", "QSysPluginEncryptor")
        self._tool: str | None = None
        self._infile: str | None = None
        self._worker: EncryptWorker | None = None

        root = QWidget()
        root.setObjectName("root")
        self.setCentralWidget(root)
        outer = QVBoxLayout(root)
        outer.setContentsMargins(22, 18, 22, 18)
        outer.setSpacing(14)

        # ---- header
        title = QLabel("Q-SYS Plugin Encryptor")
        title.setObjectName("title")
        subtitle = QLabel("Drag a .qplug on, hit Encrypt, get a .qplugx.")
        subtitle.setObjectName("subtitle")
        outer.addWidget(title)
        outer.addWidget(subtitle)

        # ---- tool card
        tool_card = QFrame()
        tool_card.setObjectName("card")
        tc = QVBoxLayout(tool_card)
        tc.setContentsMargins(14, 12, 14, 12)
        tc.setSpacing(8)
        tc.addWidget(QLabel("1.  Encryption tool"))
        tool_row = QHBoxLayout()
        tool_row.setSpacing(8)
        self.tool_path = QLineEdit()
        self.tool_path.setReadOnly(True)
        self.tool_path.setPlaceholderText(f"Locate {TOOL_NAME} ...")
        btn_find = QPushButton("Auto-find")
        btn_tool_browse = QPushButton("Browse...")
        btn_find.clicked.connect(self._on_autofind)
        btn_tool_browse.clicked.connect(self._on_browse_tool)
        tool_row.addWidget(self.tool_path, 1)
        tool_row.addWidget(btn_find)
        tool_row.addWidget(btn_tool_browse)
        tc.addLayout(tool_row)
        self.tool_status = QLabel("")
        self.tool_status.setObjectName("toolStatus")
        tc.addWidget(self.tool_status)
        outer.addWidget(tool_card)

        # ---- drop zone
        self.drop = QFrame()
        self.drop.setObjectName("dropZone")
        self.drop.setProperty("dragActive", "false")
        self.drop.setMinimumHeight(112)
        self.drop.setAcceptDrops(True)
        dz = QVBoxLayout(self.drop)
        dz.setSpacing(6)
        dz.setAlignment(Qt.AlignCenter)
        drop_title = QLabel("Drop your  .qplug  here")
        drop_title.setObjectName("dropTitle")
        drop_title.setAlignment(Qt.AlignCenter)
        drop_hint = QLabel("or use Browse below   ·   you can also drop the .exe to set the tool")
        drop_hint.setObjectName("dropHint")
        drop_hint.setAlignment(Qt.AlignCenter)
        dz.addWidget(drop_title)
        dz.addWidget(drop_hint)
        outer.addWidget(self.drop)

        # ---- input row
        in_row = QHBoxLayout()
        in_row.setSpacing(8)
        in_lbl = QLabel("Input")
        in_lbl.setFixedWidth(46)
        self.in_path = QLineEdit()
        self.in_path.setReadOnly(True)
        self.in_path.setPlaceholderText("No .qplug selected")
        btn_in_browse = QPushButton("Browse...")
        btn_in_browse.clicked.connect(self._on_browse_input)
        in_row.addWidget(in_lbl)
        in_row.addWidget(self.in_path, 1)
        in_row.addWidget(btn_in_browse)
        outer.addLayout(in_row)

        # ---- output row
        out_row = QHBoxLayout()
        out_row.setSpacing(8)
        out_lbl = QLabel("Output")
        out_lbl.setFixedWidth(46)
        self.out_path = QLineEdit()
        self.out_path.setPlaceholderText("auto-filled .qplugx path (editable)")
        btn_out_browse = QPushButton("Save as...")
        btn_out_browse.clicked.connect(self._on_browse_output)
        out_row.addWidget(out_lbl)
        out_row.addWidget(self.out_path, 1)
        out_row.addWidget(btn_out_browse)
        outer.addLayout(out_row)

        # ---- encrypt button
        self.btn_go = QPushButton("Encrypt  →  .qplugx")
        self.btn_go.setObjectName("primary")
        self.btn_go.clicked.connect(self._on_encrypt)
        outer.addWidget(self.btn_go)

        # ---- log
        self.log = QPlainTextEdit()
        self.log.setObjectName("log")
        self.log.setReadOnly(True)
        self.log.setMinimumHeight(120)
        self.log.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        outer.addWidget(self.log, 1)

        # ---- status line
        self.status = QLabel("Ready.")
        self.status.setObjectName("statusLine")
        self.status.setProperty("state", "info")
        outer.addWidget(self.status)

        # initial tool detection: prefer the bundled (built-in) tool, else the
        # quick deterministic lookup (no disk walk on startup).
        builtin = bundled_tool()
        if builtin:
            self._set_tool(builtin, bundled=True)
        else:
            saved = self._settings.value("toolPath", None)
            hit = find_tool_quick(saved if isinstance(saved, str) else None)
            self._set_tool(hit)

    # ----- state helpers ---------------------------------------------------- #
    def _set_status(self, msg: str, state: str) -> None:
        self.status.setText(msg)
        self.status.setProperty("state", state)
        _repolish(self.status)

    def _set_tool(self, path: str | None, *, bundled: bool = False) -> None:
        if path and Path(path).is_file():
            self._tool = str(Path(path).resolve())
            if bundled:
                # _MEIPASS path is a per-launch temp dir - show a friendly label
                # and do NOT persist it to settings (it changes every run).
                self.tool_path.setText("(built-in)  " + TOOL_NAME)
                self.tool_status.setText("✓  Built-in encryption tool (bundled)")
            else:
                self.tool_path.setText(self._tool)
                self.tool_status.setText("✓  Tool found")
                self._settings.setValue("toolPath", self._tool)
            self.tool_status.setProperty("state", "ok")
        else:
            self._tool = None
            self.tool_path.clear()
            self.tool_status.setText(
                "✗  Tool not set — Auto-find, Browse, or drop plugin_tool_release.exe here"
            )
            self.tool_status.setProperty("state", "err")
        _repolish(self.tool_status)

    def _set_input(self, path: str) -> None:
        p = Path(path)
        if not p.is_file():
            return
        self._infile = str(p.resolve())
        self.in_path.setText(self._infile)
        self.out_path.setText(str(p.with_suffix(".qplugx").resolve()))
        if p.suffix.lower() != ".qplug":
            self._set_status(
                f"Note: '{p.suffix}' is not a .qplug — encrypt anyway if you're sure.", "err"
            )
        else:
            self._set_status("Input loaded.", "ok")

    def _handle_paths(self, paths: list[str]) -> None:
        """Route dropped/selected files by extension."""
        for raw in paths:
            ext = Path(raw).suffix.lower()
            if ext == ".exe":
                self._set_tool(raw)
            elif ext == ".qplugx":
                continue  # already encrypted
            else:
                self._set_input(raw)  # .qplug (or anything else) -> input

    # ----- drag & drop ------------------------------------------------------ #
    def dragEnterEvent(self, event) -> None:  # noqa: N802 (Qt naming)
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.drop.setProperty("dragActive", "true")
            _repolish(self.drop)

    def dragLeaveEvent(self, event) -> None:  # noqa: N802
        self.drop.setProperty("dragActive", "false")
        _repolish(self.drop)

    def dropEvent(self, event) -> None:  # noqa: N802
        self.drop.setProperty("dragActive", "false")
        _repolish(self.drop)
        paths = [u.toLocalFile() for u in event.mimeData().urls() if u.isLocalFile()]
        if paths:
            self._handle_paths(paths)

    # ----- button handlers -------------------------------------------------- #
    def _on_browse_tool(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Locate plugin_tool_release.exe", "",
            f"Encryption tool ({TOOL_NAME});;Executables (*.exe);;All files (*)",
        )
        if path:
            self._set_tool(path)

    def _on_autofind(self) -> None:
        self._set_status("Searching common folders...", "busy")
        QApplication.processEvents()
        hit = find_tool_quick(None) or find_tool_deep()
        if hit:
            self._set_tool(hit)
            self._set_status("Tool found.", "ok")
        else:
            self._set_status("Tool not found — use Browse to locate it.", "err")

    def _on_browse_input(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Select a .qplug to encrypt", "",
            "Q-SYS plugin (*.qplug);;All files (*)",
        )
        if path:
            self._set_input(path)

    def _on_browse_output(self) -> None:
        start = self.out_path.text() or ""
        path, _ = QFileDialog.getSaveFileName(
            self, "Save encrypted plugin as", start,
            "Encrypted Q-SYS plugin (*.qplugx);;All files (*)",
        )
        if path:
            self.out_path.setText(path)

    def _on_encrypt(self) -> None:
        if not (self._tool and Path(self._tool).is_file()):
            self._set_status("No encryption tool selected.", "err")
            return
        if not (self._infile and Path(self._infile).is_file()):
            self._set_status("No input .qplug selected.", "err")
            return
        out = self.out_path.text().strip()
        if not out:
            self._set_status("No output path.", "err")
            return

        if Path(out).exists():
            ans = QMessageBox.question(
                self, "Overwrite?",
                f"Output already exists:\n{out}\n\nOverwrite it?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No,
            )
            if ans != QMessageBox.Yes:
                self._set_status("Cancelled.", "err")
                return
            try:
                Path(out).unlink()
            except OSError as exc:
                self._set_status(f"Couldn't remove existing output: {exc}", "err")
                return

        self.log.clear()
        self.btn_go.setEnabled(False)
        self._set_status("Encrypting...", "busy")

        self._worker = EncryptWorker(self._tool, self._infile, out)
        self._worker.log.connect(self._append_log)
        self._worker.result.connect(self._on_result)
        self._worker.finished.connect(self._worker.deleteLater)
        self._worker.finished.connect(self._clear_worker_ref)
        self._worker.start()

    # ----- worker slots (run on the UI thread) ------------------------------ #
    def _append_log(self, line: str) -> None:
        self.log.appendPlainText(line)

    def _on_result(self, ok: bool, message: str) -> None:
        self.btn_go.setEnabled(True)
        self._set_status(("✓  " if ok else "✗  ") + message, "ok" if ok else "err")

    def _clear_worker_ref(self) -> None:
        self._worker = None


def main() -> int:
    # Headless self-check (used by CI / local build verification): reports whether
    # the QSC tool is bundled, then exits without opening a window.
    if "--selftest" in sys.argv:
        bt = bundled_tool()
        try:  # stdout may be None in a windowed (console=False) frozen build
            print(f"bundled_tool: {bt}")
            print(f"icon: {icon_path()}")
        except Exception:
            pass
        return 0 if bt else 3

    QApplication.setApplicationName("Q-SYS Plugin Encryptor")
    app = QApplication(sys.argv)
    app.setStyleSheet(QSS)
    ico = icon_path()
    if ico:
        icon = QIcon(str(ico))
        app.setWindowIcon(icon)
    win = MainWindow()
    if ico:
        win.setWindowIcon(QIcon(str(ico)))
    win.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
