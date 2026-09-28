# -*- coding: utf-8 -*-
"""Packaging and deployment utility for SwineSpatialPlanner QGIS Plugin.

Usage:
    # 1. Generate release ZIP package (in dist/ folder):
    python package_plugin.py

    # 2. Deploy directly to current user's local QGIS plugin folder:
    python package_plugin.py --install
"""

import os
import sys
import shutil
import zipfile
import argparse
from pathlib import Path

PLUGIN_FOLDER_NAME = "suino_alpha"
PACKAGE_DISPLAY_NAME = "SwineSpatialPlanner"

INCLUDE_FILES = [
    "__init__.py",
    "suino_alpha.py",
    "suino_alpha_dialog.py",
    "suino_alpha_dialog_base.ui",
    "metadata.txt",
    "icon.png",
    "resources.py",
    "resources.qrc",
    "README.md",
]

INCLUDE_DIRS = [
    "core",
    "gis",
    "ui",
    "resources",
]

EXCLUDE_PATTERNS = [
    "__pycache__",
    ".pytest_cache",
    "*.pyc",
    "*.pyo",
    ".git*",
    "tests",
]


def should_exclude(path_obj: Path) -> bool:
    """Check if file or directory should be excluded from package."""
    for part in path_obj.parts:
        if part in ("__pycache__", ".pytest_cache", ".git"):
            return True
    if path_obj.suffix in (".pyc", ".pyo"):
        return True
    return False


def get_qgis_plugins_dir() -> Path:
    """Detect QGIS 3 user profile plugins directory according to OS."""
    if sys.platform == "win32":
        appdata = os.environ.get("APPDATA", "")
        return Path(appdata) / "QGIS" / "QGIS3" / "profiles" / "default" / "python" / "plugins"
    elif sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "QGIS" / "QGIS3" / "profiles" / "default" / "python" / "plugins"
    else:
        return Path.home() / ".local" / "share" / "QGIS" / "QGIS3" / "profiles" / "default" / "python" / "plugins"


def build_zip(source_dir: Path, output_zip: Path):
    """Bundle clean plugin structure into an installable ZIP for QGIS."""
    output_zip.parent.mkdir(parents=True, exist_ok=True)
    if output_zip.exists():
        output_zip.unlink()

    print(f"[*] Criando pacote ZIP instalavel: {output_zip}")
    count = 0

    with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        # Add root files
        for filename in INCLUDE_FILES:
            src = source_dir / filename
            if src.exists():
                arcname = f"{PLUGIN_FOLDER_NAME}/{filename}"
                zf.write(src, arcname)
                count += 1
            else:
                print(f"[!] Aviso: Arquivo opcional '{filename}' nao encontrado.")

        # Add directories
        for dirname in INCLUDE_DIRS:
            dirpath = source_dir / dirname
            if dirpath.exists() and dirpath.is_dir():
                for file_path in dirpath.rglob("*"):
                    if file_path.is_file() and not should_exclude(file_path):
                        rel_path = file_path.relative_to(source_dir)
                        arcname = f"{PLUGIN_FOLDER_NAME}/{rel_path.as_posix()}"
                        zf.write(file_path, arcname)
                        count += 1

    print(f"[OK] Pacote gerado com sucesso! ({count} arquivos incluidos)")
    print(f"[+] Localizacao: {output_zip.resolve()}")
    print("[+] Para instalar: No QGIS va em 'Complementos' -> 'Gerenciar e Instalar Complementos' -> 'Instalar a partir do ZIP'.\n")


def install_local(source_dir: Path):
    """Deploy files directly into local QGIS user plugins directory."""
    dest_dir = get_qgis_plugins_dir() / PLUGIN_FOLDER_NAME
    print(f"[*] Instalando diretamente no QGIS em:")
    print(f"    {dest_dir}")

    if dest_dir.exists():
        print("    Limpando versao antiga instalada...")
        shutil.rmtree(dest_dir)

    dest_dir.mkdir(parents=True, exist_ok=True)

    # Copy files
    for filename in INCLUDE_FILES:
        src = source_dir / filename
        if src.exists():
            shutil.copy2(src, dest_dir / filename)

    # Copy subdirectories
    for dirname in INCLUDE_DIRS:
        src_dir = source_dir / dirname
        dst_subdir = dest_dir / dirname
        if src_dir.exists():
            shutil.copytree(
                src_dir,
                dst_subdir,
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc")
            )

    print("[OK] Plugin instalado com sucesso no seu QGIS!")
    print("[+] Se o QGIS ja estiver aberto, reinicie-o para carregar a nova versao.")


def main():
    parser = argparse.ArgumentParser(description="Empacotador e Instalador do SwineSpatialPlanner")
    parser.add_argument(
        "--install",
        action="store_true",
        help="Instala diretamente na pasta de plugins do QGIS local"
    )
    args = parser.parse_args()

    source_dir = Path(__file__).parent.resolve()
    dist_dir = source_dir / "dist"
    output_zip = dist_dir / f"{PACKAGE_DISPLAY_NAME}.zip"

    # Always build the zip
    build_zip(source_dir, output_zip)

    # If --install is specified, also deploy locally
    if args.install:
        install_local(source_dir)


if __name__ == "__main__":
    main()
