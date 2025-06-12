from setuptools import setup, find_packages

setup(
    name="ai_code_translator",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "google-generativeai>=0.3.0",
        "ttkbootstrap>=1.10.1",
        "pygments>=2.16.1"
    ],
    entry_points={
        'console_scripts': [
            'ai_code_translator=integrated_gui:main',
        ],
    },
)
