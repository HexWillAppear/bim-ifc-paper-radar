from setuptools import find_packages, setup


setup(
    name="bim-ifc-paper-radar",
    version="0.1.0",
    description="Daily BIM and IFC paper collector for GitHub Pages.",
    package_dir={"": "src"},
    packages=find_packages("src"),
    python_requires=">=3.10",
    install_requires=[],
    entry_points={"console_scripts": ["paper-radar=paper_radar.collect:main"]},
)
