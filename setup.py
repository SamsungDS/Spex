from setuptools import setup, find_packages
from pathlib import Path
import os

PKG_ROOT = Path(__file__).parent


def get_requirements():
    with open(PKG_ROOT / "requirements.txt") as fp:
        res =  fp.read().split()
        return res


version = os.getenv("GITHUB_REF", "refs/tags/0.0.1").split("/")[-1]

setup(
    name="spex",
    description="extract data structures from docx/HTML specification",
    classifiers=[],
    version=version,
    author="Jesper Wendel Devantier",
    author_email="j.devantier@samsung.com",
    # url=""  # TODO: to be determined.
    packages=find_packages(exclude=["tests"]),
    install_requires=get_requirements(),
    entry_points={"console_scripts": ["spex = spex.__main__:main"]},
    license="MIT",
    options={"bdist_wheel": {"universal": True}},
    package_data={"spex": ["py.typed"]},
)