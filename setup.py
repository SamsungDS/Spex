from setuptools import setup, find_packages
import os

version = os.getenv("GITHUB_REF", "refs/tags/0.0.1").split("/")[-1]


def get_requirements():
    with open("./requirements.txt") as fp:
        return fp.read().split()


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
    package_data={
        "spex": ["py.typed"],
    },
)
