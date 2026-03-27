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
import json
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
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

# ─── Mod Database ───────────────────────────────────────────────────────────────

MODS = [
    # Bug Fixes & Framework
    # OBSE64 (282), UE4SS (32), Address Library (4475), ActiveEffectsFix (4994),
    # Baka Achievement Enabler (145), No Enchantment Drain (1253) are ALL bundled
    # in patches/obse_framework/ and patches/obse_plugins/ — NOT downloaded from Nexus.
    {"name": "Unofficial Oblivion Remastered Patch", "nexus_id": 477, "type": "esp", "category": "Bug Fixes & Framework", "load_order": 1, "esp_name": "Unofficial Oblivion Remastered Patch.esp"},
    {"name": "Oblivion Unreal Fixes", "nexus_id": 4676, "type": "pak", "category": "Bug Fixes & Framework"},
    # ActiveEffectsFix (4994) and Baka Achievement Enabler (145) — bundled in patches/obse_plugins/
    {"name": "Difficulty Slider Fixed", "nexus_id": 58, "type": "esp", "category": "Bug Fixes & Framework", "load_order": 2, "esp_name": "Difficulty Slider Fixed.esp"},
    {"name": "RainFPSFix", "nexus_id": 566, "type": "esp", "category": "Bug Fixes & Framework", "load_order": 3, "esp_name": "RainFPSFix.esp"},
    # Visuals & Lighting
    {"name": "Shaders Revised", "nexus_id": 1528, "type": "ue4ss", "category": "Visuals & Lighting", "ue4ss_folder": "ShadersRevised"},
    {"name": "Lumen Remastered", "nexus_id": 1129, "type": "ue4ss", "category": "Visuals & Lighting", "ue4ss_folder": "LumenRemastered"},
    {"name": "Lumiere", "nexus_id": 3100, "type": "pak", "category": "Visuals & Lighting"},
    {"name": "Eternal Darkness", "nexus_id": 5136, "type": "ue4ss", "category": "Visuals & Lighting", "ue4ss_folder": "EternalDarkness"},
    {"name": "Ultra Plus", "nexus_id": 27, "type": "ue4ss", "category": "Visuals & Lighting", "ue4ss_folder": "UltraPlusExtensions"},
    {"name": "Young Textures Revamped", "nexus_id": 445, "type": "pak", "category": "Visuals & Lighting"},
    {"name": "Greener Grass", "nexus_id": 2279, "type": "pak", "category": "Visuals & Lighting"},
    {"name": "Connor's Flora", "nexus_id": 4740, "type": "pak", "category": "Visuals & Lighting"},
    {"name": "NPC Overhaul AIO", "nexus_id": 3096, "type": "ue4ss", "category": "Visuals & Lighting", "ue4ss_folder": "NPCAppearanceManager", "no_enabled_txt": True},
    {"name": "8K Color World Map", "nexus_id": 944, "type": "pak", "category": "Visuals & Lighting"},
    {"name": "Brighter Torches 1.5x", "nexus_id": 2821, "type": "pak", "category": "Visuals & Lighting"},
    {"name": "Realistic HQ Skin", "nexus_id": 1284, "type": "pak", "category": "Visuals & Lighting"},
    {"name": "All Customization Options Unlocked", "nexus_id": 344, "type": "pak", "category": "Visuals & Lighting"},
    # Camera & Animations
    {"name": "Improved Camera", "nexus_id": 2362, "type": "pak", "category": "Camera & Animations"},
    {"name": "Kei Animations - Legacy", "nexus_id": 4825, "type": "pak", "category": "Camera & Animations"},
    # Combat & Magic
    {"name": "UltraCombat V2", "nexus_id": 4244, "type": "ue4ss", "category": "Combat & Magic", "ue4ss_folder": "UltraCombat"},
    {"name": "Responsive Combat AI", "nexus_id": 2792, "type": "esp", "category": "Combat & Magic", "load_order": 20, "esp_name": "Responsive Combat AI.esp"},
    {"name": "Responsive Spellcaster AI", "nexus_id": 5197, "type": "esp", "category": "Combat & Magic", "load_order": 21, "esp_name": "Spellcaster Tweaks Base Game.esp"},
    {"name": "Supreme Magicka", "nexus_id": 1098, "type": "esp", "category": "Combat & Magic", "load_order": 22, "esp_name": "SupremeMagickaRemaster.esp"},
    {"name": "Nascent Archery", "nexus_id": 2149, "type": "esp", "category": "Combat & Magic", "load_order": 23, "esp_name": "Nascent - Archery Overhaul.esp"},
    {"name": "Magic Skill Leveling Fixed", "nexus_id": 3965, "type": "esp", "category": "Combat & Magic", "load_order": 24, "esp_name": "MagicSkillLevelingFixed.esp"},
    {"name": "Way of the Fist", "nexus_id": 1323, "type": "esp", "category": "Combat & Magic", "load_order": 25, "esp_name": "Way of the Strong Fist.esp"},
    {"name": "Unique Elemental Spells", "nexus_id": 119, "type": "esp", "category": "Combat & Magic", "load_order": 26, "esp_name": "Unique Elemental Spells.esp"},
    {"name": "Engaging Combat", "nexus_id": 1812, "type": "ue4ss", "category": "Combat & Magic", "ue4ss_folder": "EngagingCombat"},
    # AI & World
    {"name": "NPC and Faction Overhaul", "nexus_id": 5140, "type": "esp", "category": "AI & World", "load_order": 30, "esp_name": "NPC & Faction Overhaul.esp"},
    {"name": "Dynamic AI Animals", "nexus_id": 2228, "type": "esp", "category": "AI & World", "load_order": 31, "esp_name": "DynamicAIBehaviorAnimals.esp"},
    {"name": "Climates Revised", "nexus_id": 791, "type": "esp", "category": "AI & World", "load_order": 32, "esp_name": "SSTClimatesRevised.esp"},
    {"name": "Quest NPCs Run", "nexus_id": 219, "type": "esp", "category": "AI & World", "load_order": 33, "esp_name": "Quest NPCs Run.esp"},
    {"name": "Ultimate Dialogue Overhaul", "nexus_id": 5183, "type": "esp", "category": "AI & World", "load_order": 35, "esp_name": "UltimateDialogueOverhaullastfinal8rdolast.esp"},
    {"name": "NPCs Come to Life", "nexus_id": 3363, "type": "esp", "category": "AI & World", "load_order": 37, "esp_name": "NaiadTravelers.esp"},
    {"name": "Balanced NPC Level Cap", "nexus_id": 182, "type": "esp", "category": "AI & World", "load_order": 38, "esp_name": "Balanced NPC Level Cap.esp"},
    # Items & Progression
    {"name": "Auto Upgrade Leveled Items", "nexus_id": 567, "type": "esp", "category": "Items & Progression", "load_order": 40, "esp_name": "AutoUpgradeRewardsOnLevel.esp"},
    {"name": "No Durability Damage", "nexus_id": 109, "type": "esp", "category": "Items & Progression", "load_order": 41, "esp_name": "No Durability Damage.esp"},
    # No Enchantment Drain (1253) — bundled in patches/obse_plugins/
    {"name": "Carry Weight + Weightless Misc", "nexus_id": 1734, "type": "ue4ss", "category": "Items & Progression", "ue4ss_folder": "CarryWeightEncumbranceOverhaul"},
    {"name": "Aiorta's Enchantment Adjustments", "nexus_id": 4645, "type": "esp", "category": "Items & Progression", "load_order": 42, "esp_name": "AiortaEnchantAdjust.esp"},
    {"name": "Better Enchanting and Soul Gems", "nexus_id": 1500, "type": "esp", "category": "Items & Progression", "load_order": 43, "esp_name": "BetterEnchantingCEEAdjustment.esp"},
    # Spells & Powers
    {"name": "Spell Duration x10", "nexus_id": 1087, "type": "esp", "category": "Spells & Powers", "load_order": 50, "esp_name": "Dank_SpellDuration.esp"},
    {"name": "Unlimited Powers", "nexus_id": 1461, "type": "esp", "category": "Spells & Powers", "load_order": 51, "esp_name": "UnlimitedPowers.esp"},
    {"name": "Spell Freedom", "nexus_id": 138, "type": "esp", "category": "Spells & Powers", "load_order": 52, "esp_name": "LessRestrictiveSpells.esp"},
    {"name": "Spells Reworked", "nexus_id": 1238, "type": "esp", "category": "Spells & Powers", "load_order": 53, "esp_name": "Spells Reworked.esp"},
    # UI & Quality of Life
    {"name": "Better HUD Slim", "nexus_id": 13, "type": "pak", "category": "UI & Quality of Life"},
    {"name": "MISS Inventory Sorter", "nexus_id": 3288, "type": "obse_config", "category": "UI & Quality of Life"},
    {"name": "Auto Local Map", "nexus_id": 1119, "type": "ue4ss", "category": "UI & Quality of Life", "ue4ss_folder": "AutoLocalMap"},
    {"name": "Additional Map Markers", "nexus_id": 479, "type": "esp", "category": "UI & Quality of Life", "load_order": 60, "esp_name": "AdditionalMapMarkers.esp"},
    {"name": "Horse Whistle", "nexus_id": 153, "type": "esp", "category": "UI & Quality of Life", "load_order": 61, "esp_name": "Horse Whistle.esp"},
    {"name": "Fixed Persuasion", "nexus_id": 1913, "type": "esp", "category": "UI & Quality of Life", "load_order": 62, "esp_name": "EasierPersuasion.esp"},
    {"name": "Better Auto Lockpick", "nexus_id": 418, "type": "esp", "category": "UI & Quality of Life", "load_order": 63, "esp_name": "BetterAutoLockpick.esp"},
    # Richer Vendors removed — overwritten by Immersive Vendor and Loot (4100)
    {"name": "PreserveStats", "nexus_id": 783, "type": "esp", "category": "UI & Quality of Life", "load_order": 65, "esp_name": "PreserveStats.esp"},
    {"name": "Quieter Lockpicking", "nexus_id": 1788, "type": "pak", "category": "UI & Quality of Life"},
    {"name": "Better Movement", "nexus_id": 2479, "type": "ue4ss", "category": "UI & Quality of Life", "ue4ss_folder": "BetterMovement"},
    {"name": "Simple Photo Mode", "nexus_id": 85, "type": "pak", "category": "UI & Quality of Life"},
    # Audio
    {"name": "High Quality Music Replacer", "nexus_id": 1267, "type": "pak", "category": "Audio"},
    {"name": "Armor Sound Overhaul", "nexus_id": 1987, "type": "pak", "category": "Audio"},
    # Stealth
    {"name": "Better Sneak", "nexus_id": 1921, "type": "ue4ss", "category": "Stealth", "ue4ss_folder": "BetterSneak"},
    {"name": "Harder Stealth", "nexus_id": 1732, "type": "config", "category": "Stealth", "config_dest": "gamesettings"},
    # Travel & Mounts
    {"name": "Better Cyrodiil Travel", "nexus_id": 1496, "type": "esp", "category": "Travel & Mounts", "load_order": 36, "esp_name": "BetterCyrodiilTravel.esp"},
    {"name": "Horse Improvements", "nexus_id": 1832, "type": "esp", "category": "Travel & Mounts", "load_order": 66, "esp_name": "Players Horse Improvements x1 Speed.esp"},
    {"name": "A Horse With Saddlebags", "nexus_id": 4527, "type": "esp", "category": "Travel & Mounts", "load_order": 67, "esp_name": "A Horse With Saddlebags.esp"},
    # Survival
    {"name": "Core Survival", "nexus_id": 3037, "type": "esp", "category": "Survival", "load_order": 80, "esp_name": "CoreSurvival.esp"},
    {"name": "Basic Portable Tent", "nexus_id": 967, "type": "esp", "category": "Survival", "load_order": 81, "esp_name": "BasicPortableTentUM.esp"},
    # Economy & Loot
    {"name": "Jobs of Oblivion", "nexus_id": 5189, "type": "esp", "category": "Economy & Loot", "load_order": 82, "esp_name": "JobsOfOblivion.esp"},
    {"name": "Immersive Vendor and Loot", "nexus_id": 4100, "type": "esp", "category": "Economy & Loot", "load_order": 83, "esp_name": "ImmersiveVendorAndLoot.esp"},
    {"name": "Enhanced Endgame Loot", "nexus_id": 1871, "type": "esp", "category": "Economy & Loot", "load_order": 84, "esp_name": "EnhancedEndgameLoot.esp"},
    # New Content
    {"name": "Dark Brotherhood Infinitum", "nexus_id": 3170, "type": "esp", "category": "New Content", "load_order": 90, "esp_name": "DarkBrotherhoodInfinitum.esp"},
    {"name": "Imperial Legion Infinitum", "nexus_id": 4225, "type": "esp", "category": "New Content", "load_order": 91, "esp_name": "ImperialLegionInfinitum.esp"},
    {"name": "Advanced Followers", "nexus_id": 722, "type": "esp", "category": "New Content", "load_order": 92, "esp_name": "Advanced Followers.esp"},
    {"name": "Lakeheart Manor", "nexus_id": 763, "type": "esp", "category": "New Content", "load_order": 93, "esp_name": "LuxuryHouseMod.esp"},
    {"name": "Radiant Mages Guild Quests", "nexus_id": 3858, "type": "esp", "category": "New Content", "load_order": 94, "esp_name": "MagesGuildRadiantNecroQuests.esp"},
    {"name": "Mad Spell Pack", "nexus_id": 4242, "type": "ue4ss", "category": "New Content", "ue4ss_folder": "MadSpellPack", "archive_ue4ss_folders": ["MadSpellPack", "MadTransform"]},
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

CHIM_CONFIG_DIR = Path.home() / ".config" / "chim-installer"
CHIM_CONFIG_FILE = CHIM_CONFIG_DIR / "config.json"


def load_saved_api_key() -> str:
    """Load saved Nexus API key from config file."""
    try:
        if CHIM_CONFIG_FILE.is_file():
            data = json.loads(CHIM_CONFIG_FILE.read_text())
            return data.get("nexus_api_key", "")
    except (json.JSONDecodeError, OSError):
        pass
    return ""


def save_api_key(api_key: str):
    """Save Nexus API key to config file."""
    try:
        CHIM_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        data = {}
        if CHIM_CONFIG_FILE.is_file():
            try:
                data = json.loads(CHIM_CONFIG_FILE.read_text())
            except (json.JSONDecodeError, OSError):
                pass
        data["nexus_api_key"] = api_key
        CHIM_CONFIG_FILE.write_text(json.dumps(data, indent=2))
    except OSError:
        pass

# ─── Theme ──────────────────────────────────────────────────────────────────────

COLORS = {
    "bg":           "#0c0b08",
    "bg_light":     "#15130e",
    "bg_lighter":   "#1e1b14",
    "bg_row_alt":   "#12100b",
    "bg_warm":      "#1a1610",
    "gold":         "#c9a84c",
    "gold_dim":     "#7a6530",
    "gold_bright":  "#e8cc6a",
    "gold_pale":    "#d4be7a",
    "text":         "#cdc0ae",
    "text_dim":     "#8a7e6e",
    "text_bright":  "#efe8da",
    "green":        "#6aab5c",
    "green_dim":    "#3d7a32",
    "red":          "#c45e5e",
    "blue":         "#5c9fd6",
    "border":       "#2a2518",
    "border_gold":  "#3a3020",
    "progress_bg":  "#1a1710",
    "progress_fg":  "#c9a84c",
    "btn_bg":       "#1a1710",
    "btn_hover":    "#2a2518",
    "btn_active":   "#3a3020",
    "scrollbar":    "#3a3020",
    "scrollbar_bg": "#0c0b08",
    "ornament":     "#4a3f28",
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

CATEGORY_ICONS["Stealth"]           = "\U0001f5e1"  # 🗡
CATEGORY_ICONS["Travel & Mounts"]   = "\U0001f3c7"  # 🏇
CATEGORY_ICONS["Survival"]          = "\U0001f525"  # 🔥
CATEGORY_ICONS["Economy & Loot"]    = "\U0001f4b0"  # 💰
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


# ─── Nexus API ──────────────────────────────────────────────────────────────────

NEXUS_API_BASE = "https://api.nexusmods.com/v1"
NEXUS_API_GAME = "oblivionremastered"


def nexus_api_request(endpoint: str, api_key: str) -> Optional[dict]:
    """Make an authenticated Nexus API request. Returns parsed JSON or None."""
    url = f"{NEXUS_API_BASE}{endpoint}"
    req = Request(url)
    req.add_header("apikey", api_key)
    req.add_header("Accept", "application/json")
    req.add_header("User-Agent", "CHIM-Installer/1.3")
    try:
        with urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except (HTTPError, URLError, json.JSONDecodeError):
        return None


def nexus_api_validate_key(api_key: str) -> tuple[bool, bool, str]:
    """
    Validate a Nexus API key. Returns (valid, is_premium, username).
    """
    data = nexus_api_request("/users/validate.json", api_key)
    if not data or "user_id" not in data:
        return False, False, ""
    is_premium = data.get("is_premium", False)
    username = data.get("name", "")
    return True, is_premium, username


def nexus_api_get_mod_files(nexus_id: int, api_key: str) -> Optional[list]:
    """Get the list of files for a mod."""
    data = nexus_api_request(
        f"/games/{NEXUS_API_GAME}/mods/{nexus_id}/files.json", api_key
    )
    if data and "files" in data:
        return data["files"]
    return None


def nexus_api_get_download_url(nexus_id: int, file_id: int, api_key: str) -> Optional[str]:
    """Get a download URL for a specific file (Premium only)."""
    data = nexus_api_request(
        f"/games/{NEXUS_API_GAME}/mods/{nexus_id}/files/{file_id}/download_link.json",
        api_key,
    )
    if data and isinstance(data, list) and len(data) > 0:
        return data[0].get("URI")
    return None


def nexus_api_pick_main_file(files: list) -> Optional[dict]:
    """Pick the best file to download — prefer MAIN_FILE category."""
    main_files = [f for f in files if f.get("category_name") == "MAIN"]
    if main_files:
        # Pick the most recent main file
        main_files.sort(key=lambda f: f.get("uploaded_timestamp", 0), reverse=True)
        return main_files[0]
    # Fall back to any non-archived file
    active = [f for f in files if f.get("category_name") != "ARCHIVED"]
    if active:
        active.sort(key=lambda f: f.get("uploaded_timestamp", 0), reverse=True)
        return active[0]
    return files[0] if files else None


def nexus_api_download_file(url: str, dest_path: Path, progress_cb=None) -> bool:
    """Download a file from a URL to dest_path. Optional progress callback(bytes_so_far, total)."""
    # Python 3.14+ rejects unencoded spaces in URLs — encode the path component
    from urllib.parse import urlparse, quote, urlunparse
    parsed = urlparse(url)
    safe_path = quote(parsed.path, safe="/:@!$&'()*+,;=-._~")
    url = urlunparse(parsed._replace(path=safe_path))
    req = Request(url)
    req.add_header("User-Agent", "CHIM-Installer/1.3")
    try:
        with urlopen(req, timeout=120) as resp:
            total = int(resp.headers.get("Content-Length", 0))
            downloaded = 0
            chunk_size = 65536
            with open(dest_path, "wb") as f:
                while True:
                    chunk = resp.read(chunk_size)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)
                    if progress_cb:
                        progress_cb(downloaded, total)
        return True
    except (HTTPError, URLError, OSError):
        # Clean up partial download
        if dest_path.exists():
            dest_path.unlink()
        return False


OBLIVION_APP_ID = "2623190"

LAUNCH_OPTIONS_LINUX = (
    'WINEDLLOVERRIDES="winmm=n,b" DXVK_ASYNC=1 SDL_HAPTIC_DISABLED=1 bash -c \'exec '
    '"${@/OblivionRemastered.exe/OblivionRemastered/Binaries/Win64/obse64_loader.exe}"'
    "' -- %command%"
)

LAUNCH_OPTIONS_WINDOWS = (
    '"%command%/../obse64_loader.exe"'
)


def find_steam_localconfig() -> Optional[Path]:
    """Find Steam's localconfig.vdf for the current user."""
    userdata_roots = [
        Path.home() / ".local/share/Steam/userdata",
        Path("/home/deck/.local/share/Steam/userdata"),
        Path.home() / ".var/app/com.valvesoftware.Steam/.local/share/Steam/userdata",
        # Windows paths (through Proton or native)
        Path.home() / ".steam/steam/userdata",
    ]
    for root in userdata_roots:
        if not root.is_dir():
            continue
        for user_dir in root.iterdir():
            if not user_dir.is_dir():
                continue
            config = user_dir / "config" / "localconfig.vdf"
            if config.is_file():
                return config
    return None


def get_steam_launch_options(config_path: Path, app_id: str) -> Optional[str]:
    """Read the current launch options for an app from localconfig.vdf."""
    try:
        content = config_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None

    # Simple VDF parser — find the app block and extract LaunchOptions
    lines = content.split("\n")
    in_app = False
    depth = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not in_app:
            if f'"{app_id}"' in stripped and "{" not in stripped:
                # Check if next non-empty line is {
                for j in range(i + 1, min(i + 3, len(lines))):
                    if lines[j].strip() == "{":
                        in_app = True
                        depth = 1
                        break
        else:
            if stripped == "{":
                depth += 1
            elif stripped == "}":
                depth -= 1
                if depth <= 0:
                    break
            elif '"LaunchOptions"' in stripped:
                # Extract value: "LaunchOptions"		"value"
                parts = stripped.split('"')
                # parts: ['', 'LaunchOptions', '', '', 'value', '']
                if len(parts) >= 5:
                    return parts[4] if parts[4] else parts[3]
                return ""
    return None


def set_steam_launch_options(config_path: Path, app_id: str, launch_options: str) -> bool:
    """Write launch options for an app in localconfig.vdf. Returns True on success."""
    try:
        content = config_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False

    lines = content.split("\n")
    in_app = False
    depth = 0
    found_launch = False

    for i, line in enumerate(lines):
        stripped = line.strip()
        if not in_app:
            if f'"{app_id}"' in stripped and "{" not in stripped:
                for j in range(i + 1, min(i + 3, len(lines))):
                    if lines[j].strip() == "{":
                        in_app = True
                        depth = 1
                        break
        else:
            if stripped == "{":
                depth += 1
            elif stripped == "}":
                depth -= 1
                if depth <= 0:
                    if not found_launch:
                        # Insert LaunchOptions before closing brace
                        indent = "\t" * (line.count("\t"))
                        lines.insert(i, f'{indent}\t"LaunchOptions"\t\t"{launch_options}"')
                        found_launch = True
                    break
            elif '"LaunchOptions"' in stripped:
                # Replace existing value
                indent = line[:len(line) - len(line.lstrip())]
                lines[i] = f'{indent}"LaunchOptions"\t\t"{launch_options}"'
                found_launch = True

    if not found_launch:
        return False

    try:
        # Backup original
        backup = config_path.with_suffix(".vdf.chim_backup")
        if not backup.exists():
            import shutil
            shutil.copy2(config_path, backup)
        config_path.write_text("\n".join(lines), encoding="utf-8")
        return True
    except OSError:
        return False


def detect_game_path() -> Optional[str]:
    """Try common Oblivion Remastered install locations (Linux, Deck, Windows)."""
    home = Path.home()
    candidates = [
        # Linux
        home / ".local/share/Steam/steamapps/common/Oblivion Remastered",
        home / ".steam/steam/steamapps/common/Oblivion Remastered",
        home / ".var/app/com.valvesoftware.Steam/.local/share/Steam/steamapps/common/Oblivion Remastered",
        # Steam Deck
        Path("/home/deck/.local/share/Steam/steamapps/common/Oblivion Remastered"),
        # Windows
        Path("C:/Program Files (x86)/Steam/steamapps/common/Oblivion Remastered"),
        Path("D:/SteamLibrary/steamapps/common/Oblivion Remastered"),
        Path("E:/SteamLibrary/steamapps/common/Oblivion Remastered"),
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
        except (zipfile.BadZipFile, NotImplementedError, Exception):
            # Python zipfile can't handle some compression methods (Deflate64, LZMA)
            # Fall back to system unzip or 7z
            unzip = shutil.which("unzip")
            if unzip:
                try:
                    subprocess.run(
                        [unzip, "-o", str(archive_path), "-d", str(dest_dir)],
                        check=True, capture_output=True, timeout=300,
                    )
                    return True
                except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                    pass
            exe = find_7z()
            if exe:
                try:
                    subprocess.run(
                        [exe, "x", str(archive_path), f"-o{dest_dir}", "-y"],
                        check=True, capture_output=True, timeout=300,
                    )
                    return True
                except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                    pass
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


def build_load_order(installed_mods: list[dict], game_path: Path) -> tuple[Path, list[str]]:
    """
    Generate Plugins.txt with correct load order for all installed ESP/ESM mods.
    IMPORTANT: Format is plain filenames, NO asterisk prefix.
    Vanilla ESM/ESPs must be listed first.
    Returns (plugins_path, list_of_plugin_names).
    """
    data_dir = game_path / "OblivionRemastered" / "Content" / "Dev" / "ObvData" / "Data"

    # Vanilla load order — must come first, in this exact order
    vanilla_plugins = [
        "Oblivion.esm",
        "DLCBattlehornCastle.esp", "DLCFrostcrag.esp", "DLCHorseArmor.esp",
        "DLCMehrunesRazor.esp", "DLCOrrery.esp", "DLCShiveringIsles.esp",
        "DLCSpellTomes.esp", "DLCThievesDen.esp", "DLCVileLair.esp",
        "Knights.esp", "AltarESPMain.esp", "AltarDeluxe.esp",
    ]

    # Collect all ESP mods that have load_order defined, sort by it
    esp_mods = [m for m in installed_mods if m.get("load_order") is not None]
    esp_mods.sort(key=lambda m: m["load_order"])

    # Also discover any .esp/.esm files actually on disk that we didn't track
    on_disk = set()
    if data_dir.is_dir():
        for f in data_dir.iterdir():
            if f.is_file() and f.suffix.lower() in (".esp", ".esm"):
                on_disk.add(f.name)

    # Build ordered plugin list
    ordered = []
    seen = set()

    # Vanilla first
    for plugin in vanilla_plugins:
        if plugin in on_disk:
            ordered.append(plugin)
            seen.add(plugin)

    # Then mod ESPs in defined load order
    for mod in esp_mods:
        esp_name = mod.get("esp_name")
        if esp_name and esp_name not in seen:
            ordered.append(esp_name)
            seen.add(esp_name)

    # Then any on-disk plugins we didn't have in our load order
    for name in sorted(on_disk):
        if name not in seen:
            ordered.append(name)
            seen.add(name)

    # Write Plugins.txt — plain filenames, NO asterisk prefix
    plugins_path = data_dir / "Plugins.txt"
    lines = []
    for plugin in ordered:
        lines.append(f"{plugin}\n")

    plugins_path.write_text("".join(lines))
    return plugins_path, ordered


def backup_existing_mods(game_path: Path) -> Optional[Path]:
    """
    Create a backup of existing mod files before CHIM install.
    Returns backup directory path, or None if nothing to back up.
    """
    from datetime import datetime

    data_dir = game_path / "OblivionRemastered" / "Content" / "Dev" / "ObvData" / "Data"
    paks_dir = game_path / "OblivionRemastered" / "Content" / "Paks" / "~mods"
    obse_dir = game_path / "OblivionRemastered" / "Binaries" / "Win64" / "OBSE" / "Plugins"
    ue4ss_root = game_path / "OblivionRemastered" / "Binaries" / "Win64" / "ue4ss"

    # Check if there's anything to back up
    has_files = False
    for d in [data_dir, paks_dir, obse_dir, ue4ss_root]:
        if d.is_dir() and any(d.iterdir()):
            has_files = True
            break

    if not has_files:
        return None

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = game_path / f"CHIM_backup_{timestamp}"
    backup_dir.mkdir(parents=True, exist_ok=True)

    for label, src_dir in [("Data", data_dir), ("Paks_mods", paks_dir),
                           ("OBSE_Plugins", obse_dir), ("UE4SS", ue4ss_root)]:
        if not src_dir.is_dir():
            continue
        dest = backup_dir / label
        dest.mkdir(parents=True, exist_ok=True)
        for f in src_dir.iterdir():
            if f.is_file():
                shutil.copy2(f, dest / f.name)
            elif f.is_dir():
                shutil.copytree(f, dest / f.name, dirs_exist_ok=True)

    return backup_dir


def verify_installation(installed_mods: list[dict], game_path: Path) -> tuple[list[str], list[str]]:
    """
    Post-install verification: check that all mod files actually landed.
    Returns (successes, failures).
    """
    data_dir = game_path / "OblivionRemastered" / "Content" / "Dev" / "ObvData" / "Data"
    paks_dir = game_path / "OblivionRemastered" / "Content" / "Paks" / "~mods"
    obse_dir = game_path / "OblivionRemastered" / "Binaries" / "Win64" / "OBSE" / "Plugins"
    ue4ss_dir = game_path / "OblivionRemastered" / "Binaries" / "Win64" / "ue4ss" / "Mods"
    bin_dir = game_path / "OblivionRemastered" / "Binaries" / "Win64"

    successes = []
    failures = []

    for mod in installed_mods:
        mod_type = mod["type"]
        name = mod["name"]

        if mod_type == "esp":
            esp_name = mod.get("esp_name")
            if esp_name:
                if (data_dir / esp_name).is_file():
                    successes.append(f"{name}: {esp_name} found in Data/")
                else:
                    # Check if ANY .esp from this mod exists (name might differ)
                    found = any(f.suffix.lower() in (".esp", ".esm") for f in data_dir.iterdir() if f.is_file())
                    if found:
                        successes.append(f"{name}: ESP found in Data/ (name may differ from expected)")
                    else:
                        failures.append(f"{name}: expected {esp_name} in Data/ — NOT FOUND")
            else:
                # No esp_name defined, just check data_dir has files
                successes.append(f"{name}: no specific ESP name to verify")

        elif mod_type == "pak":
            # Check for any .pak files in ~mods
            if paks_dir.is_dir() and any(f.suffix.lower() == ".pak" for f in paks_dir.iterdir() if f.is_file()):
                successes.append(f"{name}: PAK files present in ~mods/")
            else:
                failures.append(f"{name}: no PAK files found in ~mods/")

        elif mod_type == "obse":
            if obse_dir.is_dir() and any(f.suffix.lower() == ".dll" for f in obse_dir.iterdir() if f.is_file()):
                successes.append(f"{name}: DLL files present in OBSE/Plugins/")
            else:
                failures.append(f"{name}: no DLL files found in OBSE/Plugins/")

        elif mod_type == "obse_framework":
            obse_loader = bin_dir / "obse64_loader.exe"
            if obse_loader.is_file():
                successes.append(f"{name}: obse64_loader.exe found")
            else:
                failures.append(f"{name}: obse64_loader.exe NOT FOUND in Binaries/Win64/")

        elif mod_type == "ue4ss_framework":
            # UE4SS for Oblivion Remastered uses dwmapi.dll as proxy loader
            # and keeps actual files in ue4ss/ subfolder
            dwmapi = bin_dir / "dwmapi.dll"
            ue4ss_dll = bin_dir / "ue4ss" / "UE4SS.dll"
            ue4ss_alt = bin_dir / "UE4SS.dll"
            xinput = bin_dir / "xinput1_3.dll"
            if dwmapi.is_file() or ue4ss_dll.is_file() or ue4ss_alt.is_file() or xinput.is_file():
                successes.append(f"{name}: UE4SS framework files found")
            else:
                failures.append(f"{name}: UE4SS framework NOT FOUND in Binaries/Win64/")

        elif mod_type == "ue4ss":
            folder_name = mod.get("ue4ss_folder", name.replace(" ", ""))
            mod_dir = ue4ss_dir / folder_name
            enabled = mod_dir / "enabled.txt"
            is_optional = mod.get("optional", False)
            if mod_dir.is_dir():
                if is_optional:
                    # Optional mods have enabled.txt intentionally deleted
                    successes.append(f"{name}: folder '{folder_name}' found (optional, disabled by default)")
                elif enabled.is_file():
                    successes.append(f"{name}: folder '{folder_name}' found + enabled")
                else:
                    failures.append(f"{name}: folder '{folder_name}' exists but missing enabled.txt")
            else:
                failures.append(f"{name}: folder '{folder_name}' NOT FOUND in ue4ss/Mods/")

        elif mod_type == "config":
            successes.append(f"{name}: config mod (verified during deploy)")

        elif mod_type == "obse_config":
            if obse_dir.is_dir() and any(f.suffix.lower() in (".json", ".ini") for f in obse_dir.iterdir() if f.is_file()):
                successes.append(f"{name}: config files found in OBSE/Plugins/")
            else:
                failures.append(f"{name}: no config files found in OBSE/Plugins/")

    return successes, failures


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
        # UE4SS framework: proxy DLL goes to Binaries/Win64/, everything else
        # goes to Binaries/Win64/ue4ss/ preserving structure.
        # IMPORTANT: Skip bundled mod folders — they conflict with built-in UE4SS modules
        PROXY_DLLS = {"winmm.dll", "dwmapi.dll", "xinput1_3.dll", "xinput9_1_0.dll"}
        SKIP_MOD_FOLDERS = {"bpml_genericfunctions", "bpmodloadermod"}

        # Find root (may have a wrapper folder)
        root = extracted_dir
        subdirs = [d for d in extracted_dir.iterdir() if d.is_dir()]
        loose_files = [f for f in extracted_dir.iterdir() if f.is_file() and f.suffix.lower() in (".dll", ".exe", ".ini")]
        if len(subdirs) == 1 and not loose_files:
            root = subdirs[0]

        ue4ss_dest = bin_dir / "ue4ss"
        ue4ss_dest.mkdir(parents=True, exist_ok=True)

        for f in root.rglob("*"):
            if not f.is_file():
                continue
            rel = f.relative_to(root)
            parts = rel.parts
            parts_lower = [p.lower() for p in parts]

            # Skip bundled framework mod folders (conflict with built-in)
            if any(skip in parts_lower for skip in SKIP_MOD_FOLDERS):
                continue

            if f.name.lower() in PROXY_DLLS:
                # Proxy DLL goes to Binaries/Win64/ root
                dest = bin_dir / f.name
                shutil.copy2(f, dest)
                installed += 1
            elif len(parts) >= 2 and parts[0].lower() == "ue4ss":
                # Already in a ue4ss/ subfolder — preserve relative path
                dest = bin_dir / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(f, dest)
                installed += 1
            else:
                # Everything else (UE4SS.dll, settings, Mods/) goes to ue4ss/
                dest = ue4ss_dest / rel
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
        # Find the expected ESP name if defined
        expected_esp = None
        for m in MODS + DECK_OPTIMIZATION_MODS:
            if m["name"] == mod_name:
                expected_esp = m.get("esp_name")
                break

        for f in all_files:
            ext = f.suffix.lower()
            if ext in (".esp", ".esm"):
                # If we know the expected ESP name, only install that one
                # (prevents patch ESPs for other mods from being installed)
                if expected_esp:
                    if f.name == expected_esp:
                        dest = data_dir / f.name
                        shutil.copy2(f, dest)
                        installed += 1
                else:
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
            elif ext in (".json",):
                # JSON configs (e.g. MagicLoader) — preserve subfolder structure under Data
                rel = f.relative_to(content_root)
                # Find the "Data" part in the path and keep everything after
                rel_str = str(rel)
                data_idx = rel_str.lower().find("data")
                if data_idx >= 0:
                    after = rel_str[data_idx + 4:].lstrip("/\\")
                    dest = data_dir / after if after else data_dir / f.name
                else:
                    dest = data_dir / f.name
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(f, dest)
                installed += 1

    elif mod_type == "pak":
        # PAK files are deployed from patches/ (tested versions).
        # From Nexus archives we only extract ESPs, JSONs, and other non-PAK content.
        for f in all_files:
            ext = f.suffix.lower()
            if ext in (".esp", ".esm"):
                dest = data_dir / f.name
                shutil.copy2(f, dest)
                installed += 1
            elif ext == ".json":
                # MagicLoader configs and similar — preserve relative path under Data/
                rel = f.relative_to(content_root)
                rel_str = str(rel)
                # Route MagicLoader files to Data/MagicLoader/
                if "magicloader" in rel_str.lower():
                    magic_dir = data_dir / "MagicLoader"
                    magic_dir.mkdir(parents=True, exist_ok=True)
                    dest = magic_dir / f.name
                else:
                    dest = data_dir / f.name
                shutil.copy2(f, dest)
                installed += 1

    elif mod_type == "obse":
        for f in all_files:
            ext = f.suffix.lower()
            if ext in (".dll", ".ini", ".bin", ".pdb"):
                dest = obse_dir / f.name
                shutil.copy2(f, dest)
                installed += 1
            elif ext in (".esp", ".esm"):
                dest = data_dir / f.name
                shutil.copy2(f, dest)
                installed += 1

    elif mod_type == "ue4ss":
        # UE4SS mods — many archives bundle full game paths or the entire UE4SS framework.
        # Strategy: walk ALL extracted files, detect game-path patterns, route each file.
        folder_name = None
        archive_folders = None
        is_optional = False
        no_enabled = False
        for m in MODS + DECK_OPTIMIZATION_MODS:
            if m["name"] == mod_name:
                folder_name = m.get("ue4ss_folder")
                archive_folders = m.get("archive_ue4ss_folders")
                is_optional = m.get("optional", False)
                no_enabled = m.get("no_enabled_txt", False)
                break
        if not folder_name:
            folder_name = mod_name.replace(" ", "")

        # Build set of folder names to extract from archives
        target_folders = {folder_name}
        if archive_folders:
            target_folders.update(archive_folders)

        mod_dir = ue4ss_mods_dir / folder_name
        mod_dir.mkdir(parents=True, exist_ok=True)

        # Use ALL files from extracted_dir (not content_root) to preserve full paths
        all_extracted = [f for f in extracted_dir.rglob("*") if f.is_file()]

        # Detect if this archive has a game-path structure
        has_game_path = any(
            "ue4ss" in str(f.relative_to(extracted_dir)).lower() and
            "mods" in str(f.relative_to(extracted_dir)).lower()
            for f in all_extracted
        )

        if has_game_path:
            # Archive contains game-path structure — route files by path patterns
            for f in all_extracted:
                rel_str = str(f.relative_to(extracted_dir))
                rel_lower = rel_str.lower()

                # Skip bundled UE4SS framework files (we have our own)
                fname_lower = f.name.lower()
                if fname_lower in ("ue4ss.dll", "ue4ss-settings.ini", "ue4ss.pdb",
                                   "dwmapi.dll", "winmm.dll", "xinput1_3.dll"):
                    continue
                # Skip bundled framework mod folders
                parts_lower = [p.lower() for p in Path(rel_str).parts]
                if any(skip in parts_lower for skip in ("bpml_genericfunctions", "bpmodloadermod", "shared")):
                    continue

                # Route ESPs
                if f.suffix.lower() in (".esp", ".esm"):
                    dest = data_dir / f.name
                    shutil.copy2(f, dest)
                    installed += 1
                # Route PAKs
                elif f.suffix.lower() in (".pak", ".ucas", ".utoc"):
                    dest = paks_dir / f.name
                    shutil.copy2(f, dest)
                    installed += 1
                # Route UE4SS mod files — find files under a target folder name
                elif any(tf.lower() in parts_lower for tf in target_folders):
                    # Find which target folder this belongs to and extract relative path within it
                    for tf in target_folders:
                        tf_idx = None
                        for i, part in enumerate(Path(rel_str).parts):
                            if part.lower() == tf.lower():
                                tf_idx = i
                                break
                        if tf_idx is not None:
                            inner_rel = Path(*Path(rel_str).parts[tf_idx + 1:])
                            # Map all archive folders into the single target folder
                            dest = mod_dir / inner_rel
                            dest.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(f, dest)
                            installed += 1
                            break
                # Route other files (configs like MadConfigs/) to bin_dir preserving structure
                elif f.suffix.lower() in (".ini", ".cfg", ".json", ".txt"):
                    # Try to find a reasonable relative path from Binaries/Win64/
                    if "win64" in rel_lower:
                        idx = parts_lower.index("win64")
                        after = Path(*Path(rel_str).parts[idx + 1:])
                        # Skip if it's in ue4ss/Mods for a folder we don't want
                        if "ue4ss" not in str(after).lower():
                            dest = bin_dir / after
                            dest.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(f, dest)
                            installed += 1
        else:
            # Simple archive — no game paths, use content_root approach
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

        # Set enabled.txt — data mods and optional mods should NOT have it
        enabled = mod_dir / "enabled.txt"
        if no_enabled or is_optional:
            if enabled.exists():
                enabled.unlink()
        else:
            enabled.write_text("1\n")

    elif mod_type == "obse_config":
        # OBSE plugin config files (JSON/INI) — go to OBSE/Plugins/
        obse_plugins_dir = game_path / "OblivionRemastered" / "Binaries" / "Win64" / "OBSE" / "Plugins"
        obse_plugins_dir.mkdir(parents=True, exist_ok=True)
        for f in all_files:
            ext = f.suffix.lower()
            if ext in (".json", ".ini", ".cfg", ".txt"):
                dest = obse_plugins_dir / f.name
                shutil.copy2(f, dest)
                installed += 1

    elif mod_type == "config":
        # Config/optimization mods — route INIs to correct location
        # Look up config_dest for this mod
        config_dest = None
        for m in MODS + DECK_OPTIMIZATION_MODS:
            if m["name"] == mod_name:
                config_dest = m.get("config_dest")
                break

        gamesettings_dir = game_path / "OblivionRemastered" / "Binaries" / "Win64" / "OBSE" / "Plugins" / "GameSettings"

        for f in all_files:
            ext = f.suffix.lower()
            name_lower = f.name.lower()
            if ext == ".ini":
                if config_dest == "gamesettings":
                    # OBSE GameSettings INI (e.g. Harder Stealth)
                    gamesettings_dir.mkdir(parents=True, exist_ok=True)
                    dest = gamesettings_dir / f.name
                elif "engine" in name_lower:
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

    if installed == 0 and mod_type != "pak":
        # PAK mods may have 0 installed files because PAKs are deployed from patches/
        errors.append(f"No recognized files found in archive for {mod_name}")

    return installed, errors


# ─── Custom Widgets ─────────────────────────────────────────────────────────────

class GoldButton(tk.Canvas):
    """An ornate Elder Scrolls themed button with gold border and corner decorations."""

    def __init__(self, parent, text="", command=None, width=200, height=40,
                 font_size=11, enabled=True, accent=None, **kwargs):
        # Detect parent bg color for seamless blending
        try:
            parent_bg = parent.cget("bg")
        except Exception:
            parent_bg = COLORS["bg"]
        super().__init__(
            parent, width=width, height=height,
            bg=parent_bg, highlightthickness=0, **kwargs,
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
        self._parent_bg = parent_bg

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)

        self._draw()

    def _draw(self):
        self.delete("all")
        w, h = self._width, self._height
        r = 3

        if self._enabled:
            if self._hovered:
                border_color = self._accent
                fill = COLORS["bg_warm"]
                text_color = COLORS["gold_bright"]
            else:
                border_color = self._accent_dim
                fill = COLORS["btn_bg"]
                text_color = COLORS["text"]
        else:
            border_color = COLORS["border"]
            fill = COLORS["bg_light"]
            text_color = COLORS["text_dim"]

        # Single clean border
        self._round_rect(1, 1, w - 1, h - 1, r, outline=border_color, fill=fill, width=1.5)

        # Subtle top highlight on hover
        if self._enabled and self._hovered:
            mid = w // 2
            self.create_line(mid - 30, 2, mid + 30, 2, fill=self._accent, width=1)

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
    """Ornate Elder Scrolls themed progress bar with double border."""

    def __init__(self, parent, width=700, height=26, **kwargs):
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
        r = 4

        # Outer border
        self._round_rect(0, 0, w, h, r, fill=COLORS["progress_bg"], outline=COLORS["gold_dim"], width=1)
        # Inner border
        self._round_rect(3, 3, w - 3, h - 3, r - 1, fill=COLORS["progress_bg"], outline=COLORS["border_gold"], width=0.5)

        # Filled portion
        if self._value > 0:
            fw = max(12, int((w - 6) * self._value))
            self._round_rect(3, 3, fw + 3, h - 3, r - 1, fill=COLORS["progress_fg"], outline="")
            # Gold shimmer highlight on filled portion
            if fw > 20:
                self.create_line(6, 6, fw, 6, fill=COLORS["gold_bright"], width=1)

        # Percentage text
        pct = int(self._value * 100)
        self.create_text(
            w // 2, h // 2, text=f"\u2726 {pct}% \u2726",
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
        self.root.resizable(True, True)

        # Window size — adapt to screen, fit Steam Deck 1280x800
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        if sh <= 800:
            # Steam Deck or small screen
            ww, wh = min(720, sw - 40), min(580, sh - 60)
        else:
            ww, wh = 800, 700
        self.root.minsize(640, 480)
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

        # Main container
        self.container = tk.Frame(self.root, bg=COLORS["bg"])
        self.container.pack(fill="both", expand=True)

        # Start with welcome screen
        self._show_welcome()

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

    def _clear_container(self):
        for w in self.container.winfo_children():
            w.destroy()
        self._stop_watcher()

    def _make_label(self, parent, text, size=11, color=None, bold=False, **kwargs):
        weight = "bold" if bold else "normal"
        font_family = "Cinzel" if bold and size >= 18 else "Segoe UI"
        return tk.Label(
            parent, text=text, bg=COLORS["bg"],
            fg=color or COLORS["text"],
            font=(font_family, size, weight),
            **kwargs,
        )

    def _make_separator(self, parent):
        sep = tk.Frame(parent, bg=COLORS["border_gold"], height=1)
        sep.pack(fill="x", padx=40, pady=8)
        return sep

    # ─── Welcome Screen ────────────────────────────────────────────────────

    def _make_ornament_line(self, parent, width=300):
        """Draw an ornate horizontal divider with diamond center."""
        c = tk.Canvas(parent, width=width, height=16, bg=COLORS["bg"], highlightthickness=0)
        mid = width // 2
        # Main line
        c.create_line(20, 8, width - 20, 8, fill=COLORS["gold_dim"], width=1)
        # Center diamond
        c.create_polygon(mid, 2, mid + 6, 8, mid, 14, mid - 6, 8,
                         fill=COLORS["gold_dim"], outline=COLORS["gold"])
        # End caps
        for x in [20, width - 20]:
            c.create_oval(x - 2, 6, x + 2, 10, fill=COLORS["gold_dim"], outline="")
        return c

    def _show_welcome(self):
        self._clear_container()
        frame = tk.Frame(self.container, bg=COLORS["bg"])
        frame.pack(expand=True)

        # Top ornament
        self._make_ornament_line(frame, 500).pack(pady=(0, 50))

        # Title with glow effect
        title_canvas = tk.Canvas(frame, width=700, height=80, bg=COLORS["bg"], highlightthickness=0)
        title_canvas.pack(pady=(0, 12))
        # Outer glow
        for ox, oy in [(-3,0),(3,0),(0,-3),(0,3),(-3,-3),(3,3),(3,-3),(-3,3),(-2,-2),(2,2)]:
            title_canvas.create_text(350+ox, 40+oy, text="C   H   I   M",
                fill="#3d2e10", font=("Cinzel", 56, "bold"))
        # Inner glow
        for ox, oy in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,1)]:
            title_canvas.create_text(350+ox, 40+oy, text="C   H   I   M",
                fill="#6a5020", font=("Cinzel", 56, "bold"))
        # Actual title
        title_canvas.create_text(350, 40, text="C   H   I   M",
            fill=COLORS["gold"], font=("Cinzel", 56, "bold"))

        # Description
        tk.Label(
            frame, text="Oblivion Remastered Modpack", bg=COLORS["bg"],
            fg="#e8e0d0", font=("Segoe UI", 14),
        ).pack(pady=(0, 10))

        # Glowing lore text
        lore_text = "The Elder Scrolls secret syllable of royalty \u2014\nthe power to see through the dream and rewrite it."
        lore_canvas = tk.Canvas(frame, width=600, height=56, bg=COLORS["bg"], highlightthickness=0)
        lore_canvas.pack(pady=(0, 50))
        # Outer glow
        for ox, oy in [(-2,0),(2,0),(0,-2),(0,2),(-2,-2),(2,2),(2,-2),(-2,2)]:
            lore_canvas.create_text(300+ox, 28+oy, text=lore_text,
                fill="#3d3018", font=("Segoe UI", 11), justify="center")
        # Inner glow
        for ox, oy in [(-1,0),(1,0),(0,-1),(0,1)]:
            lore_canvas.create_text(300+ox, 28+oy, text=lore_text,
                fill="#5a4520", font=("Segoe UI", 11), justify="center")
        # Actual text — warm orange offset from gold title
        lore_canvas.create_text(300, 28, text=lore_text,
            fill="#e07830", font=("Segoe UI", 11), justify="center")

        # Center ornament
        self._make_ornament_line(frame, 350).pack(pady=(0, 50))

        # Begin button
        GoldButton(
            frame, text="Begin Installation", command=self._show_profile,
            width=260, height=48, font_size=13,
        ).pack()

        # Bottom ornament + version
        self._make_ornament_line(frame, 250).pack(pady=(50, 10))
        tk.Label(
            frame, text="v1.3", bg=COLORS["bg"],
            fg=COLORS["ornament"], font=("Segoe UI", 8),
        ).pack()

    def _animate_welcome(self):
        """Fade in welcome screen elements."""
        # Simple opacity simulation — we just delay showing elements
        # tkinter doesn't support true alpha, but we can stagger reveals
        pass  # The canvas draws instantly; animation is handled by the visual weight

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
        pc_count = len(MODS)
        tk.Label(pc_frame, text=f"{pc_count} mods. Max quality visuals, combat overhaul, AI improvements,\n"
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
        frame.pack(fill="both", expand=True, padx=30, pady=20)

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

        # Nexus API auto-download row
        api_frame = tk.Frame(frame, bg=COLORS["bg_light"], padx=10, pady=6)
        api_frame.pack(fill="x", padx=30, pady=(0, 8))

        self._api_status_lbl = self._make_label(api_frame, "", size=9, color=COLORS["text_dim"])
        self._api_status_lbl.config(bg=COLORS["bg_light"])
        self._api_status_lbl.pack(side="left", padx=(0, 8))

        # Check for saved API key
        saved_key = load_saved_api_key()
        if saved_key:
            self._api_status_lbl.config(text="Nexus API key saved \u2714", fg=COLORS["green"])

        self._auto_dl_btn = GoldButton(
            api_frame, text="Auto-Download All", command=self._prompt_api_key,
            width=160, height=30, font_size=9,
        )
        self._auto_dl_btn.pack(side="right")

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

            # Mod name (with optional warning)
            display_name = mod["name"]
            name_color = COLORS["text"]
            if mod.get("optional"):
                display_name = f"{mod['name']}  \u26a0"
                name_color = COLORS["gold_dim"]
            name_lbl = tk.Label(
                row, text=display_name, bg=bg, fg=name_color,
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
            width=280, height=38, font_size=10,
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
            short_name = mod["name"] if len(mod["name"]) <= 30 else mod["name"][:27] + "..."
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

    # ─── Nexus API Auto-Download ─────────────────────────────────────────

    def _prompt_api_key(self):
        """Show a popup dialog for the API key, then start auto-download."""
        saved_key = load_saved_api_key()

        # If we have a saved key, use it directly
        if saved_key:
            self._api_status_lbl.config(text="Using saved API key...", fg=COLORS["gold"])
            self._auto_dl_btn.set_enabled(False)
            self.root.update_idletasks()
            threading.Thread(target=self._run_auto_download, args=(saved_key,), daemon=True).start()
            return

        # Popup dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Nexus API Key")
        dialog.configure(bg=COLORS["bg"])
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()

        # Center on parent
        dw, dh = 480, 200
        x = self.root.winfo_x() + (self.root.winfo_width() - dw) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - dh) // 2
        dialog.geometry(f"{dw}x{dh}+{x}+{y}")

        self._make_label(dialog, "Nexus Mods API Key", size=14, color=COLORS["gold"], bold=True).pack(pady=(20, 4))
        self._make_label(dialog, "Premium required. Find your key at nexusmods.com \u2192 account settings.", size=9, color=COLORS["text_dim"]).pack(pady=(0, 12))

        key_var = tk.StringVar()
        entry = tk.Entry(
            dialog, textvariable=key_var,
            bg=COLORS["bg_lighter"], fg=COLORS["text"],
            insertbackground=COLORS["gold"], font=("Segoe UI", 10),
            relief="flat", bd=0, width=50,
            highlightthickness=1, highlightcolor=COLORS["gold_dim"],
            highlightbackground=COLORS["border"],
        )
        entry.pack(padx=30, ipady=8)
        entry.focus_set()

        btn_row = tk.Frame(dialog, bg=COLORS["bg"])
        btn_row.pack(pady=(16, 20))

        def on_ok():
            api_key = key_var.get().strip()
            if not api_key:
                return
            save_api_key(api_key)
            dialog.destroy()
            self._api_status_lbl.config(text="Validating key...", fg=COLORS["gold"])
            self._auto_dl_btn.set_enabled(False)
            self.root.update_idletasks()
            threading.Thread(target=self._run_auto_download, args=(api_key,), daemon=True).start()

        def on_cancel():
            dialog.destroy()

        GoldButton(btn_row, text="Download All", command=on_ok, width=140, height=36, font_size=10).pack(side="left", padx=(0, 10))
        GoldButton(btn_row, text="Cancel", command=on_cancel, width=100, height=36, font_size=10).pack(side="left")

        # Enter key triggers OK
        dialog.bind("<Return>", lambda e: on_ok())

    def _run_auto_download(self, api_key: str):
        """Background thread: validate key, then download all pending mods."""
        # Validate
        valid, is_premium, username = nexus_api_validate_key(api_key)
        if not valid:
            self.root.after(0, lambda: self._api_status_lbl.config(
                text="Invalid API key", fg=COLORS["red"]))
            self.root.after(0, lambda: self._auto_dl_btn.set_enabled(True))
            return

        if not is_premium:
            self.root.after(0, lambda: self._api_status_lbl.config(
                text=f"Hi {username} — Premium required for auto-download", fg=COLORS["red"]))
            self.root.after(0, lambda: self._auto_dl_btn.set_enabled(True))
            return

        self.root.after(0, lambda: self._api_status_lbl.config(
            text=f"Premium \u2714  Downloading as {username}...", fg=COLORS["green"]))

        # Download each pending mod
        pending = [m for m in self.active_mods
                   if self.mod_status[m["nexus_id"]] not in (STATUS_DOWNLOADED, STATUS_SKIPPED)]
        total = len(pending)

        for idx, mod in enumerate(pending):
            nid = mod["nexus_id"]
            name = mod["name"]

            self.root.after(0, lambda n=name, i=idx: self._api_status_lbl.config(
                text=f"[{i+1}/{total}] {n}...", fg=COLORS["gold"]))

            # Get file list
            files = nexus_api_get_mod_files(nid, api_key)
            if not files:
                self.root.after(0, lambda n=name: self._api_status_lbl.config(
                    text=f"Failed to get files for {n}", fg=COLORS["red"]))
                continue

            # Pick main file
            file_info = nexus_api_pick_main_file(files)
            if not file_info:
                continue

            file_id = file_info["file_id"]
            file_name = file_info.get("file_name", f"{nid}.zip")

            # Get download URL
            dl_url = nexus_api_get_download_url(nid, file_id, api_key)
            if not dl_url:
                self.root.after(0, lambda n=name: self._api_status_lbl.config(
                    text=f"Failed to get download link for {n}", fg=COLORS["red"]))
                continue

            # Download to Downloads dir
            dest = self.downloads_dir / file_name

            def progress_cb(downloaded, total_bytes, mod_name=name, mod_idx=idx):
                if total_bytes > 0:
                    pct = int(downloaded / total_bytes * 100)
                    self.root.after(0, lambda p=pct, n=mod_name, i=mod_idx: self._api_status_lbl.config(
                        text=f"[{i+1}/{total}] {n}... {p}%", fg=COLORS["gold"]))

            ok = nexus_api_download_file(dl_url, dest, progress_cb)
            if ok:
                self.mod_status[nid] = STATUS_DOWNLOADED
                self.mod_files[nid] = dest
                self.root.after(0, self._update_download_ui)
            else:
                self.root.after(0, lambda n=name: self._api_status_lbl.config(
                    text=f"Download failed: {n}", fg=COLORS["red"]))

            # Brief pause to avoid rate limiting (1 req/sec limit)
            import time
            time.sleep(1.0)

        # Done
        done = sum(1 for s in self.mod_status.values() if s in (STATUS_DOWNLOADED, STATUS_SKIPPED))
        self.root.after(0, lambda d=done: self._api_status_lbl.config(
            text=f"Auto-download complete — {d}/{len(self.active_mods)} ready", fg=COLORS["green"]))
        self.root.after(0, lambda: self._auto_dl_btn.set_enabled(True))
        self.root.after(0, self._update_download_ui)

    # ─── Verification Screen ──────────────────────────────────────────────

    def _show_verify(self):
        self._stop_watcher()
        self._clear_container()

        frame = tk.Frame(self.container, bg=COLORS["bg"])
        frame.pack(fill="both", expand=True, padx=30, pady=20)

        self._make_label(frame, "Verifying Mods", size=22, color=COLORS["gold"], bold=True).pack(anchor="w", pady=(0, 6))
        self._make_label(
            frame, "Checking archives, file types, conflicts, and disk space before installing...",
            size=10, color=COLORS["text_dim"],
        ).pack(anchor="w", pady=(0, 20))

        self._verify_progress = ProgressBar(frame, width=700, height=24)
        self._verify_progress.pack(pady=(0, 16))

        self._verify_status = self._make_label(frame, "Starting verification...", size=11, color=COLORS["text"])
        self._verify_status.pack(anchor="w", pady=(0, 10))

        # Button frame — pack at bottom FIRST so it's always visible
        self._verify_btn_frame = tk.Frame(frame, bg=COLORS["bg"])
        self._verify_btn_frame.pack(side="bottom", fill="x", pady=(10, 0))

        # Log area — fills remaining space
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

            # PAK mods: PAK files are deployed from patches/, so we only need
            # ESPs/JSONs from the archive. If it only has PAKs, that's fine.
            if mod["type"] == "pak":
                has_paks = bool(extensions & {".pak", ".ucas", ".utoc"})
                has_extras = bool(extensions & {".esp", ".esm", ".json"})
                if has_paks or has_extras:
                    self._vlog(f"  [{idx+1}/{total}] {mod['name']}: OK ({len(all_files)} files, PAKs bundled)", "green")
                else:
                    self._vlog(f"  [{idx+1}/{total}] {mod['name']}: OK (PAKs deployed from bundle)", "green")
            else:
                expected_map = {
                    "esp": {".esp", ".esm", ".bsa", ".ini"},
                    "obse": {".dll", ".ini", ".esp", ".esm", ".bin", ".pdb"},
                    "ue4ss": {".lua", ".txt", ".ini", ".dll", ".json", ".pak", ".ucas", ".utoc", ".esp", ".esm"},
                    "config": {".ini", ".txt", ".cfg", ".json"},
                    "obse_config": {".json", ".ini", ".cfg", ".txt", ".xml"},
                }
                expected = expected_map.get(mod["type"], set())
                relevant = extensions & expected

                if not relevant and len(all_files) > 0:
                    self._vlog(f"  [{idx+1}/{total}] {mod['name']}: no expected files found (has: {', '.join(extensions)})", "red")
                    issues.append(f"{mod['name']}: archive doesn't contain expected file types for {mod['type']} mod")
                else:
                    # Check for file conflicts (skip known shared framework files)
                    shared_files = {"ue4ss.dll", "dwmapi.dll", "xinput1_3.dll", "ue4ss-settings.ini"}
                    for f in all_files:
                        ext = f.suffix.lower()
                        if ext in (".esp", ".esm", ".pak", ".ucas", ".utoc", ".dll"):
                            key = f.name.lower()
                            if key in shared_files:
                                continue
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
        frame.pack(fill="both", expand=True, padx=30, pady=20)

        self._make_label(frame, "Installing Mods", size=22, color=COLORS["gold"], bold=True).pack(anchor="w", pady=(0, 6))
        self._make_label(
            frame, "Extracting archives and placing files...",
            size=10, color=COLORS["text_dim"],
        ).pack(anchor="w", pady=(0, 20))

        self._install_progress = ProgressBar(frame, width=700, height=24)
        self._install_progress.pack(pady=(0, 20))

        self._install_status = self._make_label(frame, "Preparing...", size=11, color=COLORS["text"])
        self._install_status.pack(anchor="w", pady=(0, 10))

        # Button frame — pack at bottom FIRST so it's always visible
        self._install_btn_frame = tk.Frame(frame, bg=COLORS["bg"])
        self._install_btn_frame.pack(side="bottom", fill="x", pady=(10, 0))

        # Log area — fills remaining space
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
        try:
            self._run_install_inner()
        except Exception as e:
            import traceback
            print(f"INSTALL CRASHED: {e}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            self._log(f"FATAL ERROR: {e}", "red")

    def _run_install_inner(self):
        game_path = Path(self.game_path)
        bin_dir = game_path / "OblivionRemastered" / "Binaries" / "Win64"
        data_dir = game_path / "OblivionRemastered" / "Content" / "Dev" / "ObvData" / "Data"
        paks_dir = game_path / "OblivionRemastered" / "Content" / "Paks" / "~mods"
        ue4ss_dir = bin_dir / "ue4ss"
        ue4ss_mods_dir = ue4ss_dir / "Mods"
        obse_dir = bin_dir / "OBSE" / "Plugins"
        patches_base = Path(getattr(sys, '_MEIPASS', None) or Path(__file__).parent) / "patches"

        to_install = [m for m in self.active_mods if self.mod_status[m["nexus_id"]] == STATUS_DOWNLOADED]
        total = len(to_install)

        if total == 0:
            self._log("No mods to install.", "red")
            self.root.after(1000, self._show_done)
            return

        is_deck = self.profile == PROFILE_DECK
        profile_label = "CHIM Deck" if is_deck else "CHIM"
        self._log(f"Installing {total} mods ({profile_label}) to:", "gold")
        self._log(f"  {game_path}", "dim")
        self._log("")

        errors_total = []
        config_dir = self._find_saved_config_dir(game_path)
        if not config_dir:
            self._log("⚠ Run the game once before installing CHIM.", "red")
            self._log("")

        # ── Step 1: Backup ──
        self._log("Step 1: Backup...", "gold")
        self.root.after(0, lambda: self._install_status.config(text="Creating backup..."))
        self.root.after(0, lambda: self._install_progress.set_value(0.03))
        backup_path = backup_existing_mods(game_path)
        if backup_path:
            self._log(f"  → {backup_path.name}/", "green")
            if config_dir and config_dir.is_dir():
                cb = backup_path / "SavedConfig"
                cb.mkdir(parents=True, exist_ok=True)
                for f in config_dir.iterdir():
                    if f.is_file():
                        shutil.copy2(f, cb / f.name)
        else:
            self._log("  Clean install.", "dim")
        self._log("")

        # ── Step 2: Deploy frameworks from patches ──
        self._log("Step 2: Deploying frameworks...", "gold")
        self.root.after(0, lambda: self._install_status.config(text="Deploying OBSE + UE4SS..."))
        self.root.after(0, lambda: self._install_progress.set_value(0.06))

        for d in [data_dir, paks_dir, obse_dir, ue4ss_mods_dir]:
            d.mkdir(parents=True, exist_ok=True)

        # OBSE framework
        obse_fw = patches_base / "obse_framework"
        if obse_fw.is_dir():
            for f in obse_fw.iterdir():
                if f.is_file():
                    shutil.copy2(f, bin_dir / f.name)
            self._log(f"  ✔ OBSE framework", "green")

        # OBSE plugins (bundled known-working versions)
        obse_plugins_src = patches_base / "obse_plugins"
        if obse_plugins_src.is_dir():
            for f in obse_plugins_src.rglob("*"):
                if f.is_file():
                    rel = f.relative_to(obse_plugins_src)
                    dest = obse_dir / rel
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(f, dest)
            self._log(f"  ✔ OBSE plugins", "green")

        # PAK files (bundled tested versions — Nexus "latest" has breaking changes)
        paks_bundle = patches_base / "paks"
        if paks_bundle.is_dir():
            for f in paks_bundle.iterdir():
                if f.is_file():
                    shutil.copy2(f, paks_dir / f.name)
            pak_count = sum(1 for f in paks_bundle.iterdir() if f.is_file() and f.suffix.lower() == ".pak")
            self._log(f"  ✔ {pak_count} PAK files", "green")

        # UE4SS framework
        ue4ss_fw = patches_base / "ue4ss_framework"
        if ue4ss_fw.is_dir():
            for f in ue4ss_fw.iterdir():
                if not f.is_file():
                    continue
                if f.name.lower() == "winmm.dll":
                    shutil.copy2(f, bin_dir / f.name)
                else:
                    shutil.copy2(f, ue4ss_dir / f.name)
            self._log(f"  ✔ UE4SS framework", "green")

        # UE4SS shared/
        shared_src = patches_base / "ue4ss_shared"
        if shared_src.is_dir():
            shared_dest = ue4ss_mods_dir / "shared"
            shared_dest.mkdir(parents=True, exist_ok=True)
            for f in shared_src.rglob("*"):
                if f.is_file():
                    rel = f.relative_to(shared_src)
                    dest = shared_dest / rel
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(f, dest)
            self._log(f"  ✔ UE4SS shared libs", "green")

        # mods.txt
        mods_txt_name = "mods_deck.txt" if is_deck else "mods.txt"
        mods_txt_src = patches_base / mods_txt_name
        if mods_txt_src.is_file():
            shutil.copy2(mods_txt_src, ue4ss_mods_dir / "mods.txt")
        self._log("")

        # ── Step 3: Install mods from archives ──
        self._log("Step 3: Installing mods...", "gold")
        for idx, mod in enumerate(to_install):
            nid = mod["nexus_id"]
            archive = self.mod_files[nid]
            progress = 0.10 + (idx + 1) / total * 0.55

            self.root.after(0, lambda p=progress: self._install_progress.set_value(p))
            self.root.after(0, lambda m=mod, i=idx: self._install_status.config(
                text=f"[{i+1}/{total}]  {m['name']}"
            ))

            self._log(f"  [{idx+1}/{total}] {mod['name']}", "gold")

            if not archive or not archive.exists():
                self._log(f"    Missing archive", "red")
                errors_total.append(f"{mod['name']}: archive missing")
                continue

            tmp_dir = Path(tempfile.mkdtemp(prefix="chim_"))
            ok = extract_archive(archive, tmp_dir)
            if not ok:
                self._log(f"    Extract failed", "red")
                errors_total.append(f"{mod['name']}: extraction failed")
                shutil.rmtree(tmp_dir, ignore_errors=True)
                continue

            installed, errs = classify_and_install_files(tmp_dir, game_path, mod["type"], mod["name"])
            if installed > 0:
                self._log(f"    {installed} file(s) ✔", "green")
            if errs:
                for e in errs:
                    self._log(f"    {e}", "red")
                errors_total.extend(errs)

            shutil.rmtree(tmp_dir, ignore_errors=True)

        self._log("")

        # ── Step 4: Apply mod patches + cleanup ──
        self._log("Step 4: Patches + cleanup...", "gold")
        self.root.after(0, lambda: self._install_status.config(text="Applying patches..."))
        self.root.after(0, lambda: self._install_progress.set_value(0.70))

        try:
            # UE4SS mod patches (config overlays for EternalDarkness, LumenRemastered, etc.)
            ue4ss_patches = patches_base / "ue4ss_mods"
            if ue4ss_patches.is_dir():
                for mod_dir in ue4ss_patches.iterdir():
                    if not mod_dir.is_dir():
                        continue
                    dest_mod = ue4ss_mods_dir / mod_dir.name
                    if not dest_mod.is_dir():
                        continue
                    for f in mod_dir.rglob("*"):
                        if f.is_file():
                            rel = f.relative_to(mod_dir)
                            dest = dest_mod / rel
                            dest.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(f, dest)
                    self._log(f"  ✔ {mod_dir.name} patched", "green")

            # Cleanup: dwmapi.dll (some archives bundle it)
            dwmapi = bin_dir / "dwmapi.dll"
            if dwmapi.is_file():
                dwmapi.unlink()

            # Cleanup: BPML/BPModLoader real folders (built into UE4SS.dll)
            for fw in ("BPML_GenericFunctions", "BPModLoaderMod"):
                fw_dir = ue4ss_mods_dir / fw
                if fw_dir.is_dir():
                    shutil.rmtree(fw_dir)

            # Cleanup: shared/ extras from Nexus archives
            shared_dir = ue4ss_mods_dir / "shared"
            for extra in ("jsbProfiler", "Types.lua"):
                p = shared_dir / extra
                if p.is_dir():
                    shutil.rmtree(p)
                elif p.is_file():
                    p.unlink()

            # Cleanup: junk files
            for junk in ("obse64_readme.txt", "obse64_whatsnew.txt", "enchantmentdrain.log",
                         "UltraPlusConfig.ini", "UltraPlus_version.txt", "UltraPlusConfig.default",
                         "ShadersRevisedPreset.ini", "Readme_UE4SS.txt",
                         "obr-achievementunblocker.log"):
                p = bin_dir / junk
                if p.is_file():
                    p.unlink()
            for junk_dir in ("MadConfigs", "src", "D3D12"):
                p = bin_dir / junk_dir
                if p.is_dir():
                    shutil.rmtree(p)

            # NPCAppearanceManager: data mod, no enabled.txt
            npc_dir = ue4ss_mods_dir / "NPCAppearanceManager"
            if npc_dir.is_dir():
                npc_en = npc_dir / "enabled.txt"
                if npc_en.exists():
                    npc_en.unlink()

            # UltraPlus symlink (skip on Deck — UltraPlus is excluded)
            if not is_deck:
                up_ext = ue4ss_mods_dir / "UltraPlusExtensions"
                up_short = ue4ss_mods_dir / "UltraPlus"
                if up_ext.is_dir() and not up_short.exists():
                    import platform as _plat
                    if _plat.system() == "Windows":
                        shutil.copytree(up_ext, up_short, dirs_exist_ok=True)
                    else:
                        up_short.symlink_to("UltraPlusExtensions")
                    self._log(f"  ✔ UltraPlus symlink", "green")

            self._log(f"  ✔ Cleanup done", "green")
        except Exception as e:
            self._log(f"  Patch error: {e}", "red")
            import traceback
            self._log(f"  {traceback.format_exc()}", "red")

        self._log("")

        # ── Step 5: Deploy legacy ESPs + load order ──
        self._log("Step 5: Load order...", "gold")
        self.root.after(0, lambda: self._install_status.config(text="Generating load order..."))
        self.root.after(0, lambda: self._install_progress.set_value(0.80))

        # Deploy legacy ESPs (from mods that were in the original tested build)
        legacy_dir = patches_base / "legacy_esps"
        if legacy_dir.is_dir():
            leg_count = 0
            for f in legacy_dir.iterdir():
                if f.is_file():
                    shutil.copy2(f, data_dir / f.name)
                    leg_count += 1
            if leg_count:
                self._log(f"  ✔ {leg_count} legacy files deployed", "green")

        # Deploy bundled Plugins.txt (tested working format)
        plugins_src = patches_base / "Plugins.txt"
        if plugins_src.is_file():
            shutil.copy2(plugins_src, data_dir / "Plugins.txt")
            lines = [l.strip() for l in plugins_src.read_text().splitlines() if l.strip() and not l.startswith("#")]
            self._log(f"  ✔ {len(lines)} plugins in load order", "green")
        else:
            # Fallback to generated
            try:
                plugins_path, ordered = build_load_order(to_install, game_path)
                self._log(f"  ✔ {len(ordered)} plugins generated", "green")
            except Exception as e:
                self._log(f"  ✘ Failed: {e}", "red")
                errors_total.append(f"Load order: {e}")

        self._log("")

        # ── Step 6: Deploy config ──
        self._log("Step 6: Config...", "gold")
        self.root.after(0, lambda: self._install_status.config(text="Deploying config..."))
        self.root.after(0, lambda: self._install_progress.set_value(0.88))

        if is_deck:
            # Deck: deploy optimized configs (read-only so game can't overwrite)
            deck_dir = patches_base / "deck"
            if config_dir and deck_dir.is_dir():
                for ini_name, src_name in [("Engine.ini", "deck_engine.ini"), ("GameUserSettings.ini", "deck_gameusersettings.ini")]:
                    src = deck_dir / src_name
                    if not src.is_file():
                        src = self._find_bundled_file(src_name)  # fallback to project root
                    if src and src.is_file():
                        dest = config_dir / ini_name
                        if dest.exists():
                            bk = dest.with_suffix(".ini.backup_chim")
                            if not bk.exists():
                                shutil.copy2(dest, bk)
                        shutil.copy2(src, dest)
                        dest.chmod(0o444)
                        self._log(f"  ✔ {ini_name} (Deck, read-only)", "green")
        else:
            # PC: deploy Engine.ini (writable — game needs to write to it)
            engine_src = patches_base / "config" / "Engine.ini"
            if engine_src.is_file() and config_dir:
                dest = config_dir / "Engine.ini"
                if dest.exists():
                    bk = dest.with_suffix(".ini.pre_chim")
                    if not bk.exists():
                        shutil.copy2(dest, bk)
                shutil.copy2(engine_src, dest)
                dest.chmod(0o644)
                self._log(f"  ✔ Engine.ini (writable)", "green")
            elif not config_dir:
                self._log(f"  ⚠ Config dir not found", "red")

        self._log("")

        # ── Step 7: Launch options ──
        self._log("Step 7: Launch options...", "gold")
        self.root.after(0, lambda: self._install_status.config(text="Launch options..."))
        self.root.after(0, lambda: self._install_progress.set_value(0.95))

        config_path = find_steam_localconfig()
        if config_path:
            current = get_steam_launch_options(config_path, OBLIVION_APP_ID)
            import platform
            target_opts = LAUNCH_OPTIONS_WINDOWS if platform.system() == "Windows" else LAUNCH_OPTIONS_LINUX

            if current and "obse64_loader" in current:
                self._log(f"  Already set ✔", "green")
            else:
                def _copy_and_prompt():
                    dlg = tk.Toplevel(self.root)
                    dlg.title("Launch Options")
                    dlg.configure(bg=COLORS["bg"])
                    dlg.resizable(False, False)
                    dlg.transient(self.root)
                    dlg.grab_set()
                    dw, dh = 620, 340
                    x = self.root.winfo_x() + (self.root.winfo_width() - dw) // 2
                    y = self.root.winfo_y() + (self.root.winfo_height() - dh) // 2
                    dlg.geometry(f"{dw}x{dh}+{x}+{y}")
                    self._make_label(dlg, "One Last Step", size=18, color=COLORS["gold"], bold=True).pack(pady=(20, 8))
                    self._make_label(dlg, "Copy the launch options below and paste them in Steam:", size=10, color=COLORS["text_dim"]).pack(pady=(0, 8))
                    self._make_label(dlg, "Right-click game \u2192 Properties \u2192 Launch Options \u2192 Paste", size=10, color=COLORS["text"]).pack(pady=(0, 12))
                    text_frame = tk.Frame(dlg, bg=COLORS["border_gold"], padx=1, pady=1)
                    text_frame.pack(fill="x", padx=30, pady=(0, 12))
                    launch_text = tk.Text(text_frame, height=3, wrap="word", bg=COLORS["bg_light"], fg=COLORS["gold_bright"], font=("Consolas", 9), insertbackground=COLORS["gold"], selectbackground=COLORS["gold_dim"], selectforeground=COLORS["text_bright"], relief="flat", padx=8, pady=6)
                    launch_text.pack(fill="x")
                    launch_text.insert("1.0", target_opts)
                    launch_text.tag_add("sel", "1.0", "end")
                    launch_text.focus_set()
                    def _copy_to_clipboard():
                        self.root.clipboard_clear()
                        self.root.clipboard_append(target_opts)
                        self.root.update()
                        copy_btn.set_text("\u2714 Copied!")
                    btn_frame_dlg = tk.Frame(dlg, bg=COLORS["bg"])
                    btn_frame_dlg.pack(pady=(4, 0))
                    copy_btn = GoldButton(btn_frame_dlg, text="Copy to Clipboard", command=_copy_to_clipboard, width=170, height=38, font_size=10)
                    copy_btn.pack(side="left", padx=(0, 12))
                    def on_done():
                        dlg.destroy()
                        self._log(f"  Launch options shown ✔", "green")
                    GoldButton(btn_frame_dlg, text="Done", command=on_done, width=100, height=38, font_size=10).pack(side="left")
                self.root.after(0, _copy_and_prompt)

        self.root.after(0, lambda: self._install_progress.set_value(1.0))
        self._log("")
        if errors_total:
            self._log(f"Completed with {len(errors_total)} warning(s).", "gold")
        else:
            self._log("All mods installed successfully.", "green")
        self.root.after(0, lambda: self._install_status.config(text="Installation complete."))

        # Show Done button
        self.root.after(500, self._add_done_button)

    def _find_saved_config_dir(self, game_path: Path) -> Optional[Path]:
        """Find the saved config directory for Oblivion Remastered (Linux/Proton/Windows)."""
        import platform as _plat
        candidates = []

        if _plat.system() == "Windows":
            # Windows native: %LOCALAPPDATA%/OblivionRemastered/Saved/Config/Windows
            local = os.environ.get("LOCALAPPDATA", "")
            if local:
                candidates.append(Path(local) / "OblivionRemastered" / "Saved" / "Config" / "Windows")
            # Also check Documents path
            userprofile = os.environ.get("USERPROFILE", "")
            if userprofile:
                candidates.append(Path(userprofile) / "Documents" / "My Games" / "Oblivion Remastered" / "Saved" / "Config" / "Windows")
        else:
            # Linux / Steam Deck — Proton compatdata paths
            candidates = [
                Path.home() / ".local/share/Steam/steamapps/compatdata/2623190/pfx/drive_c/users/steamuser/Documents/My Games/Oblivion Remastered/Saved/Config/Windows",
                Path("/home/deck/.local/share/Steam/steamapps/compatdata/2623190/pfx/drive_c/users/steamuser/Documents/My Games/Oblivion Remastered/Saved/Config/Windows"),
                Path.home() / ".var/app/com.valvesoftware.Steam/.local/share/Steam/steamapps/compatdata/2623190/pfx/drive_c/users/steamuser/Documents/My Games/Oblivion Remastered/Saved/Config/Windows",
            ]

        for c in candidates:
            if c.is_dir():
                return c

        # Fallback: search compatdata (Linux only)
        if _plat.system() != "Windows":
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
        GoldButton(
            self._install_btn_frame, text="Continue  \u2192", command=self._show_done,
            width=140, height=40, font_size=11,
        ).pack(side="right")

    # ─── Done Screen ───────────────────────────────────────────────────────

    def _show_done(self):
        self._clear_container()

        frame = tk.Frame(self.container, bg=COLORS["bg"])
        frame.pack(expand=True)

        # Top ornament
        self._make_ornament_line(frame, 400).pack(pady=(0, 40))

        tk.Label(
            frame, text="C   H   I   M", bg=COLORS["bg"], fg=COLORS["gold"],
            font=("Cinzel", 42, "bold"),
        ).pack(pady=(0, 12))

        tk.Label(
            frame, text="has been installed.", bg=COLORS["bg"],
            fg="#e8e0d0", font=("Segoe UI", 16),
        ).pack(pady=(0, 30))

        # Center ornament
        self._make_ornament_line(frame, 300).pack(pady=(0, 30))

        # Status summary
        status_frame = tk.Frame(frame, bg=COLORS["bg"])
        status_frame.pack(pady=(0, 10))

        checks = [
            ("\u2714  Mods installed", COLORS["green"]),
            ("\u2714  Load order generated", COLORS["green"]),
            ("\u2714  Launch options copied to clipboard", COLORS["green"]),
        ]
        if self.profile == PROFILE_DECK:
            checks.append(("\u2714  Deck configs deployed", COLORS["green"]))

        for text, color in checks:
            tk.Label(status_frame, text=text, bg=COLORS["bg"], fg=color,
                     font=("Segoe UI", 11)).pack(anchor="w")

        # Deck-specific reminder (the one thing we can't auto-set)
        if self.profile == PROFILE_DECK:
            deck_frame = tk.Frame(frame, bg="#1a1408", padx=16, pady=12,
                                  highlightbackground=COLORS["gold"], highlightthickness=1)
            deck_frame.pack(fill="x", padx=40, pady=(20, 10))
            tk.Label(deck_frame, text="Quick Access Menu (\u2022\u2022\u2022 button):",
                     bg="#1a1408", fg=COLORS["gold"], font=("Segoe UI", 10, "bold")).pack(anchor="w")
            tk.Label(deck_frame,
                     text="30 FPS  |  40 Hz  |  Tearing Off  |  TDP 12-15W  |  GPU 1200 MHz",
                     bg="#1a1408", fg=COLORS["gold_bright"], font=("Segoe UI", 10)).pack(anchor="w", pady=(4, 0))

        # Ready message
        tk.Label(
            frame, text="Launch the game through Steam and go.",
            bg=COLORS["bg"], fg=COLORS["text_dim"], font=("Segoe UI", 10),
        ).pack(pady=(20, 30))

        # Buttons
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
