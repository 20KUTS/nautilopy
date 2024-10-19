import argparse
import importlib
import subprocess
import sys
from typing import Dict, List
import re

def f_install_package(s_package_name: str, s_package_manager: str = "conda") -> bool:
    """
    Install a Python package using conda, mamba, or pip, and verify its installation.

    This function attempts to install the specified package using the preferred package manager.
    If that fails, it falls back to pip. It handles packages with different install and import names.

    Args:
        s_package_name (str): Name of the package to install.
        s_package_manager (str): Package manager to use ('conda' or 'mamba'). Defaults to 'conda'.

    Returns:
        bool: True if the installation was successful, False otherwise.

    Raises:
        ValueError: If an invalid package manager is specified.

    Notes:
        - The function first checks if the package is already installed.
        - It uses a mapping dictionary to handle packages with different install and import names.
        - The installation process is silent (no output) to reduce clutter.
        - If conda/mamba fails, it automatically falls back to pip.

    Examples:
        >>> b_success = f_install_package("numpy")
        NumPy is already installed.
        >>> print(b_success)
        True

        >>> b_success = f_install_package("non_existent_package")
        non_existent_package not found. Installing using conda...
        Failed to install non_existent_package using conda. Attempting to install with pip...
        Failed to install non_existent_package with pip as well.
        >>> print(b_success)
        False

    References:
        - Conda documentation: https://docs.conda.io/projects/conda/en/latest/
        - Pip documentation: https://pip.pypa.io/en/stable/
        - Importlib documentation: https://docs.python.org/3/library/importlib.html
    """
    # Dictionary mapping package names to their import names and display names
    C_PACKAGE_MAPPING: Dict[str, Dict[str, str]] = {
        'pillow': {'import': 'PIL', 'name': 'Pillow'},
        'beautifulsoup4': {'import': 'bs4', 'name': 'Beautiful Soup'},
        'python-docx': {'import': 'docx', 'name': 'python-docx'},
        'pyyaml': {'import': 'yaml', 'name': 'PyYAML'},
        'python-magic': {'import': 'magic', 'name': 'python-magic'},
        'scikit-learn': {'import': 'sklearn', 'name': 'scikit-learn'},
        'opencv-python': {'import': 'cv2', 'name': 'OpenCV'},
        'matplotlib': {'import': 'matplotlib.pyplot', 'name': 'Matplotlib'},
        'tensorflow': {'import': 'tensorflow', 'name': 'TensorFlow'},
        'torch': {'import': 'torch', 'name': 'PyTorch'},
        'nltk': {'import': 'nltk', 'name': 'NLTK'},
        'scipy': {'import': 'scipy', 'name': 'SciPy'},
        'numpy': {'import': 'numpy', 'name': 'NumPy'},
        'pandas': {'import': 'pandas', 'name': 'Pandas'},
        'seaborn': {'import': 'seaborn', 'name': 'Seaborn'},
        'requests': {'import': 'requests', 'name': 'Requests'},
        'flask': {'import': 'flask', 'name': 'Flask'},
        'django': {'import': 'django', 'name': 'Django'},
        'sqlalchemy': {'import': 'sqlalchemy', 'name': 'SQLAlchemy'},
        'pytest': {'import': 'pytest', 'name': 'pytest'},
        'ipython': {'import': 'IPython', 'name': 'IPython'}
    }
    
    # Get package info from the mapping, or use default values if not in the mapping
    dic_package_info: Dict[str, str] = C_PACKAGE_MAPPING.get(s_package_name.lower(), {'import': s_package_name, 'name': s_package_name})
    s_import_name: str = dic_package_info['import']
    s_display_name: str = dic_package_info['name']

    def f_import_package() -> bool:
        """Attempt to import the package and return success status."""
        try:
            importlib.import_module(s_import_name.split('.')[0])
            return True
        except ImportError:
            return False

    # Check if the package is already installed
    if f_import_package():
        print(f"{s_display_name} is already installed.")
        return True

    print(f"{s_display_name} not found. Installing using {s_package_manager}...")
    
    # Validate the package manager
    if s_package_manager not in ['conda', 'mamba']:
        raise ValueError("Package manager must be 'conda' or 'mamba'")
    
    def f_install_with_manager(s_manager: str) -> bool:
        """Attempt to install the package with the specified package manager."""
        try:
            # Run the installation command silently
            subprocess.check_call([s_manager, "install", "-y", s_package_name], 
                                  stdout=subprocess.DEVNULL, 
                                  stderr=subprocess.DEVNULL)
            return f_import_package()
        except subprocess.CalledProcessError:
            return False

    def f_install_with_pip() -> bool:
        """Attempt to install the package with pip."""
        try:
            # Run pip installation command silently
            subprocess.check_call([sys.executable, "-m", "pip", "install", s_package_name], 
                                  stdout=subprocess.DEVNULL, 
                                  stderr=subprocess.DEVNULL)
            return f_import_package()
        except subprocess.CalledProcessError:
            return False

    # Attempt installation with the specified package manager
    if f_install_with_manager(s_package_manager):
        print(f"{s_display_name} successfully installed with {s_package_manager}.")
        return True
    
    # If conda/mamba fails, try pip
    print(f"Failed to install {s_display_name} using {s_package_manager}. Attempting to install with pip...")
    if f_install_with_pip():
        print(f"{s_display_name} successfully installed with pip.")
        return True
    
    # If all installation attempts fail
    print(f"Failed to install {s_display_name} with pip as well.")
    return False





def f_parse_requirements(s_file_path: str) -> List[str]:
    """
    Parse the requirements.txt file and extract only package names.

    Args:
        s_file_path (str): Path to the requirements.txt file.

    Returns:
        List[str]: List of package names without version specifications.
    """
    l_packages = []
    with open(s_file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line and not line.startswith('#'):
                # Extract package name, ignoring version specifiers
                match = re.match(r'^([a-zA-Z0-9_.-]+)', line)
                if match:
                    l_packages.append(match.group(1))
    return l_packages

def f_install_from_requirements(s_file_path: str, s_package_manager: str = "conda") -> None:
    """
    Install packages from a requirements.txt file.

    Args:
        s_file_path (str): Path to the requirements.txt file.
        s_package_manager (str): Package manager to use ('conda' or 'mamba'). Defaults to 'conda'.
    """
    l_packages = f_parse_requirements(s_file_path)

    for s_package in l_packages:
        f_install_package(s_package, s_package_manager)

def main():
    parser = argparse.ArgumentParser(description="Install Python packages from requirements.txt")
    parser.add_argument("file", help="Path to the requirements.txt file")
    parser.add_argument("--manager", choices=["conda", "mamba"], default="conda",
                        help="Package manager to use (default: conda)")
    args = parser.parse_args()

    f_install_from_requirements(args.file, args.manager)

if __name__ == "__main__":
    main()