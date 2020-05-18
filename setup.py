import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="osu-cplayer", # Replace with your own username
    version="0.0.2",
    author="Eshan Ramesh",
    author_email="esrh@netc.eu",
    description="fast and featured command line osu! song player built on mpv",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/eshrh/osu-cplayer",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=['python-mpv','tinytag','urwid'],
    entry_points = {'console_scripts':['osu-cplayer=osu_cplayer.osu_cplayer:main']}
)
