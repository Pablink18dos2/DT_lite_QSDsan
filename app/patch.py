"""Patch pkg_resources imports for Python 3.13 compatibility.

Python 3.13 removed pkg_resources from the standard library.
QSDsan 1.3.0 and EXPOsan 1.4.3 use it in their __init__.py files.
This script patches both files to use importlib.metadata as fallback.

Run once during Docker build: RUN python app/patch.py
Idempotent: safe to run multiple times.
"""

import site
import sys
from pathlib import Path


def find_init_file(package_name):
    """Find __init__.py for a package in site-packages."""
    for sp in site.getsitepackages():
        init_path = Path(sp) / package_name / '__init__.py'
        if init_path.exists():
            return init_path
    # Also check user site
    user_sp = site.getusersitepackages()
    if isinstance(user_sp, str):
        init_path = Path(user_sp) / package_name / '__init__.py'
        if init_path.exists():
            return init_path
    return None


def patch_file(init_path, package_name):
    """Apply the pkg_resources -> importlib.metadata fallback patch."""
    content = init_path.read_text(encoding='utf-8')

    # Already patched?
    if 'ModuleNotFoundError' in content:
        print(f'  [OK] {package_name} already patched: {init_path}')
        return False

    # Find and replace the pkg_resources import pattern
    old_pattern = f"import pkg_resources\n__version__ = pkg_resources.get_distribution('{package_name}').version"
    new_pattern = (
        f'try:\n'
        f'    import pkg_resources\n'
        f"    __version__ = pkg_resources.get_distribution('{package_name}').version\n"
        f'except (ModuleNotFoundError, Exception):\n'
        f'    from importlib.metadata import version\n'
        f"    __version__ = version('{package_name}')"
    )

    if old_pattern in content:
        content = content.replace(old_pattern, new_pattern)
        init_path.write_text(content, encoding='utf-8')
        print(f'  [OK] Patched {package_name}: {init_path}')
        return True

    # Try a more flexible match (different quoting or spacing)
    import re

    pattern = re.compile(
        r'import pkg_resources\s*\n\s*__version__\s*=\s*pkg_resources\.get_distribution\([\'"]'
        + re.escape(package_name)
        + r'[\'"]\)\.version'
    )
    if pattern.search(content):
        content = pattern.sub(new_pattern, content)
        init_path.write_text(content, encoding='utf-8')
        print(f'  [OK] Patched {package_name} (flexible match): {init_path}')
        return True

    print(f'  [WARN] Could not find pkg_resources pattern in {package_name}')
    return False


def main():
    print('BSM1 Simulator - pkg_resources patch for Python 3.13')
    print(f'Python version: {sys.version}')

    for pkg in ['qsdsan', 'exposan']:
        init_path = find_init_file(pkg)
        if init_path is None:
            print(f'  [ERROR] {pkg}/__init__.py not found in site-packages')
            continue
        patch_file(init_path, pkg)

    print('Patch complete.')


if __name__ == '__main__':
    main()
