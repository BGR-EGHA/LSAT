# LSAT


[![DOI](https://zenodo.org/badge/386274608.svg)](https://zenodo.org/badge/latestdoi/386274608)

LSAT PM (Landslide Susceptibility Assessment Tools Project Manager Suite) was primarily developed to conduct landslide susceptibility analyses, it is not limited to this issue and applies to any other research dealing with supervised spatial binary classification.
We tested LSAT on Windows and Linux (Ubuntu 20.04). LSAT uses Python3 and great packages like PyQt5, sklearn and GDAL.

LSAT aims to be an easy to use Toolkit. Giving the user more time to focus on their research instead of the inner workings of the tools they use.

## How to run LSAT

The easiest way to run LSAT on Windows is to download the most recent installer [here](https://github.com/BGR-EGHA/LSAT/releases).

### Running LSAT from source on Windows

1. Make sure you have Python 3 installed (3.7 tested), if not you can get it from [python.org/downloads](https://www.python.org/downloads/).
2. Download LSAT
3. Navigate to the LSAT directory and open a PowerShell window (if you downloaded a zipped version you will need to unzip LSAT first).
4. Create a virtual environment
```
python -m venv venv
```
5. Activate the virtual environment (venv should appear in the command line, indicating you were successful)
```
.\venv\Scripts\activate
```
6. Install the required packages
```
python -m pip install -r requirements.txt
```

Additionally to the packages listed in the requirements.txt you will need GDAL (3.3.1 tested).
Unfortunately, GDAL can usually not simply be installed with a pip command.
You can either download a .whl file from [Christoph Gohlkes fantastic website](https://www.lfd.uci.edu/~gohlke/pythonlibs/#gdal) or
build it yourself.
Installing a .whl file:

```
python -m pip install *path to .whl file*
```

7. Start LSAT PM
```
python startMenu_main.py
```

After the initial setup you just need to open the powershell window, activate the venv and start
LSAT PM to run it.

### Running LSAT from source on Linux (Ubuntu 20.04.3 tested)

1. Download LSAT
2. Navigate to the LSAT directory and open a Terminal (if you downloaded a zipped version you will need to extract LSAT first).
3. Install Python packages (venv, pip, python development tools), gdal and libraries for Qt
```
sudo apt install python3-venv python3-pip gdal-bin libgdal-dev python3-dev '^libxcb.*-dev'
```

4. Create a virtual environment
```
python3 -m venv venv
```

5. Activate the virtual environment (venv should appear in the command line, indicating you were successful)
```
source venv/bin/activate
```

6. Install the required packages
```
python3 -m pip install -r requirements.txt
```
Additionally to the packages listed in the requirements.txt you will need GDAL (3.0.4 tested).
Unfortunately, GDAL can usually not simply be installed with the standard pip command.
You need to specify the version based on the gdal version installed.
To get the installed version run
```
ogrinfo --version
```
It will output something like: "GDAL $VERSION, released $RELEASEDATE". Now install that version
```
python3 -m pip install gdal==$VERSION
```

7. Start LSAT PM
```
python3 startMenu_main.py
```

After the initial setup you just need to open a terminal, activate the venv and start
LSAT PM to run it.

## Documentation

All windows installers come with documentation.
Alternatively you can find the current documentation and documentation for older releases (see releases) [here](https://github.com/BGR-EGHA/LSAT-Documentation).

## Test dataset

We offer a test dataset to try out LSAT [here](https://github.com/BGR-EGHA/LSAT-TestData).

## License

Distributed under the GPLv3 License, see LICENSE.txt.

## Feedback

Bug reports are welcome! Please use GitHub issues to report bugs.
