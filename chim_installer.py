#!/usr/bin/env python3
"""
CHIM Installer — Oblivion Remastered Modpack
A guided installer for Linux desktop and Steam Deck (Desktop Mode).
Requires: Python 3.8+, tkinter (standard library)
Optional: p7zip, unrar (for .7z/.rar extraction)
"""

import os
import sys
import glob
import shutil
import zipfile
import subprocess
import webbrowser
import tempfile
import re
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from typing import Optional

# ─── Mod Database ───────────────────────────────────────────────────────────────

MODS = [
    # Bug Fixes & Framework
    {"name": "OBSE64", "nexus_id": 282, "type": "obse_framework", "category": "Bug Fixes & Framework"},
    {"name": "Address Library", "nexus_id": 4475, "type": "obse", "category": "Bug Fixes & Framework"},
    {"name": "UE4SS", "nexus_id": 32, "type": "ue4ss_framework", "category": "Bug Fixes & Framework"},
    {"name": "Unofficial Oblivion Remastered Patch", "nexus_id": 477, "type": "esp", "category": "Bug Fixes & Framework"},
    {"name": "Oblivion Unreal Fixes", "nexus_id": 4676, "type": "pak", "category": "Bug Fixes & Framework"},
    {"name": "ActiveEffectsFix", "nexus_id": 4994, "type": "obse", "category": "Bug Fixes & Framework"},
    {"name": "Baka Achievement Enabler", "nexus_id": 145, "type": "obse", "category": "Bug Fixes & Framework"},
    {"name": "Difficulty Slider Fixed", "nexus_id": 58, "type": "esp", "category": "Bug Fixes & Framework"},
    {"name": "RainFPSFix", "nexus_id": 566, "type": "esp", "category": "Bug Fixes & Framework"},
    # Visuals & Lighting
    {"name": "Shaders Revised", "nexus_id": 1528, "type": "ue4ss", "category": "Visuals & Lighting"},
    {"name": "Lumen Remastered", "nexus_id": 1129, "type": "ue4ss", "category": "Visuals & Lighting"},
    {"name": "Lumiere", "nexus_id": 3100, "type": "esp", "category": "Visuals & Lighting"},
    {"name": "Eternal Darkness", "nexus_id": 5136, "type": "ue4ss", "category": "Visuals & Lighting"},
    {"name": "Ultra Plus", "nexus_id": 27, "type": "ue4ss", "category": "Visuals & Lighting"},
    {"name": "Young Textures Revamped", "nexus_id": 445, "type": "pak", "category": "Visuals & Lighting"},
    {"name": "Greener Grass", "nexus_id": 2279, "type": "pak", "category": "Visuals & Lighting"},
    {"name": "Connor's Flora", "nexus_id": 4740, "type": "pak", "category": "Visuals & Lighting"},
    {"name": "NPC Overhaul AIO", "nexus_id": 3096, "type": "ue4ss", "category": "Visuals & Lighting"},
    {"name": "8K Color World Map", "nexus_id": 944, "type": "pak", "category": "Visuals & Lighting"},
    {"name": "Brighter Torches 1.5x", "nexus_id": 2821, "type": "pak", "category": "Visuals & Lighting"},
    # Camera & Animations
    {"name": "Improved Camera", "nexus_id": 2362, "type": "pak", "category": "Camera & Animations"},
    {"name": "Pelinal's Edge", "nexus_id": 4781, "type": "pak", "category": "Camera & Animations"},
    {"name": "Morihaus Might", "nexus_id": 4318, "type": "pak", "category": "Camera & Animations"},
    {"name": "Longsword Overhaul", "nexus_id": 4541, "type": "pak", "category": "Camera & Animations"},
    {"name": "Shortsword Anticipation", "nexus_id": 2489, "type": "pak", "category": "Camera & Animations"},
    # Combat & Magic
    {"name": "UltraCombat V2", "nexus_id": 4244, "type": "ue4ss", "category": "Combat & Magic"},
    {"name": "Responsive Combat AI", "nexus_id": 2792, "type": "esp", "category": "Combat & Magic"},
    {"name": "Responsive Spellcaster AI", "nexus_id": 5197, "type": "esp", "category": "Combat & Magic"},
    {"name": "Supreme Magicka", "nexus_id": 1098, "type": "esp", "category": "Combat & Magic"},
    {"name": "Nascent Archery", "nexus_id": 2149, "type": "esp", "category": "Combat & Magic"},
    {"name": "Magic Skill Leveling Fixed", "nexus_id": 3965, "type": "esp", "category": "Combat & Magic"},
    # AI & World
    {"name": "NPCs Come to Life", "nexus_id": 3363, "type": "esp", "category": "AI & World"},
    {"name": "Dynamic AI Animals", "nexus_id": 2228, "type": "esp", "category": "AI & World"},
    {"name": "Climates Revised", "nexus_id": 791, "type": "esp", "category": "AI & World"},
    {"name": "Balanced NPC Level Cap", "nexus_id": 182, "type": "esp", "category": "AI & World"},
    {"name": "Quest NPCs Run", "nexus_id": 219, "type": "esp", "category": "AI & World"},
    # Items & Progression
    {"name": "Auto Upgrade Leveled Items", "nexus_id": 567, "type": "esp", "category": "Items & Progression"},
    {"name": "No Durability Damage", "nexus_id": 109, "type": "esp", "category": "Items & Progression"},
    {"name": "No Enchantment Drain", "nexus_id": 1253, "type": "obse", "category": "Items & Progression"},
    {"name": "Carry Weight + Weightless Misc", "nexus_id": 1734, "type": "ue4ss", "category": "Items & Progression"},
    # Spells & Powers
    {"name": "Spell Duration x10", "nexus_id": 1087, "type": "esp", "category": "Spells & Powers"},
    {"name": "Unlimited Powers", "nexus_id": 1461, "type": "esp", "category": "Spells & Powers"},
    {"name": "Spell Freedom", "nexus_id": 138, "type": "esp", "category": "Spells & Powers"},
    # UI & Quality of Life
    {"name": "Better HUD Slim", "nexus_id": 13, "type": "pak", "category": "UI & Quality of Life"},
    {"name": "MISS Inventory Sorter", "nexus_id": 3288, "type": "ue4ss", "category": "UI & Quality of Life"},
    {"name": "Auto Local Map", "nexus_id": 1119, "type": "ue4ss", "category": "UI & Quality of Life"},
    {"name": "Additional Map Markers", "nexus_id": 479, "type": "esp", "category": "UI & Quality of Life"},
    {"name": "Horse Whistle", "nexus_id": 153, "type": "esp", "category": "UI & Quality of Life"},
    {"name": "Easier Persuasion", "nexus_id": 3393, "type": "esp", "category": "UI & Quality of Life"},
    {"name": "Better Auto Lockpick", "nexus_id": 418, "type": "esp", "category": "UI & Quality of Life"},
    {"name": "Richer Vendors", "nexus_id": 96, "type": "esp", "category": "UI & Quality of Life"},
    {"name": "PreserveStats", "nexus_id": 783, "type": "esp", "category": "UI & Quality of Life"},
    {"name": "Quieter Lockpicking", "nexus_id": 1788, "type": "pak", "category": "UI & Quality of Life"},
    # Audio
    {"name": "High Quality Music Replacer", "nexus_id": 1267, "type": "pak", "category": "Audio"},
    # New Content
    {"name": "Dark Brotherhood Infinitum", "nexus_id": 3170, "type": "esp", "category": "New Content"},
    {"name": "Imperial Legion Infinitum", "nexus_id": 4225, "type": "esp", "category": "New Content"},
    {"name": "Advanced Followers", "nexus_id": 722, "type": "esp", "category": "New Content"},
    {"name": "Lakeheart Manor", "nexus_id": 763, "type": "esp", "category": "New Content"},
    {"name": "Radiant Mages Guild Quests", "nexus_id": 3858, "type": "esp", "category": "New Content"},
]

# ─── Deck Optimization Mods (replaces visual mods on Steam Deck) ─────────────

DECK_OPTIMIZATION_MODS = [
    {"name": "LUMEN BEGONE", "nexus_id": 183, "type": "pak", "category": "Deck Optimization"},
    {"name": "No More VRAM Leaks", "nexus_id": 399, "type": "ue4ss", "category": "Deck Optimization"},
    {"name": "4GB GPU Optimization", "nexus_id": 245, "type": "config", "category": "Deck Optimization"},
    {"name": "Optimax (4GB Low Preset)", "nexus_id": 488, "type": "config", "category": "Deck Optimization"},
    {"name": "Oblivion Optimizer", "nexus_id": 39, "type": "config", "category": "Deck Optimization"},
    {"name": "Actual Stuttering Fix", "nexus_id": 1776, "type": "config", "category": "Deck Optimization"},
    {"name": "Simply No Fog", "nexus_id": 1429, "type": "pak", "category": "Deck Optimization"},
]

# Nexus IDs to EXCLUDE on Steam Deck (heavy visual mods that tank performance)
DECK_EXCLUDE_IDS = {
    944,   # 8K Color World Map — 30MB texture at 800p is pointless
    2279,  # Greener Grass — 108MB, extra foliage geometry
    445,   # Young Textures Revamped — unnecessary at 800p
    4740,  # Connor's Flora — more vegetation = more frame drops
    1528,  # Shaders Revised — extra post-processing overhead
    1129,  # Lumen Remastered — RT enhancement, Deck can't handle RT
    3096,  # NPC Overhaul AIO — extra texture load
    2821,  # Brighter Torches 1.5x — minor but unnecessary visual load
    27,    # Ultra Plus — graphics framework, opposite of what Deck needs
    5136,  # Eternal Darkness — shader-heavy darker nights
    1267,  # High Quality Music Replacer — 55MB audio, saves storage
}

# Install profile constants
PROFILE_PC = "pc"
PROFILE_DECK = "deck"

NEXUS_GAME_DOMAIN = "oblivionremastered"
NEXUS_BASE = f"https://www.nexusmods.com/{NEXUS_GAME_DOMAIN}/mods"

# ─── Theme ──────────────────────────────────────────────────────────────────────

COLORS = {
    "bg":           "#0a0a0a",
    "bg_light":     "#141414",
    "bg_lighter":   "#1e1e1e",
    "bg_row_alt":   "#121218",
    "gold":         "#c9a84c",
    "gold_dim":     "#8a7333",
    "gold_bright":  "#e6c65a",
    "text":         "#d4d4d4",
    "text_dim":     "#888888",
    "text_bright":  "#f0f0f0",
    "green":        "#4caf50",
    "green_dim":    "#2e7d32",
    "red":          "#cf6679",
    "blue":         "#5c9fd6",
    "border":       "#2a2a2a",
    "progress_bg":  "#1a1a1a",
    "progress_fg":  "#c9a84c",
    "btn_bg":       "#1e1e1e",
    "btn_hover":    "#2a2a2a",
    "btn_active":   "#333333",
    "scrollbar":    "#333333",
    "scrollbar_bg": "#0f0f0f",
}

CATEGORY_ICONS = {
    "Bug Fixes & Framework":  "\u2699",  # ⚙
    "Visuals & Lighting":     "\u2728",  # ✨
    "Camera & Animations":    "\u25ce",  # ◎
    "Combat & Magic":         "\u2694",  # ⚔
    "AI & World":             "\u263a",  # ☺
    "Items & Progression":    "\u2b50",  # ⭐
    "Spells & Powers":        "\u269b",  # ⚛
    "UI & Quality of Life":   "\u2630",  # ☰
    "Audio":                  "\u266b",  # ♫
    "New Content":            "\u2726",  # ✦
}

STATUS_PENDING    = "pending"
STATUS_WAITING    = "waiting"
STATUS_DOWNLOADED = "downloaded"
STATUS_SKIPPED    = "skipped"
STATUS_INSTALLED  = "installed"

CATEGORY_ICONS["Deck Optimization"] = "\u26a1"  # ⚡


# ─── Helpers ────────────────────────────────────────────────────────────────────

def is_gaming_mode() -> bool:
    """Check if running inside Steam Deck Gaming Mode (Gamescope session)."""
    if os.environ.get("GAMESCOPE_WAYLAND_DISPLAY"):
        return True
    xdg = os.environ.get("XDG_CURRENT_DESKTOP", "").lower()
    if "gamescope" in xdg:
        return True
    session = os.environ.get("XDG_SESSION_DESKTOP", "").lower()
    if "gamescope" in session:
        return True
    return False


def is_steam_deck() -> bool:
    """Detect if running on Steam Deck hardware (regardless of mode)."""
    # Check for deck user
    if Path("/home/deck").is_dir():
        return True
    # Check for SteamOS
    if "steamos" in os.environ.get("XDG_CURRENT_DESKTOP", "").lower():
        return True
    # Check DMI product name
    try:
        product = Path("/sys/devices/virtual/dmi/id/product_name").read_text().strip().lower()
        if "jupiter" in product or "galileo" in product:  # LCD Deck / OLED Deck
            return True
    except (FileNotFoundError, PermissionError):
        pass
    return False


def detect_game_path() -> Optional[str]:
    """Try common Oblivion Remastered install locations."""
    home = Path.home()
    candidates = [
        home / ".local/share/Steam/steamapps/common/Oblivion Remastered",
        Path("/home/deck/.local/share/Steam/steamapps/common/Oblivion Remastered"),
        home / ".steam/steam/steamapps/common/Oblivion Remastered",
        home / ".var/app/com.valvesoftware.Steam/.local/share/Steam/steamapps/common/Oblivion Remastered",
    ]
    for p in candidates:
        if p.is_dir():
            return str(p)
    return None


def nexus_url(nexus_id: int) -> str:
    return f"{NEXUS_BASE}/{nexus_id}?tab=files"


def get_downloads_dir() -> Path:
    """Return the user's Downloads directory."""
    xdg = os.environ.get("XDG_DOWNLOAD_DIR")
    if xdg and Path(xdg).is_dir():
        return Path(xdg)
    d = Path.home() / "Downloads"
    d.mkdir(exist_ok=True)
    return d


def mod_filename_patterns(mod: dict) -> list[str]:
    """
    Generate regex patterns that match Nexus download filenames for a mod.
    Nexus filenames look like: 'Mod Name-NEXUSID-VERSION.zip'
    or sometimes just 'something-NEXUSID-*.zip'
    """
    nid = str(mod["nexus_id"])
    # Match any archive containing the nexus ID in the filename
    return [
        rf".*[-_ ]{re.escape(nid)}[-_ v].*\.(zip|7z|rar)$",
        rf"^{re.escape(nid)}[-_ ].*\.(zip|7z|rar)$",
    ]


def find_downloaded_file(mod: dict, downloads_dir: Path) -> Optional[Path]:
    """Check if an archive matching this mod exists in downloads dir."""
    nid = str(mod["nexus_id"])
    if not downloads_dir.is_dir():
        return None
    for f in downloads_dir.iterdir():
        if not f.is_file():
            continue
        name = f.name.lower()
        if not name.endswith((".zip", ".7z", ".rar")):
            continue
        # Nexus convention: name contains the mod ID surrounded by dashes or spaces
        if re.search(rf'(^|[-_ ]){re.escape(nid)}([-_ v.])', f.name):
            return f
    return None


def find_7z() -> Optional[str]:
    """Find 7z binary — bundled first, then system."""
    base = Path(getattr(sys, '_MEIPASS', None) or Path(__file__).parent)
    # Check for bundled binaries (Linux: 7zzs, Windows: 7za.exe)
    for name in ("7zzs", "7za.exe", "7za", "7zz"):
        bundled = base / name
        if bundled.is_file():
            return str(bundled)
    # Fall back to system PATH
    for name in ("7z", "7za", "7zz", "7zzs"):
        found = shutil.which(name)
        if found:
            return found
    return None


def extract_archive(archive_path: Path, dest_dir: Path) -> bool:
    """Extract an archive to dest_dir. Returns True on success."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    name = archive_path.name.lower()

    if name.endswith(".zip"):
        try:
            with zipfile.ZipFile(archive_path, "r") as zf:
                zf.extractall(dest_dir)
            return True
        except (zipfile.BadZipFile, Exception):
            return False

    elif name.endswith(".7z"):
        exe = find_7z()
        if not exe:
            return False
        try:
            subprocess.run(
                [exe, "x", str(archive_path), f"-o{dest_dir}", "-y"],
                check=True, capture_output=True, timeout=300,
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            return False

    elif name.endswith(".rar"):
        exe = shutil.which("unrar")
        if not exe:
            # Try bundled/system 7z as fallback for rar
            exe = find_7z()
            if exe:
                try:
                    subprocess.run(
                        [exe, "x", str(archive_path), f"-o{dest_dir}", "-y"],
                        check=True, capture_output=True, timeout=300,
                    )
                    return True
                except Exception:
                    return False
            return False
        try:
            subprocess.run(
                [exe, "x", str(archive_path), str(dest_dir), "-y"],
                check=True, capture_output=True, timeout=300,
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            return False

    return False


def classify_and_install_files(
    extracted_dir: Path,
    game_path: Path,
    mod_type: str,
    mod_name: str,
) -> tuple[int, list[str]]:
    """
    Walk extracted files and copy them to the correct game directories.
    Returns (files_installed, list_of_errors).
    """
    data_dir = game_path / "OblivionRemastered" / "Content" / "Dev" / "ObvData" / "Data"
    paks_dir = game_path / "OblivionRemastered" / "Content" / "Paks" / "~mods"
    obse_dir = game_path / "OblivionRemastered" / "Binaries" / "Win64" / "OBSE" / "Plugins"
    ue4ss_mods_dir = game_path / "OblivionRemastered" / "Binaries" / "Win64" / "ue4ss" / "Mods"
    bin_dir = game_path / "OblivionRemastered" / "Binaries" / "Win64"

    installed = 0
    errors = []

    # Ensure target dirs exist
    for d in [data_dir, paks_dir, obse_dir, ue4ss_mods_dir]:
        d.mkdir(parents=True, exist_ok=True)

    all_files = list(extracted_dir.rglob("*"))
    # Filter out directories
    all_files = [f for f in all_files if f.is_file()]

    if mod_type == "obse_framework":
        # OBSE64: copy everything preserving structure relative to the OBSE root.
        # Typically contains: obse64_loader.exe, obse64_steam_loader.dll, Data/OBSE/Plugins/
        # The exe/dll go to Binaries/Win64, the Data subfolder goes to Data
        for f in all_files:
            rel = f.relative_to(extracted_dir)
            parts = rel.parts
            # Strip leading folder if it looks like a version wrapper (e.g. "obse64_0_1_2")
            if len(parts) > 1 and parts[0].lower().startswith("obse"):
                rel = Path(*parts[1:])
                parts = rel.parts

            ext = f.suffix.lower()
            name_lower = f.name.lower()

            if ext in (".exe", ".dll") and "obse" in name_lower:
                dest = bin_dir / f.name
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(f, dest)
                installed += 1
            elif ext in (".dll", ".ini") and "obse" not in name_lower:
                # Plugin files
                dest = obse_dir / f.name
                shutil.copy2(f, dest)
                installed += 1
            elif ext in (".esp", ".esm"):
                dest = data_dir / f.name
                shutil.copy2(f, dest)
                installed += 1
            elif "data" in str(rel).lower() and "obse" in str(rel).lower():
                # Preserve subdirectory structure under OBSE/Plugins
                # Find the "Plugins" part and keep everything after
                rel_str = str(rel)
                idx = rel_str.lower().find("plugins")
                if idx >= 0:
                    after = rel_str[idx + len("plugins"):].lstrip("/\\")
                    dest = obse_dir / after if after else obse_dir / f.name
                else:
                    dest = obse_dir / f.name
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(f, dest)
                installed += 1
            else:
                # Fallback: copy to bin dir preserving relative path
                dest = bin_dir / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(f, dest)
                installed += 1
        return installed, errors

    if mod_type == "ue4ss_framework":
        # UE4SS framework: copy everything to Binaries/Win64/ preserving structure
        # Find root (may have a wrapper folder)
        root = extracted_dir
        subdirs = [d for d in extracted_dir.iterdir() if d.is_dir()]
        # If there's exactly one subfolder and no loose important files, unwrap
        loose_files = [f for f in extracted_dir.iterdir() if f.is_file() and f.suffix.lower() in (".dll", ".exe", ".ini")]
        if len(subdirs) == 1 and not loose_files:
            root = subdirs[0]

        for f in root.rglob("*"):
            if not f.is_file():
                continue
            rel = f.relative_to(root)
            dest = bin_dir / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, dest)
            installed += 1
        return installed, errors

    # For standard mod types, find the "real" root of extracted content
    # (skip single wrapper directories)
    content_root = extracted_dir
    while True:
        children = list(content_root.iterdir())
        dirs = [c for c in children if c.is_dir()]
        files = [c for c in children if c.is_file()]
        if len(dirs) == 1 and len(files) == 0:
            content_root = dirs[0]
        else:
            break

    all_files = [f for f in content_root.rglob("*") if f.is_file()]

    if mod_type == "esp":
        for f in all_files:
            ext = f.suffix.lower()
            if ext in (".esp", ".esm"):
                dest = data_dir / f.name
                shutil.copy2(f, dest)
                installed += 1
            elif ext == ".bsa":
                dest = data_dir / f.name
                shutil.copy2(f, dest)
                installed += 1
            elif ext in (".ini",):
                # INI files that accompany ESPs go to Data
                dest = data_dir / f.name
                shutil.copy2(f, dest)
                installed += 1

    elif mod_type == "pak":
        for f in all_files:
            ext = f.suffix.lower()
            if ext in (".pak", ".ucas", ".utoc"):
                dest = paks_dir / f.name
                shutil.copy2(f, dest)
                installed += 1
            elif ext in (".esp", ".esm"):
                dest = data_dir / f.name
                shutil.copy2(f, dest)
                installed += 1

    elif mod_type == "obse":
        for f in all_files:
            ext = f.suffix.lower()
            if ext in (".dll", ".ini"):
                dest = obse_dir / f.name
                shutil.copy2(f, dest)
                installed += 1
            elif ext in (".esp", ".esm"):
                dest = data_dir / f.name
                shutil.copy2(f, dest)
                installed += 1

    elif mod_type == "ue4ss":
        # UE4SS mods go into ue4ss/Mods/<ModName>/
        mod_dir = ue4ss_mods_dir / mod_name.replace(" ", "")
        mod_dir.mkdir(parents=True, exist_ok=True)

        # Check if extracted content already has the expected UE4SS structure
        # (contains scripts/ or dlls/ or a main.lua or enabled.txt)
        has_structure = any(
            f.name.lower() in ("main.lua", "enabled.txt") or
            f.parent.name.lower() in ("scripts", "dlls")
            for f in all_files
        )

        for f in all_files:
            ext = f.suffix.lower()
            rel = f.relative_to(content_root)

            if ext in (".esp", ".esm"):
                dest = data_dir / f.name
                shutil.copy2(f, dest)
                installed += 1
            elif ext in (".pak", ".ucas", ".utoc"):
                dest = paks_dir / f.name
                shutil.copy2(f, dest)
                installed += 1
            else:
                if has_structure:
                    dest = mod_dir / rel
                else:
                    dest = mod_dir / f.name
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(f, dest)
                installed += 1

        # Ensure enabled.txt exists
        enabled = mod_dir / "enabled.txt"
        if not enabled.exists():
            enabled.write_text("1\n")

    elif mod_type == "config":
        # Config/optimization mods — ini files go to various locations
        for f in all_files:
            ext = f.suffix.lower()
            name_lower = f.name.lower()
            if ext == ".ini":
                if "engine" in name_lower:
                    # Engine.ini goes to saved config dir (handled separately for Deck)
                    dest = bin_dir / f.name
                elif "gameusersettings" in name_lower:
                    dest = bin_dir / f.name
                else:
                    dest = bin_dir / f.name
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(f, dest)
                installed += 1
            elif ext in (".pak", ".ucas", ".utoc"):
                dest = paks_dir / f.name
                shutil.copy2(f, dest)
                installed += 1
            elif ext in (".cfg", ".txt", ".json"):
                dest = bin_dir / f.name
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(f, dest)
                installed += 1

    if installed == 0:
        errors.append(f"No recognized files found in archive for {mod_name}")

    return installed, errors


# ─── Custom Widgets ─────────────────────────────────────────────────────────────

class GoldButton(tk.Canvas):
    """A custom button with gold border, hover effects, and clean styling."""

    def __init__(self, parent, text="", command=None, width=200, height=40,
                 font_size=11, enabled=True, accent=None, **kwargs):
        super().__init__(
            parent, width=width, height=height,
            bg=COLORS["bg"], highlightthickness=0, **kwargs,
        )
        self._text = text
        self._command = command
        self._width = width
        self._height = height
        self._font_size = font_size
        self._enabled = enabled
        self._hovered = False
        self._accent = accent or COLORS["gold"]
        self._accent_dim = accent or COLORS["gold_dim"]

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)

        self._draw()

    def _draw(self):
        self.delete("all")
        w, h = self._width, self._height
        r = 6  # corner radius

        if self._enabled:
            border_color = self._accent if self._hovered else self._accent_dim
            fill = COLORS["btn_hover"] if self._hovered else COLORS["btn_bg"]
            text_color = COLORS["text_bright"] if self._hovered else COLORS["text"]
        else:
            border_color = COLORS["border"]
            fill = COLORS["bg_light"]
            text_color = COLORS["text_dim"]

        # Rounded rectangle via polygon
        self._round_rect(2, 2, w - 2, h - 2, r, outline=border_color, fill=fill, width=1.5)

        self.create_text(
            w // 2, h // 2, text=self._text,
            fill=text_color, font=("Segoe UI", self._font_size),
        )

    def _round_rect(self, x1, y1, x2, y2, r, **kwargs):
        points = [
            x1 + r, y1,
            x2 - r, y1,
            x2, y1,
            x2, y1 + r,
            x2, y2 - r,
            x2, y2,
            x2 - r, y2,
            x1 + r, y2,
            x1, y2,
            x1, y2 - r,
            x1, y1 + r,
            x1, y1,
            x1 + r, y1,
        ]
        self.create_polygon(points, smooth=True, **kwargs)

    def _on_enter(self, e):
        if self._enabled:
            self._hovered = True
            self.config(cursor="hand2")
            self._draw()

    def _on_leave(self, e):
        self._hovered = False
        self.config(cursor="")
        self._draw()

    def _on_press(self, e):
        if self._enabled:
            self.config(cursor="hand2")

    def _on_release(self, e):
        if self._enabled and self._command:
            self._command()

    def set_enabled(self, enabled: bool):
        self._enabled = enabled
        self._draw()

    def set_text(self, text: str):
        self._text = text
        self._draw()


class ProgressBar(tk.Canvas):
    """Custom gold-themed progress bar."""

    def __init__(self, parent, width=700, height=22, **kwargs):
        super().__init__(
            parent, width=width, height=height,
            bg=COLORS["bg"], highlightthickness=0, **kwargs,
        )
        self._width = width
        self._height = height
        self._value = 0.0
        self._draw()

    def _draw(self):
        self.delete("all")
        w, h = self._width, self._height
        r = h // 2

        # Background track
        self._round_rect(0, 0, w, h, r, fill=COLORS["progress_bg"], outline=COLORS["border"])

        # Filled portion
        if self._value > 0:
            fw = max(h, int(w * self._value))
            self._round_rect(0, 0, fw, h, r, fill=COLORS["progress_fg"], outline="")

        # Percentage text
        pct = int(self._value * 100)
        self.create_text(
            w // 2, h // 2, text=f"{pct}%",
            fill=COLORS["text_bright"] if self._value > 0.4 else COLORS["text"],
            font=("Segoe UI", 9, "bold"),
        )

    def _round_rect(self, x1, y1, x2, y2, r, **kwargs):
        points = [
            x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r,
            x2, y2 - r, x2, y2, x2 - r, y2, x1 + r, y2,
            x1, y2, x1, y2 - r, x1, y1 + r, x1, y1, x1 + r, y1,
        ]
        self.create_polygon(points, smooth=True, **kwargs)

    def set_value(self, value: float):
        self._value = max(0.0, min(1.0, value))
        self._draw()


# ─── Main Application ──────────────────────────────────────────────────────────

class CHIMInstaller:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("CHIM  —  Oblivion Remastered Modpack Installer")
        self.root.configure(bg=COLORS["bg"])
        self.root.resizable(False, False)

        # Window size and centering
        ww, wh = 800, 600
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw - ww) // 2
        y = (sh - wh) // 2
        self.root.geometry(f"{ww}x{wh}+{x}+{y}")

        # State
        self.game_path: Optional[str] = None
        self.downloads_dir = get_downloads_dir()
        self.mod_status: dict[int, str] = {}  # nexus_id -> status
        self.mod_files: dict[int, Optional[Path]] = {}  # nexus_id -> downloaded file path
        self.current_mod_index = 0
        self._watcher_running = False
        self._watcher_id = None
        self.profile = PROFILE_DECK if is_steam_deck() else PROFILE_PC
        self.dry_run = False
        self.install_log_lines: list[str] = []
        self.active_mods: list[dict] = list(MODS)

        # Initialize all mod statuses
        self._init_mod_status()

    def _init_mod_status(self):
        self.mod_status.clear()
        self.mod_files.clear()
        self._build_active_mods()
        for mod in self.active_mods:
            self.mod_status[mod["nexus_id"]] = STATUS_PENDING
            self.mod_files[mod["nexus_id"]] = None

    def _build_active_mods(self):
        """Build the mod list for the current profile and store it."""
        if self.profile == PROFILE_DECK:
            filtered = [m for m in MODS if m["nexus_id"] not in DECK_EXCLUDE_IDS]
            self.active_mods = filtered + DECK_OPTIMIZATION_MODS
        else:
            self.active_mods = list(MODS)

        # Main container
        self.container = tk.Frame(self.root, bg=COLORS["bg"])
        self.container.pack(fill="both", expand=True)

        # Start with welcome screen
        self._show_welcome()

    def _clear_container(self):
        for w in self.container.winfo_children():
            w.destroy()
        self._stop_watcher()

    def _make_label(self, parent, text, size=11, color=None, bold=False, **kwargs):
        weight = "bold" if bold else "normal"
        return tk.Label(
            parent, text=text, bg=COLORS["bg"],
            fg=color or COLORS["text"],
            font=("Segoe UI", size, weight),
            **kwargs,
        )

    def _make_separator(self, parent):
        sep = tk.Frame(parent, bg=COLORS["border"], height=1)
        sep.pack(fill="x", padx=40, pady=8)
        return sep

    # ─── Welcome Screen ────────────────────────────────────────────────────

    def _show_welcome(self):
        self._clear_container()
        frame = tk.Frame(self.container, bg=COLORS["bg"])
        frame.pack(expand=True)

        # Title
        tk.Label(
            frame, text="C  H  I  M", bg=COLORS["bg"], fg=COLORS["gold"],
            font=("Segoe UI", 42, "bold"),
        ).pack(pady=(0, 4))

        # Subtitle
        tk.Label(
            frame, text="Oblivion Remastered Modpack", bg=COLORS["bg"],
            fg=COLORS["text_dim"], font=("Segoe UI", 14),
        ).pack(pady=(0, 30))

        # Horizontal gold line
        line = tk.Frame(frame, bg=COLORS["gold_dim"], height=1, width=300)
        line.pack(pady=(0, 30))

        # Description
        desc = (
            "A curated collection of 59 mods for Oblivion Remastered.\n"
            "Bug fixes, visual upgrades, combat overhaul, quality-of-life,\n"
            "and new content  —  all tested for compatibility on Linux."
        )
        tk.Label(
            frame, text=desc, bg=COLORS["bg"], fg=COLORS["text"],
            font=("Segoe UI", 11), justify="center",
        ).pack(pady=(0, 10))

        # Platform note
        tk.Label(
            frame, text="Works on Desktop Linux and Steam Deck (Desktop Mode)",
            bg=COLORS["bg"], fg=COLORS["text_dim"], font=("Segoe UI", 9),
        ).pack(pady=(0, 40))

        # Begin button
        GoldButton(
            frame, text="Begin Installation", command=self._show_profile,
            width=240, height=46, font_size=13,
        ).pack()

        # Version
        tk.Label(
            frame, text="v1.0", bg=COLORS["bg"], fg=COLORS["border"],
            font=("Segoe UI", 9),
        ).pack(side="bottom", pady=(30, 0))

    # ─── Profile Selection Screen ─────────────────────────────────────────

    def _show_profile(self):
        self._clear_container()

        frame = tk.Frame(self.container, bg=COLORS["bg"])
        frame.pack(expand=True)

        self._make_label(frame, "Choose Your Profile", size=22, color=COLORS["gold"], bold=True).pack(pady=(0, 8))
        self._make_label(
            frame, "The installer will tailor the mod list to your hardware.",
            size=10, color=COLORS["text_dim"],
        ).pack(pady=(0, 30))

        # PC Profile card
        pc_frame = tk.Frame(frame, bg=COLORS["bg_light"], padx=20, pady=16,
                            highlightbackground=COLORS["gold_dim"], highlightthickness=1)
        pc_frame.pack(fill="x", padx=40, pady=(0, 12))

        tk.Label(pc_frame, text="CHIM  —  Full Experience", bg=COLORS["bg_light"],
                 fg=COLORS["gold"], font=("Segoe UI", 13, "bold")).pack(anchor="w")
        tk.Label(pc_frame, text="59 mods. Max quality visuals, combat overhaul, AI improvements,\n"
                 "QoL, and new content. For desktop Linux PCs with a dedicated GPU.",
                 bg=COLORS["bg_light"], fg=COLORS["text_dim"], font=("Segoe UI", 9),
                 justify="left").pack(anchor="w", pady=(4, 8))
        GoldButton(pc_frame, text="Select PC Profile", width=180, height=36, font_size=10,
                   command=lambda: self._set_profile(PROFILE_PC)).pack(anchor="w")

        # Deck Profile card
        deck_frame = tk.Frame(frame, bg=COLORS["bg_light"], padx=20, pady=16,
                              highlightbackground=COLORS["blue"], highlightthickness=1)
        deck_frame.pack(fill="x", padx=40, pady=(0, 12))

        deck_detected = " (DETECTED)" if is_steam_deck() else ""
        tk.Label(deck_frame, text=f"CHIM Deck  —  Max Optimization{deck_detected}",
                 bg=COLORS["bg_light"], fg=COLORS["blue"],
                 font=("Segoe UI", 13, "bold")).pack(anchor="w")
        tk.Label(deck_frame, text="Performance-first build. Strips heavy visual mods, adds VRAM fixes,\n"
                 "disables forced ray tracing, optimizes Engine.ini. Keeps all gameplay\n"
                 "mods. Makes the game actually playable at stable 30 FPS on Steam Deck.",
                 bg=COLORS["bg_light"], fg=COLORS["text_dim"], font=("Segoe UI", 9),
                 justify="left").pack(anchor="w", pady=(4, 8))
        GoldButton(deck_frame, text="Select Deck Profile", width=180, height=36, font_size=10,
                   accent=COLORS["blue"],
                   command=lambda: self._set_profile(PROFILE_DECK)).pack(anchor="w")

        # Dry run checkbox
        # Back button
        GoldButton(
            frame, text="\u2190  Back", command=self._show_welcome,
            width=100, height=34, font_size=9,
        ).pack(pady=(20, 0))

    def _set_profile(self, profile: str):
        self.profile = profile
        self._init_mod_status()
        self.current_mod_index = 0
        self._show_game_path()

    # ─── Game Path Screen ──────────────────────────────────────────────────

    def _show_game_path(self):
        self._clear_container()

        frame = tk.Frame(self.container, bg=COLORS["bg"])
        frame.pack(fill="both", expand=True, padx=50, pady=30)

        self._make_label(frame, "Game Location", size=22, color=COLORS["gold"], bold=True).pack(anchor="w", pady=(0, 6))
        self._make_label(
            frame,
            "The installer needs to know where Oblivion Remastered is installed.",
            size=10, color=COLORS["text_dim"],
        ).pack(anchor="w", pady=(0, 20))

        self._make_separator(frame)

        # Auto-detect
        detected = detect_game_path()
        if detected:
            self.game_path = detected

        status_color = COLORS["green"] if detected else COLORS["red"]
        status_text = "Auto-detected:" if detected else "Not found automatically."

        self._make_label(frame, status_text, size=10, color=status_color).pack(anchor="w", pady=(10, 4))

        # Path entry row
        path_row = tk.Frame(frame, bg=COLORS["bg"])
        path_row.pack(fill="x", pady=(0, 20))

        self._path_var = tk.StringVar(value=detected or "")
        entry = tk.Entry(
            path_row, textvariable=self._path_var,
            bg=COLORS["bg_lighter"], fg=COLORS["text"],
            insertbackground=COLORS["gold"],
            font=("Segoe UI", 10),
            relief="flat", bd=0,
            highlightthickness=1, highlightcolor=COLORS["gold_dim"],
            highlightbackground=COLORS["border"],
        )
        entry.pack(side="left", fill="x", expand=True, ipady=8, padx=(0, 10))

        browse_btn = GoldButton(
            path_row, text="Browse", command=self._browse_game_path,
            width=100, height=38, font_size=10,
        )
        browse_btn.pack(side="right")

        # Expected contents note
        self._make_label(
            frame,
            "The folder should contain OblivionRemastered/ with Binaries/ and Content/ inside.",
            size=9, color=COLORS["text_dim"],
        ).pack(anchor="w", pady=(0, 10))

        # Validation message
        self._path_msg = self._make_label(frame, "", size=10, color=COLORS["red"])
        self._path_msg.pack(anchor="w", pady=(0, 20))

        # Buttons row at bottom
        btn_row = tk.Frame(frame, bg=COLORS["bg"])
        btn_row.pack(side="bottom", fill="x", pady=(20, 0))

        GoldButton(
            btn_row, text="\u2190  Back", command=self._show_welcome,
            width=120, height=40, font_size=10,
        ).pack(side="left")

        GoldButton(
            btn_row, text="Next  \u2192", command=self._validate_and_proceed,
            width=120, height=40, font_size=10,
        ).pack(side="right")

    def _browse_game_path(self):
        path = filedialog.askdirectory(
            title="Select Oblivion Remastered install folder",
            initialdir=str(Path.home()),
        )
        if path:
            self._path_var.set(path)

    def _validate_and_proceed(self):
        path = self._path_var.get().strip()
        if not path:
            self._path_msg.config(text="Please enter or browse to the game path.")
            return
        p = Path(path)
        if not p.is_dir():
            self._path_msg.config(text="That directory does not exist.")
            return
        # Check for expected subfolders
        or_dir = p / "OblivionRemastered"
        if not or_dir.is_dir():
            # Maybe they selected one level too deep or too shallow
            # Be lenient — warn but allow
            self._path_msg.config(
                text="Warning: OblivionRemastered/ subfolder not found. Proceeding anyway.",
                fg=COLORS["gold"],
            )
        else:
            self._path_msg.config(text="")
        self.game_path = path
        self._show_download()

    # ─── Download Screen ───────────────────────────────────────────────────

    def _show_download(self):
        self._clear_container()

        # Pre-scan downloads for already-downloaded mods
        for mod in self.active_mods:
            existing = find_downloaded_file(mod, self.downloads_dir)
            if existing:
                self.mod_status[mod["nexus_id"]] = STATUS_DOWNLOADED
                self.mod_files[mod["nexus_id"]] = existing

        # Find first non-downloaded mod
        self.current_mod_index = 0
        for i, mod in enumerate(self.active_mods):
            if self.mod_status[mod["nexus_id"]] != STATUS_DOWNLOADED:
                self.current_mod_index = i
                break
        else:
            # All already downloaded
            self.current_mod_index = len(self.active_mods)

        frame = tk.Frame(self.container, bg=COLORS["bg"])
        frame.pack(fill="both", expand=True, padx=0, pady=0)

        # Header
        header = tk.Frame(frame, bg=COLORS["bg"])
        header.pack(fill="x", padx=30, pady=(20, 10))

        profile_name = "CHIM Deck" if self.profile == PROFILE_DECK else "CHIM"
        title_color = COLORS["blue"] if self.profile == PROFILE_DECK else COLORS["gold"]
        self._make_label(header, f"Download Mods  —  {profile_name}", size=20, color=title_color, bold=True).pack(side="left")

        self._dl_counter = self._make_label(header, "", size=11, color=COLORS["text_dim"])
        self._dl_counter.pack(side="right")

        # Progress bar
        prog_frame = tk.Frame(frame, bg=COLORS["bg"])
        prog_frame.pack(fill="x", padx=30, pady=(0, 10))
        self._dl_progress = ProgressBar(prog_frame, width=740, height=20)
        self._dl_progress.pack()

        # Mod list (scrollable)
        list_outer = tk.Frame(frame, bg=COLORS["border"], bd=1, relief="flat")
        list_outer.pack(fill="both", expand=True, padx=30, pady=(0, 10))

        self._dl_canvas = tk.Canvas(
            list_outer, bg=COLORS["bg"], highlightthickness=0, bd=0,
        )
        scrollbar = tk.Scrollbar(
            list_outer, orient="vertical", command=self._dl_canvas.yview,
            bg=COLORS["scrollbar"], troughcolor=COLORS["scrollbar_bg"],
            activebackground=COLORS["gold_dim"], width=10, relief="flat",
        )
        self._dl_canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        self._dl_canvas.pack(side="left", fill="both", expand=True)

        self._dl_list_frame = tk.Frame(self._dl_canvas, bg=COLORS["bg"])
        self._dl_canvas_window = self._dl_canvas.create_window(
            (0, 0), window=self._dl_list_frame, anchor="nw",
        )

        self._dl_list_frame.bind("<Configure>", lambda e: self._dl_canvas.configure(
            scrollregion=self._dl_canvas.bbox("all"),
        ))
        self._dl_canvas.bind("<Configure>", lambda e: self._dl_canvas.itemconfigure(
            self._dl_canvas_window, width=e.width,
        ))

        # Mouse wheel scrolling
        def _on_mousewheel(e):
            self._dl_canvas.yview_scroll(-1 * (e.delta // 120 or (1 if e.num == 4 else -1)), "units")

        self._dl_canvas.bind_all("<Button-4>", _on_mousewheel)
        self._dl_canvas.bind_all("<Button-5>", _on_mousewheel)
        self._dl_canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # Populate mod rows
        self._mod_rows = {}
        current_cat = None
        row_idx = 0

        for i, mod in enumerate(self.active_mods):
            # Category header
            if mod["category"] != current_cat:
                current_cat = mod["category"]
                icon = CATEGORY_ICONS.get(current_cat, "\u2022")
                cat_frame = tk.Frame(self._dl_list_frame, bg=COLORS["bg_light"])
                cat_frame.pack(fill="x", pady=(6 if row_idx > 0 else 0, 0))
                tk.Label(
                    cat_frame, text=f"  {icon}  {current_cat}",
                    bg=COLORS["bg_light"], fg=COLORS["gold"],
                    font=("Segoe UI", 10, "bold"), anchor="w",
                ).pack(fill="x", padx=8, pady=4)

            bg = COLORS["bg_row_alt"] if row_idx % 2 == 0 else COLORS["bg"]
            row = tk.Frame(self._dl_list_frame, bg=bg)
            row.pack(fill="x")

            # Status icon
            status = self.mod_status[mod["nexus_id"]]
            status_icon, status_color = self._status_display(status)
            status_lbl = tk.Label(
                row, text=status_icon, bg=bg, fg=status_color,
                font=("Segoe UI", 12), width=3,
            )
            status_lbl.pack(side="left", padx=(8, 0))

            # Mod name
            name_lbl = tk.Label(
                row, text=mod["name"], bg=bg, fg=COLORS["text"],
                font=("Segoe UI", 10), anchor="w",
            )
            name_lbl.pack(side="left", fill="x", expand=True, padx=4, pady=3)

            # Type badge
            type_text = mod["type"].replace("_framework", " \u2606").upper()
            tk.Label(
                row, text=type_text, bg=bg, fg=COLORS["text_dim"],
                font=("Segoe UI", 8), width=10,
            ).pack(side="right", padx=(0, 8))

            self._mod_rows[mod["nexus_id"]] = {
                "row": row, "status_lbl": status_lbl, "name_lbl": name_lbl, "bg": bg,
            }
            row_idx += 1

        # Bottom buttons
        btn_frame = tk.Frame(frame, bg=COLORS["bg"])
        btn_frame.pack(fill="x", padx=30, pady=(0, 15))

        GoldButton(
            btn_frame, text="\u2190  Back", command=self._show_game_path,
            width=110, height=38, font_size=10,
        ).pack(side="left")

        self._install_btn = GoldButton(
            btn_frame, text="Verify & Install  \u2192", command=self._show_verify,
            width=180, height=38, font_size=10, enabled=False,
        )
        # Hidden until all mods are downloaded or skipped

        self._skip_btn = GoldButton(
            btn_frame, text="Skip", command=self._skip_current_mod,
            width=80, height=38, font_size=10,
        )
        self._skip_btn.pack(side="right", padx=(0, 10))

        self._nexus_btn = GoldButton(
            btn_frame, text="Download Next Mod", command=self._open_next_nexus,
            width=200, height=38, font_size=10,
        )
        self._nexus_btn.pack(side="right", padx=(0, 10))

        self._update_download_ui()
        self._start_watcher()

    def _status_display(self, status: str) -> tuple[str, str]:
        if status == STATUS_DOWNLOADED:
            return ("\u2b07", COLORS["gold_bright"])  # ⬇ downloaded, ready to install
        elif status == STATUS_WAITING:
            return ("\u25cb", COLORS["gold"])          # ○ waiting for download
        elif status == STATUS_SKIPPED:
            return ("\u2014", COLORS["text_dim"])      # — skipped
        else:
            return ("\u2022", COLORS["text_dim"])      # • pending

    def _update_download_ui(self):
        done = sum(1 for s in self.mod_status.values() if s in (STATUS_DOWNLOADED, STATUS_SKIPPED))
        total = len(self.active_mods)

        self._dl_counter.config(text=f"{done} / {total} mods ready")
        self._dl_progress.set_value(done / total)

        # Update each row's status icon
        for mod in self.active_mods:
            nid = mod["nexus_id"]
            if nid in self._mod_rows:
                status = self.mod_status[nid]
                icon, color = self._status_display(status)
                self._mod_rows[nid]["status_lbl"].config(text=icon, fg=color)

        # Highlight current mod
        for i, mod in enumerate(self.active_mods):
            nid = mod["nexus_id"]
            if nid in self._mod_rows:
                row_data = self._mod_rows[nid]
                if i == self.current_mod_index and self.mod_status[nid] not in (STATUS_DOWNLOADED, STATUS_SKIPPED):
                    row_data["row"].config(bg=COLORS["bg_lighter"])
                    row_data["status_lbl"].config(bg=COLORS["bg_lighter"])
                    row_data["name_lbl"].config(bg=COLORS["bg_lighter"], fg=COLORS["gold_bright"])
                else:
                    row_data["row"].config(bg=row_data["bg"])
                    row_data["status_lbl"].config(bg=row_data["bg"])
                    row_data["name_lbl"].config(bg=row_data["bg"], fg=COLORS["text"])

        # Update button text
        if self.current_mod_index < len(self.active_mods):
            mod = self.active_mods[self.current_mod_index]
            short_name = mod["name"][:25]
            self._nexus_btn.set_text(f"Download: {short_name}")
            self._nexus_btn.set_enabled(True)
            self._skip_btn.set_enabled(True)
            self.mod_status[mod["nexus_id"]] = STATUS_WAITING
            icon, color = self._status_display(STATUS_WAITING)
            if mod["nexus_id"] in self._mod_rows:
                self._mod_rows[mod["nexus_id"]]["status_lbl"].config(text=icon, fg=color)
        else:
            self._nexus_btn.set_text("All mods ready!")
            self._nexus_btn.set_enabled(False)
            self._skip_btn.set_enabled(False)

        # Only show install button when ALL mods are downloaded or skipped
        all_ready = all(s in (STATUS_DOWNLOADED, STATUS_SKIPPED) for s in self.mod_status.values())
        if all_ready:
            self._install_btn.pack(side="right")
            self._install_btn.set_enabled(True)
        else:
            self._install_btn.pack_forget()

        # Auto-scroll to current mod
        if self.current_mod_index < len(self.active_mods):
            nid = self.active_mods[self.current_mod_index]["nexus_id"]
            if nid in self._mod_rows:
                row_widget = self._mod_rows[nid]["row"]
                self._dl_list_frame.update_idletasks()
                y = row_widget.winfo_y()
                h = self._dl_canvas.winfo_height()
                total_h = self._dl_list_frame.winfo_height()
                if total_h > h:
                    fraction = max(0, (y - h // 3)) / total_h
                    self._dl_canvas.yview_moveto(fraction)

    def _advance_to_next(self):
        """Move to the next unfinished mod."""
        for i in range(self.current_mod_index + 1, len(self.active_mods)):
            nid = self.active_mods[i]["nexus_id"]
            if self.mod_status[nid] not in (STATUS_DOWNLOADED, STATUS_SKIPPED):
                self.current_mod_index = i
                self._update_download_ui()
                return
        # All done
        self.current_mod_index = len(self.active_mods)
        self._update_download_ui()

    def _open_next_nexus(self):
        if self.current_mod_index >= len(self.active_mods):
            return
        mod = self.active_mods[self.current_mod_index]
        url = nexus_url(mod["nexus_id"])
        webbrowser.open(url)

    def _skip_current_mod(self):
        if self.current_mod_index >= len(self.active_mods):
            return
        mod = self.active_mods[self.current_mod_index]
        self.mod_status[mod["nexus_id"]] = STATUS_SKIPPED
        self._advance_to_next()

    def _start_watcher(self):
        self._watcher_running = True
        self._poll_downloads()

    def _stop_watcher(self):
        self._watcher_running = False
        if self._watcher_id:
            try:
                self.root.after_cancel(self._watcher_id)
            except Exception:
                pass
            self._watcher_id = None

    def _poll_downloads(self):
        if not self._watcher_running:
            return
        changed = False
        for mod in self.active_mods:
            nid = mod["nexus_id"]
            if self.mod_status[nid] in (STATUS_DOWNLOADED, STATUS_SKIPPED):
                continue
            found = find_downloaded_file(mod, self.downloads_dir)
            if found:
                self.mod_status[nid] = STATUS_DOWNLOADED
                self.mod_files[nid] = found
                changed = True

        if changed:
            # Advance current index if current mod got downloaded
            if self.current_mod_index < len(self.active_mods):
                nid = self.active_mods[self.current_mod_index]["nexus_id"]
                if self.mod_status[nid] in (STATUS_DOWNLOADED, STATUS_SKIPPED):
                    self._advance_to_next()
            self._update_download_ui()

        self._watcher_id = self.root.after(2000, self._poll_downloads)

    # ─── Verification Screen ──────────────────────────────────────────────

    def _show_verify(self):
        self._stop_watcher()
        self._clear_container()

        frame = tk.Frame(self.container, bg=COLORS["bg"])
        frame.pack(fill="both", expand=True, padx=50, pady=30)

        self._make_label(frame, "Verifying Mods", size=22, color=COLORS["gold"], bold=True).pack(anchor="w", pady=(0, 6))
        self._make_label(
            frame, "Checking archives, file types, conflicts, and disk space before installing...",
            size=10, color=COLORS["text_dim"],
        ).pack(anchor="w", pady=(0, 20))

        self._verify_progress = ProgressBar(frame, width=700, height=24)
        self._verify_progress.pack(pady=(0, 16))

        self._verify_status = self._make_label(frame, "Starting verification...", size=11, color=COLORS["text"])
        self._verify_status.pack(anchor="w", pady=(0, 10))

        # Log area
        log_frame = tk.Frame(frame, bg=COLORS["border"], bd=1, relief="flat")
        log_frame.pack(fill="both", expand=True, pady=(0, 10))

        self._verify_log = tk.Text(
            log_frame, bg=COLORS["bg_light"], fg=COLORS["text_dim"],
            font=("Cascadia Code", 9), wrap="word",
            relief="flat", bd=0, highlightthickness=0,
            insertbackground=COLORS["gold"],
        )
        v_scroll = tk.Scrollbar(
            log_frame, orient="vertical", command=self._verify_log.yview,
            bg=COLORS["scrollbar"], troughcolor=COLORS["scrollbar_bg"],
            activebackground=COLORS["gold_dim"], width=10, relief="flat",
        )
        self._verify_log.configure(yscrollcommand=v_scroll.set)
        v_scroll.pack(side="right", fill="y")
        self._verify_log.pack(side="left", fill="both", expand=True, padx=4, pady=4)

        self._verify_log.tag_configure("gold", foreground=COLORS["gold"])
        self._verify_log.tag_configure("green", foreground=COLORS["green"])
        self._verify_log.tag_configure("red", foreground=COLORS["red"])
        self._verify_log.tag_configure("dim", foreground=COLORS["text_dim"])
        self._verify_log.tag_configure("blue", foreground=COLORS["blue"])

        self._verify_btn_frame = tk.Frame(frame, bg=COLORS["bg"])
        self._verify_btn_frame.pack(fill="x", pady=(10, 0))

        # Run verification in background
        threading.Thread(target=self._run_verify, daemon=True).start()

    def _vlog(self, text: str, tag: str = ""):
        def _do():
            self._verify_log.insert("end", text + "\n", tag)
            self._verify_log.see("end")
        self.root.after(0, _do)

    def _run_verify(self):
        import time
        game_path = Path(self.game_path)
        to_verify = [m for m in self.active_mods if self.mod_status[m["nexus_id"]] == STATUS_DOWNLOADED]
        total = len(to_verify)
        issues = []
        warnings = []

        if total == 0:
            self._vlog("No mods to verify.", "red")
            return

        self._vlog(f"Verifying {total} mods...", "gold")
        self._vlog("")

        # ── Check 1: Game directory structure ──
        self._vlog("Checking game directory...", "gold")
        required_dirs = {
            "Data": game_path / "OblivionRemastered" / "Content" / "Dev" / "ObvData" / "Data",
            "Paks": game_path / "OblivionRemastered" / "Content" / "Paks",
            "Binaries": game_path / "OblivionRemastered" / "Binaries" / "Win64",
        }
        for name, path in required_dirs.items():
            if path.is_dir():
                self._vlog(f"  {name}: OK", "green")
            else:
                self._vlog(f"  {name}: MISSING — {path}", "red")
                issues.append(f"Game directory missing: {name} ({path})")
        self._vlog("")

        # ── Check 2: Disk space ──
        self._vlog("Checking disk space...", "gold")
        try:
            stat = shutil.disk_usage(str(game_path))
            free_gb = stat.free / (1024**3)
            # Estimate ~2GB needed for full install
            needed_gb = 2.0
            if free_gb < needed_gb:
                self._vlog(f"  Free: {free_gb:.1f} GB — need at least {needed_gb:.0f} GB", "red")
                issues.append(f"Insufficient disk space: {free_gb:.1f} GB free, need {needed_gb:.0f} GB")
            else:
                self._vlog(f"  Free: {free_gb:.1f} GB — OK", "green")
        except Exception as e:
            self._vlog(f"  Could not check disk space: {e}", "red")
            warnings.append("Could not verify disk space")
        self._vlog("")

        # ── Check 3: Archive integrity + file type validation ──
        self._vlog("Verifying archives...", "gold")
        dest_files = {}  # track output filenames for conflict detection

        for idx, mod in enumerate(to_verify):
            nid = mod["nexus_id"]
            archive = self.mod_files[nid]
            progress = (idx + 1) / total

            self.root.after(0, lambda p=progress: self._verify_progress.set_value(p))
            self.root.after(0, lambda m=mod, i=idx: self._verify_status.config(
                text=f"[{i+1}/{total}]  {m['name']}"
            ))

            if not archive or not archive.exists():
                self._vlog(f"  [{idx+1}/{total}] {mod['name']}: archive missing", "red")
                issues.append(f"{mod['name']}: archive file not found")
                continue

            # Try extracting to temp dir
            tmp_dir = Path(tempfile.mkdtemp(prefix="chim_verify_"))
            ok = extract_archive(archive, tmp_dir)

            if not ok:
                self._vlog(f"  [{idx+1}/{total}] {mod['name']}: CORRUPT or unsupported archive", "red")
                issues.append(f"{mod['name']}: failed to extract {archive.name}")
                shutil.rmtree(tmp_dir, ignore_errors=True)
                continue

            # Check file types match expected mod type
            all_files = [f for f in tmp_dir.rglob("*") if f.is_file()]
            extensions = set(f.suffix.lower() for f in all_files)

            expected_map = {
                "esp": {".esp", ".esm", ".bsa", ".ini"},
                "pak": {".pak", ".ucas", ".utoc", ".esp", ".esm"},
                "obse": {".dll", ".ini", ".esp", ".esm"},
                "obse_framework": {".dll", ".exe", ".ini"},
                "ue4ss": {".lua", ".txt", ".ini", ".dll", ".json", ".pak", ".ucas", ".utoc", ".esp", ".esm"},
                "ue4ss_framework": {".dll", ".ini", ".txt", ".lua", ".exe"},
                "config": {".ini", ".txt", ".cfg", ".json"},
            }
            expected = expected_map.get(mod["type"], set())
            relevant = extensions & expected

            if not relevant and len(all_files) > 0:
                self._vlog(f"  [{idx+1}/{total}] {mod['name']}: no expected files found (has: {', '.join(extensions)})", "red")
                issues.append(f"{mod['name']}: archive doesn't contain expected file types for {mod['type']} mod")
            else:
                # Check for file conflicts
                for f in all_files:
                    ext = f.suffix.lower()
                    if ext in (".esp", ".esm", ".pak", ".ucas", ".utoc", ".dll"):
                        key = f.name.lower()
                        if key in dest_files and dest_files[key] != mod['name']:
                            self._vlog(f"  [{idx+1}/{total}] {mod['name']}: conflict — {f.name} also in {dest_files[key]}", "red")
                            warnings.append(f"File conflict: {f.name} exists in both {mod['name']} and {dest_files[key]}")
                        else:
                            dest_files[key] = mod['name']

                self._vlog(f"  [{idx+1}/{total}] {mod['name']}: OK ({len(all_files)} files)", "green")

            shutil.rmtree(tmp_dir, ignore_errors=True)
            time.sleep(0.05)  # brief pause for UI updates

        self._vlog("")

        # ── Check 4: Required tools ──
        self._vlog("Checking extraction tools...", "gold")
        has_7z = find_7z()
        has_unrar = shutil.which("unrar")
        # Check if any mods need 7z/rar
        archive_types = set()
        for mod in to_verify:
            archive = self.mod_files.get(mod["nexus_id"])
            if archive:
                archive_types.add(archive.suffix.lower())
        if ".7z" in archive_types and not has_7z:
            self._vlog("  p7zip: MISSING — needed for .7z archives", "red")
            issues.append("p7zip not installed — needed for .7z extraction (install with: sudo pacman -S p7zip)")
        elif ".7z" in archive_types:
            self._vlog("  p7zip: OK", "green")
        if ".rar" in archive_types and not has_unrar and not has_7z:
            self._vlog("  unrar: MISSING — needed for .rar archives", "red")
            issues.append("unrar not installed — needed for .rar extraction (install with: sudo pacman -S unrar)")
        elif ".rar" in archive_types:
            self._vlog("  unrar/7z: OK", "green")
        self._vlog("")

        # ── Results ──
        self.root.after(0, lambda: self._verify_progress.set_value(1.0))

        if issues:
            self._vlog(f"VERIFICATION FAILED — {len(issues)} issue(s) found:", "red")
            for issue in issues:
                self._vlog(f"  • {issue}", "red")
            if warnings:
                self._vlog("")
                for w in warnings:
                    self._vlog(f"  ⚠ {w}", "gold")
            self.root.after(0, lambda: self._verify_status.config(
                text=f"Verification failed — {len(issues)} issue(s) found"
            ))
            self.root.after(0, self._show_verify_fail_buttons)
        else:
            self._vlog("ALL CHECKS PASSED", "green")
            if warnings:
                for w in warnings:
                    self._vlog(f"  ⚠ {w}", "gold")
            self._vlog("")
            self._vlog(f"Ready to install {total} mods. No issues detected.", "green")
            self.root.after(0, lambda: self._verify_status.config(
                text=f"All {total} mods verified — ready to install"
            ))
            self.root.after(0, self._show_verify_pass_buttons)

    def _show_verify_pass_buttons(self):
        GoldButton(
            self._verify_btn_frame, text="\u2190  Back", command=self._show_download,
            width=110, height=38, font_size=10,
        ).pack(side="left")
        GoldButton(
            self._verify_btn_frame, text="Install Mods  \u2192", command=self._show_install,
            width=180, height=42, font_size=12,
        ).pack(side="right")

    def _show_verify_fail_buttons(self):
        GoldButton(
            self._verify_btn_frame, text="\u2190  Back to Downloads", command=self._show_download,
            width=180, height=38, font_size=10,
        ).pack(side="left")
        GoldButton(
            self._verify_btn_frame, text="Re-Verify", command=self._show_verify,
            width=120, height=38, font_size=10,
        ).pack(side="right")

    # ─── Install Screen ────────────────────────────────────────────────────

    def _show_install(self):
        self._clear_container()

        frame = tk.Frame(self.container, bg=COLORS["bg"])
        frame.pack(fill="both", expand=True, padx=50, pady=30)

        self._make_label(frame, "Installing Mods", size=22, color=COLORS["gold"], bold=True).pack(anchor="w", pady=(0, 6))
        self._make_label(
            frame, "Extracting archives and placing files...",
            size=10, color=COLORS["text_dim"],
        ).pack(anchor="w", pady=(0, 20))

        self._install_progress = ProgressBar(frame, width=700, height=24)
        self._install_progress.pack(pady=(0, 20))

        self._install_status = self._make_label(frame, "Preparing...", size=11, color=COLORS["text"])
        self._install_status.pack(anchor="w", pady=(0, 10))

        # Log area
        log_frame = tk.Frame(frame, bg=COLORS["border"], bd=1, relief="flat")
        log_frame.pack(fill="both", expand=True, pady=(0, 10))

        self._install_log = tk.Text(
            log_frame, bg=COLORS["bg_light"], fg=COLORS["text_dim"],
            font=("Cascadia Code", 9), wrap="word",
            relief="flat", bd=0, highlightthickness=0,
            insertbackground=COLORS["gold"],
        )
        log_scroll = tk.Scrollbar(
            log_frame, orient="vertical", command=self._install_log.yview,
            bg=COLORS["scrollbar"], troughcolor=COLORS["scrollbar_bg"],
            activebackground=COLORS["gold_dim"], width=10, relief="flat",
        )
        self._install_log.configure(yscrollcommand=log_scroll.set)
        log_scroll.pack(side="right", fill="y")
        self._install_log.pack(side="left", fill="both", expand=True, padx=4, pady=4)

        self._install_log.tag_configure("gold", foreground=COLORS["gold"])
        self._install_log.tag_configure("green", foreground=COLORS["green"])
        self._install_log.tag_configure("red", foreground=COLORS["red"])
        self._install_log.tag_configure("dim", foreground=COLORS["text_dim"])

        # Start installation in background thread
        threading.Thread(target=self._run_install, daemon=True).start()

    def _log(self, text: str, tag: str = ""):
        self.install_log_lines.append(text)
        def _do():
            self._install_log.insert("end", text + "\n", tag)
            self._install_log.see("end")
        self.root.after(0, _do)

    def _run_install(self):
        game_path = Path(self.game_path)
        to_install = [m for m in self.active_mods if self.mod_status[m["nexus_id"]] == STATUS_DOWNLOADED]
        total = len(to_install)

        if total == 0:
            self._log("No mods to install.", "red")
            self.root.after(1000, self._show_done)
            return

        mode_label = "DRY RUN — " if self.dry_run else ""
        profile_label = "CHIM Deck" if self.profile == PROFILE_DECK else "CHIM"
        self._log(f"{mode_label}Installing {total} mods ({profile_label} profile) to:", "gold")
        self._log(f"  {game_path}", "dim")
        if self.dry_run:
            self._log("  (Dry run — no files will be modified)", "blue")
        self._log("")

        # Ensure mod directories exist (skip in dry run)
        dirs = [
            game_path / "OblivionRemastered" / "Content" / "Dev" / "ObvData" / "Data",
            game_path / "OblivionRemastered" / "Content" / "Paks" / "~mods",
            game_path / "OblivionRemastered" / "Binaries" / "Win64" / "OBSE" / "Plugins",
            game_path / "OblivionRemastered" / "Binaries" / "Win64" / "ue4ss" / "Mods",
        ]
        if not self.dry_run:
            for d in dirs:
                d.mkdir(parents=True, exist_ok=True)

        errors_total = []

        for idx, mod in enumerate(to_install):
            nid = mod["nexus_id"]
            archive = self.mod_files[nid]
            progress = (idx + 1) / total

            self.root.after(0, lambda p=progress: self._install_progress.set_value(p))
            self.root.after(0, lambda m=mod, i=idx: self._install_status.config(
                text=f"[{i+1}/{total}]  {m['name']}"
            ))

            self._log(f"[{idx+1}/{total}]  {mod['name']}", "gold")

            if not archive or not archive.exists():
                self._log(f"  Archive not found, skipping.", "red")
                errors_total.append(f"{mod['name']}: archive missing")
                continue

            if self.dry_run:
                self._log(f"  Would extract: {archive.name}", "dim")
                self._log(f"  Would install as type: {mod['type']}", "dim")
                import time; time.sleep(0.1)  # Brief pause so user can see progress
                self._log(f"  [DRY RUN] OK", "green")
                continue

            # Extract to temp dir
            tmp_dir = Path(tempfile.mkdtemp(prefix="chim_"))
            self._log(f"  Extracting {archive.name}...", "dim")

            ok = extract_archive(archive, tmp_dir)
            if not ok:
                self._log(f"  FAILED to extract. Need p7zip or unrar?", "red")
                errors_total.append(f"{mod['name']}: extraction failed")
                shutil.rmtree(tmp_dir, ignore_errors=True)
                continue

            # Install files
            installed, errs = classify_and_install_files(tmp_dir, game_path, mod["type"], mod["name"])
            if installed > 0:
                self._log(f"  Installed {installed} file(s).", "green")
            if errs:
                for e in errs:
                    self._log(f"  {e}", "red")
                errors_total.extend(errs)

            # Cleanup
            shutil.rmtree(tmp_dir, ignore_errors=True)

        self._log("")
        # Deploy CHIM Deck custom configs if Deck profile
        if self.profile == PROFILE_DECK and not self.dry_run:
            self._log("")
            self._log("Deploying CHIM Deck optimized configs...", "gold")
            config_dir = self._find_saved_config_dir(game_path)
            if config_dir:
                for ini_name, bundled_name in [("Engine.ini", "deck_engine.ini"), ("GameUserSettings.ini", "deck_gameusersettings.ini")]:
                    src = self._find_bundled_file(bundled_name)
                    if src and src.is_file():
                        dest = config_dir / ini_name
                        # Backup existing
                        if dest.exists():
                            backup = dest.with_suffix(f".ini.backup_chim")
                            shutil.copy2(dest, backup)
                            self._log(f"  Backed up {ini_name} → {backup.name}", "dim")
                        shutil.copy2(src, dest)
                        # Make read-only so game can't overwrite
                        dest.chmod(0o444)
                        self._log(f"  Installed {ini_name} (read-only)", "green")
                    else:
                        self._log(f"  {bundled_name} not found in installer bundle", "red")
                        errors_total.append(f"Missing bundled config: {bundled_name}")
            else:
                self._log("  Could not find saved config directory — deploy configs manually", "red")
                errors_total.append("Config directory not found")

        if errors_total:
            self._log(f"Completed with {len(errors_total)} warning(s).", "gold")
        else:
            self._log("All mods installed successfully.", "green")

        self.root.after(0, lambda: self._install_status.config(text="Installation complete."))

        # Show Done button
        self.root.after(500, self._add_done_button)

    def _find_saved_config_dir(self, game_path: Path) -> Optional[Path]:
        """Find the Proton/Wine saved config directory for Oblivion Remastered."""
        # Standard Proton compatdata path
        candidates = [
            Path.home() / ".local/share/Steam/steamapps/compatdata/2623190/pfx/drive_c/users/steamuser/Documents/My Games/Oblivion Remastered/Saved/Config/Windows",
            Path("/home/deck/.local/share/Steam/steamapps/compatdata/2623190/pfx/drive_c/users/steamuser/Documents/My Games/Oblivion Remastered/Saved/Config/Windows"),
            Path.home() / ".var/app/com.valvesoftware.Steam/.local/share/Steam/steamapps/compatdata/2623190/pfx/drive_c/users/steamuser/Documents/My Games/Oblivion Remastered/Saved/Config/Windows",
        ]
        for c in candidates:
            if c.is_dir():
                return c
        # Try to find it by searching compatdata
        for compat_root in [Path.home() / ".local/share/Steam/steamapps/compatdata", Path("/home/deck/.local/share/Steam/steamapps/compatdata")]:
            config_path = compat_root / "2623190" / "pfx" / "drive_c" / "users" / "steamuser" / "Documents" / "My Games" / "Oblivion Remastered" / "Saved" / "Config" / "Windows"
            if config_path.is_dir():
                return config_path
        return None

    def _find_bundled_file(self, filename: str) -> Optional[Path]:
        """Find a file bundled with the installer (PyInstaller or dev mode)."""
        base = Path(getattr(sys, '_MEIPASS', None) or Path(__file__).parent)
        p = base / filename
        return p if p.is_file() else None

    def _add_done_button(self):
        btn_frame = tk.Frame(self.container, bg=COLORS["bg"])
        btn_frame.pack(fill="x", padx=50, pady=(0, 15))
        GoldButton(
            btn_frame, text="Continue  \u2192", command=self._show_done,
            width=140, height=40, font_size=11,
        ).pack(side="right")

    # ─── Done Screen ───────────────────────────────────────────────────────

    def _show_done(self):
        self._clear_container()

        frame = tk.Frame(self.container, bg=COLORS["bg"])
        frame.pack(expand=True)

        # Gold line
        tk.Frame(frame, bg=COLORS["gold_dim"], height=1, width=200).pack(pady=(0, 30))

        tk.Label(
            frame, text="C H I M", bg=COLORS["bg"], fg=COLORS["gold"],
            font=("Segoe UI", 36, "bold"),
        ).pack(pady=(0, 20))

        tk.Label(
            frame, text="has been installed.", bg=COLORS["bg"],
            fg=COLORS["text"], font=("Segoe UI", 14),
        ).pack(pady=(0, 30))

        # Gold line
        tk.Frame(frame, bg=COLORS["gold_dim"], height=1, width=200).pack(pady=(0, 30))

        tk.Label(
            frame, text="See the dream. Reshape it.", bg=COLORS["bg"],
            fg=COLORS["gold_dim"], font=("Segoe UI", 12),
            justify="center",
        ).pack(pady=(0, 40))

        # Tips — different for PC vs Deck
        tips_frame = tk.Frame(frame, bg=COLORS["bg_light"], padx=20, pady=12)
        tips_frame.pack(pady=(0, 30))

        if self.profile == PROFILE_DECK:
            tips_text = (
                "STEAM DECK SETUP\n\n"
                "1. Use Proton Experimental or GE-Proton 10-1+\n"
                "2. Set Launch Options to:\n"
                "   MANGOHUD=1 RADV_PERFTEST=gpl %command%\n\n"
                "3. Quick Access Menu (... button):\n"
                "   • Framerate Limit: 30 FPS\n"
                "   • Refresh Rate: 40 Hz\n"
                "   • Allow Tearing: Off\n"
                "   • TDP Limit: 12-15W\n"
                "   • GPU Clock: 1200 MHz\n\n"
                "4. Game MUST be on Internal SSD (not SD card)\n"
                "5. Only change graphics settings from the MAIN MENU\n"
                "   (changing in-game causes crashes)"
            )
        else:
            tips_text = (
                "Launch Oblivion Remastered through Steam as usual.\n"
                "CHIM is installed and ready to go.\n\n"
                "If anything looks wrong, use the install log\n"
                "to troubleshoot or report issues."
            )

        tk.Label(
            tips_frame, text=tips_text,
            bg=COLORS["bg_light"], fg=COLORS["text_dim"],
            font=("Segoe UI", 9), justify="left",
        ).pack()

        btn_frame = tk.Frame(frame, bg=COLORS["bg"])
        btn_frame.pack()

        GoldButton(
            btn_frame, text="Save Install Log", command=self._save_log,
            width=160, height=38, font_size=10,
        ).pack(side="left", padx=(0, 12))

        GoldButton(
            btn_frame, text="Close Installer", command=self.root.destroy,
            width=160, height=38, font_size=10,
        ).pack(side="left")

    def _save_log(self):
        log_path = Path.home() / "chim_install_log.txt"
        profile_name = "CHIM Deck" if self.profile == PROFILE_DECK else "CHIM"
        header = f"CHIM Installer Log — Profile: {profile_name} — Dry Run: {self.dry_run}\n{'='*60}\n\n"
        log_path.write_text(header + "\n".join(self.install_log_lines))
        messagebox.showinfo("Log Saved", f"Install log saved to:\n{log_path}")

    # ─── Run ───────────────────────────────────────────────────────────────

    def run(self):
        self.root.mainloop()


# ─── Entry Point ────────────────────────────────────────────────────────────────

def main():
    # Gaming mode check
    if is_gaming_mode():
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showwarning(
                "CHIM Installer — Desktop Mode Required",
                "CHIM installer needs Desktop Mode.\n\n"
                "Hold the power button \u2192 Switch to Desktop,\n"
                "then run this again.",
            )
            root.destroy()
        except Exception:
            print(
                "CHIM installer needs Desktop Mode.\n"
                "Hold the power button -> Switch to Desktop, then run this again."
            )
        sys.exit(1)

    app = CHIMInstaller()
    if "--dry-run" in sys.argv:
        app.dry_run = True
    app.run()


if __name__ == "__main__":
    main()
