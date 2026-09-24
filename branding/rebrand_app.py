#!/usr/bin/env python3
"""Rename the NutriTrack Android project to Himalo in one go.

Run it from the Android project's root folder (the one containing settings.gradle
or settings.gradle.kts):

    python3 path/to/rebrand_app.py            # preview only, changes nothing
    python3 path/to/rebrand_app.py --apply    # make the changes

It will:
  * set applicationId and namespace to app.himalo
  * move the Kotlin/Java sources from com/example to app/himalo and fix package/import lines
  * rename NutriTrackApplication to HimaloApplication
  * replace NutriTrack / Nutritrack / nutritrack text (app name, strings, updater asset name)
  * install the new launcher icons and the himalo_logo drawable

It does NOT touch app/google-services.json: download the new one from Firebase after
registering app.himalo (see docs/REBRAND.md) or the build will fail with
"No matching client found for package name 'app.himalo'".

Commit or back up your project first so you can undo.
"""
import os
import re
import shutil
import sys

OLD_APP_ID = "app.nutritrack"
NEW_APP_ID = "app.himalo"
OLD_PKG = "com.example"
NEW_PKG = "app.himalo"

TEXT_EXT = {".kt", ".kts", ".java", ".xml", ".gradle", ".pro", ".properties", ".json", ".md", ".txt", ".html"}
SKIP_DIRS = {".git", ".gradle", "build", ".idea", ".cxx", "node_modules"}
SKIP_FILES = {"google-services.json"}  # replaced by downloading the new one

BRANDING = os.path.dirname(os.path.abspath(__file__))
APPLY = "--apply" in sys.argv
changes = []


def log(msg):
    changes.append(msg)
    print(("" if APPLY else "[preview] ") + msg)


def text_files(root):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            if os.path.splitext(name)[1] in TEXT_EXT and name not in SKIP_FILES:
                yield os.path.join(dirpath, name)


def rewrite(text):
    # Order matters: specific identifiers before generic words.
    text = text.replace(OLD_APP_ID, NEW_APP_ID)
    text = re.sub(r"\bcom\.example(?=[.;\s\"'`)]|$)", NEW_PKG, text, flags=re.M)
    text = text.replace("NutriTrackApplication", "HimaloApplication")
    text = text.replace("nutritrack_logo", "himalo_logo")
    text = text.replace("NutriTrack", "Himalo").replace("Nutritrack", "Himalo").replace("NUTRITRACK", "HIMALO")
    # Keep the Firebase project id/hosts (they cannot be renamed) and the GitHub repo
    # URL (GitHub redirects old -> new after you rename the repo, not the reverse).
    text = re.sub(r"(?<!sasam17/)nutritrack(?!-2bf22)", "himalo", text)
    return text


def main():
    root = os.getcwd()
    if not any(os.path.exists(os.path.join(root, f)) for f in ("settings.gradle", "settings.gradle.kts")):
        sys.exit("Run this from the Android project root (the folder with settings.gradle).")

    # 1. Move source folders com/example -> app/himalo
    for dirpath, dirnames, _ in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        if dirpath.replace(os.sep, "/").endswith(("/java", "/kotlin")):
            old = os.path.join(dirpath, "com", "example")
            new = os.path.join(dirpath, "app", "himalo")
            if os.path.isdir(old):
                log(f"move {os.path.relpath(old)} -> {os.path.relpath(new)}")
                if APPLY:
                    os.makedirs(os.path.dirname(new), exist_ok=True)
                    shutil.move(old, new)
                    parent = os.path.dirname(old)
                    if not os.listdir(parent):
                        os.rmdir(parent)

    # 2. Rename files whose names contain the old brand
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            if name in SKIP_FILES:
                continue
            new_name = name.replace("NutriTrackApplication", "HimaloApplication").replace("nutritrack_logo", "himalo_logo")
            new_name = new_name.replace("NutriTrack", "Himalo")
            if new_name != name:
                log(f"rename {os.path.relpath(os.path.join(dirpath, name))} -> {new_name}")
                if APPLY:
                    os.rename(os.path.join(dirpath, name), os.path.join(dirpath, new_name))

    # 3. Rewrite file contents
    for path in text_files(root):
        if path.startswith(BRANDING):
            continue
        try:
            with open(path, encoding="utf-8") as f:
                old = f.read()
        except (UnicodeDecodeError, OSError):
            continue
        new = rewrite(old)
        if new != old:
            log(f"edit {os.path.relpath(path)}")
            if APPLY:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(new)

    # 4. Launcher icons + logo. Remove old ic_launcher* (png/webp/xml) first so the
    #    build doesn't fail on duplicate resources.
    res = os.path.join(root, "app", "src", "main", "res")
    src_res = os.path.join(BRANDING, "android", "res")
    if os.path.isdir(res):
        for d in os.listdir(res):
            full = os.path.join(res, d)
            if not os.path.isdir(full):
                continue
            for f in os.listdir(full):
                stem = os.path.splitext(f)[0]
                if (d.startswith("mipmap") and stem.startswith("ic_launcher")) or stem in ("nutritrack_logo", "himalo_logo"):
                    log(f"remove old {os.path.relpath(os.path.join(full, f))}")
                    if APPLY:
                        os.remove(os.path.join(full, f))
        for d in os.listdir(src_res):
            for f in os.listdir(os.path.join(src_res, d)):
                log(f"add {os.path.relpath(os.path.join(res, d, f))}")
                if APPLY:
                    os.makedirs(os.path.join(res, d), exist_ok=True)
                    shutil.copy2(os.path.join(src_res, d, f), os.path.join(res, d, f))
    else:
        print("app/src/main/res not found; copy branding/android/res in by hand.")

    print()
    if not APPLY:
        print(f"{len(changes)} changes previewed. Re-run with --apply to make them.")
    else:
        print(f"Done: {len(changes)} changes. Now replace app/google-services.json with the one for app.himalo, then build.")


if __name__ == "__main__":
    main()
