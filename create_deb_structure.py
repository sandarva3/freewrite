#!/usr/bin/env python3

import os
import shutil
from pathlib import Path
import stat

def create_directory(path):
    """Create directory if it doesn't exist"""
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"Created directory: {path}")

def create_file(path, content):
    """Create file with specified content"""
    with open(path, 'w') as f:
        f.write(content)
    print(f"Created file: {path}")

def make_executable(path):
    """Make file executable"""
    current = os.stat(path)
    os.chmod(path, current.st_mode | stat.S_IEXEC)
    print(f"Made executable: {path}")

def main():
    # Root directory for package creation
    root_dir = Path("freewrite-package")
    create_directory(root_dir)
    
    # Create debian directory and files
    debian_dir = root_dir / "debian"
    create_directory(debian_dir)
    
    # control file
    control_content = """Source: freewrite
Section: editors
Priority: optional
Maintainer: Your Name <your.email@example.com>
Build-Depends: debhelper (>= 9), python3, dh-python
Standards-Version: 4.5.0
Homepage: https://your-website.com/freewrite

Package: freewrite
Architecture: all
Depends: ${python3:Depends}, ${misc:Depends}, python3-pyqt5
Description: Distraction-free writing application
 Freewrite is a minimalist application designed to help writers
 focus on their content with a distraction-free environment.
 It provides a clean interface for writing without the clutter
 of complex formatting options.
"""
    create_file(debian_dir / "control", control_content)
    
    # changelog file
    changelog_content = """freewrite (1.0.0) unstable; urgency=medium

  * Initial release.

 -- Your Name <your.email@example.com>  Mon, 19 May 2025 12:00:00 +0000
"""
    create_file(debian_dir / "changelog", changelog_content)
    
    # compat file
    create_file(debian_dir / "compat", "9\n")
    
    # copyright file
    copyright_content = """Format: https://www.debian.org/doc/packaging-manuals/copyright-format/1.0/
Upstream-Name: freewrite
Source: https://your-website.com/freewrite

# In debian/copyright
Files: *
Copyright: 2025, Farza, www.twitter.com/farzatv 
           2025, Sandarva www.twitter.com/sandarvapaudel3
License: [ORIGINAL LICENSE]
Comment: Linux port of the original macOS application

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.
 .
 This package is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.
 .
 You should have received a copy of the GNU General Public License
 along with this program. If not, see <https://www.gnu.org/licenses/>.
 .
 On Debian systems, the complete text of the GNU General
 Public License version 3 can be found in "/usr/share/common-licenses/GPL-3".
"""
    create_file(debian_dir / "copyright", copyright_content)
    
    # rules file
    rules_content = """#!/usr/bin/make -f
%:
	dh $@ --with python3
"""
    create_file(debian_dir / "rules", rules_content)
    make_executable(debian_dir / "rules")
    
    # install file
    install_content = """usr/bin/freewrite usr/bin/
usr/share/applications/freewrite.desktop usr/share/applications/
usr/share/freewrite/* usr/share/freewrite/
usr/share/icons/hicolor/*/apps/freewrite.png usr/share/icons/hicolor/*/apps/
"""
    create_file(debian_dir / "install", install_content)
    
    # desktop file
    desktop_content = """[Desktop Entry]
Name=Freewrite
Comment=Distraction-free writing application
Exec=freewrite
Icon=freewrite
Terminal=false
Type=Application
Categories=Office;WordProcessor;
Keywords=Text;Editor;Write;
"""
    create_file(debian_dir / "freewrite.desktop", desktop_content)
    
    # Create usr structure
    usr_bin = root_dir / "usr" / "bin"
    create_directory(usr_bin)
    
    # Create launcher script
    launcher_content = """#!/bin/sh
python3 /usr/share/freewrite/main.py "$@"
"""
    create_file(usr_bin / "freewrite", launcher_content)
    make_executable(usr_bin / "freewrite")
    
    # Create applications directory
    apps_dir = root_dir / "usr" / "share" / "applications"
    create_directory(apps_dir)
    create_file(apps_dir / "freewrite.desktop", desktop_content)
    
    # Create program directory
    prog_dir = root_dir / "usr" / "share" / "freewrite"
    create_directory(prog_dir)
    create_directory(prog_dir / "assets")
    create_directory(prog_dir / "fonts")
    create_directory(prog_dir / "app_icons")
    
    # Create icons directory structure
    for size in ["16x16", "32x32", "64x64", "128x128", "256x256", "512x512"]:
        icon_dir = root_dir / "usr" / "share" / "icons" / "hicolor" / size / "apps"
        create_directory(icon_dir)
    
    # Create setup.py
    setup_content = """#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(
    name="freewrite",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "PyQt5",
    ],
    entry_points={
        'console_scripts': [
            'freewrite=freewrite.main:main',
        ],
    },
    package_data={
        'freewrite': [
            'assets/*',
            'fonts/*',
            'app_icons/*',
        ],
    },
)
"""
    create_file(root_dir / "setup.py", setup_content)
    
    print("\nPackage structure created successfully!")
    print(f"Next steps:")
    print(f"1. Copy your Python files to {prog_dir}")
    print(f"2. Copy your icons to the respective icon directories")
    print(f"3. Navigate to {root_dir}")
    print(f"4. Run: dpkg-buildpackage -us -uc -b")
    print(f"5. Install with: sudo dpkg -i ../freewrite_1.0.0_all.deb")

if __name__ == "__main__":
    main()#!/usr/bin/env python3

import os
import shutil
from pathlib import Path
import stat

def create_directory(path):
    """Create directory if it doesn't exist"""
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"Created directory: {path}")

def create_file(path, content):
    """Create file with specified content"""
    with open(path, 'w') as f:
        f.write(content)
    print(f"Created file: {path}")

def make_executable(path):
    """Make file executable"""
    current = os.stat(path)
    os.chmod(path, current.st_mode | stat.S_IEXEC)
    print(f"Made executable: {path}")

def main():
    # Root directory for package creation
    root_dir = Path("freewrite-package")
    create_directory(root_dir)
    
    # Create debian directory and files
    debian_dir = root_dir / "debian"
    create_directory(debian_dir)
    
    # control file
    control_content = """Source: freewrite
Section: editors
Priority: optional
Maintainer: Sandarva Paudel, sandarvapoudel182@gmail.com 
Build-Depends: debhelper (>= 9), python3, dh-python
Standards-Version: 4.5.0
Homepage: https://your-website.com/freewrite

Package: freewrite
Architecture: all
Depends: ${python3:Depends}, ${misc:Depends}, python3-pyqt5
Description: Distraction-free writing application
 Freewrite is a minimalist application designed to help writers
 focus on their content with a distraction-free environment.
 It provides a clean interface for writing without the clutter
 of complex formatting options.
"""
    create_file(debian_dir / "control", control_content)
    
    # changelog file
    changelog_content = """freewrite (1.0.0) unstable; urgency=medium

  * Initial release.

 -- Your Name <your.email@example.com>  Mon, 19 May 2025 12:00:00 +0000
"""
    create_file(debian_dir / "changelog", changelog_content)
    
    # compat file
    create_file(debian_dir / "compat", "9\n")
    
    # copyright file
    copyright_content = """Format: https://www.debian.org/doc/packaging-manuals/copyright-format/1.0/
Upstream-Name: freewrite
Source: https://your-website.com/freewrite

Files: *
Copyright: 2025 Your Name <your.email@example.com>
License: GPL-3.0+
 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.
 .
 This package is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.
 .
 You should have received a copy of the GNU General Public License
 along with this program. If not, see <https://www.gnu.org/licenses/>.
 .
 On Debian systems, the complete text of the GNU General
 Public License version 3 can be found in "/usr/share/common-licenses/GPL-3".
"""
    create_file(debian_dir / "copyright", copyright_content)
    
    # rules file
    rules_content = """#!/usr/bin/make -f
%:
	dh $@ --with python3
"""
    create_file(debian_dir / "rules", rules_content)
    make_executable(debian_dir / "rules")
    
    # install file
    install_content = """usr/bin/freewrite usr/bin/
usr/share/applications/freewrite.desktop usr/share/applications/
usr/share/freewrite/* usr/share/freewrite/
usr/share/icons/hicolor/*/apps/freewrite.png usr/share/icons/hicolor/*/apps/
"""
    create_file(debian_dir / "install", install_content)
    
    # desktop file
    desktop_content = """[Desktop Entry]
Name=Freewrite
Comment=Distraction-free writing application
Exec=freewrite
Icon=freewrite
Terminal=false
Type=Application
Categories=Office;WordProcessor;
Keywords=Text;Editor;Write;
"""
    create_file(debian_dir / "freewrite.desktop", desktop_content)
    
    # Create usr structure
    usr_bin = root_dir / "usr" / "bin"
    create_directory(usr_bin)
    
    # Create launcher script
    launcher_content = """#!/bin/sh
python3 /usr/share/freewrite/main.py "$@"
"""
    create_file(usr_bin / "freewrite", launcher_content)
    make_executable(usr_bin / "freewrite")
    
    # Create applications directory
    apps_dir = root_dir / "usr" / "share" / "applications"
    create_directory(apps_dir)
    create_file(apps_dir / "freewrite.desktop", desktop_content)
    
    # Create program directory
    prog_dir = root_dir / "usr" / "share" / "freewrite"
    create_directory(prog_dir)
    create_directory(prog_dir / "assets")
    create_directory(prog_dir / "fonts")
    create_directory(prog_dir / "app_icons")
    
    # Create icons directory structure
    for size in ["16x16", "32x32", "64x64", "128x128", "256x256", "512x512"]:
        icon_dir = root_dir / "usr" / "share" / "icons" / "hicolor" / size / "apps"
        create_directory(icon_dir)
    
    # Create setup.py
    setup_content = """#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(
    name="freewrite",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "PyQt5",
    ],
    entry_points={
        'console_scripts': [
            'freewrite=freewrite.main:main',
        ],
    },
    package_data={
        'freewrite': [
            'assets/*',
            'fonts/*',
            'app_icons/*',
        ],
    },
)
"""
    create_file(root_dir / "setup.py", setup_content)
    
    print("\nPackage structure created successfully!")
    print(f"Next steps:")
    print(f"1. Copy your Python files to {prog_dir}")
    print(f"2. Copy your icons to the respective icon directories")
    print(f"3. Navigate to {root_dir}")
    print(f"4. Run: dpkg-buildpackage -us -uc -b")
    print(f"5. Install with: sudo dpkg -i ../freewrite_1.0.0_all.deb")

if __name__ == "__main__":
    main()
