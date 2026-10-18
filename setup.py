from setuptools import setup, find_packages

setup(
    name="flyfly_oncology",
    version="1.0.0",
    description="TIMO-Cancer-Solver: Neuromorphic Connectome Attractor Discovery Engine for Oncology",
    author="Hussam Gad-Allah",
    author_email="12422023437409@pg.cu.edu.eg",
    packages=find_packages(),
    install_requires=[
        "torch>=2.0.0",
        "numpy>=1.24.0",
        "scipy>=1.10.0"
    ],
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12"
    ],
)
