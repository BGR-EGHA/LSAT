# LSAT

LSAT PMS (Landslide Susceptibility Assessment Tools Project Manager Suite) was primarily developed to conduct landslide susceptibility analyses, it is not limited to this issue and applies to any other research dealing with supervised spatial binary classification.
LSAT was tested on Windows and Linux (Ubuntu 20.04). LSAT uses Python3 and PyQt5.

LSAT aims to be an easy to use Toolkit. Giving the user more time to focus on their research instead of the inner workings of the tools they use.

LSAT is released under the GPLv3 license.

## How to run LSAT

The easiest way to get LSAT is to download the most recent release [here](https://github.com/BGR-EGHA/LSAT/releases).

### Running LSAT from source on Windows with Powershell

1. Make sure you have Python 3.7 installed, if not you can get it from python.org.
2. Download LSAT
3. Navigate to the LSAT directory and open a PowerShell window there.
4. Create a virtual environment
```
python -m venv venv
```
5. Activate the virtual envirnment (venv should appear in the command line, indicating you were successfull)
```
.\venv\Scripts\activate
```
5. Install the required packages
```
python -m pip install -r requirements.txt
```

Additionally to the packages listed in the requirements.txt you will need GDAL (3.3.0 tested).
Unfortunately, GDAL can usually not simply be installed with a pip command.
You can either download a .whl file from [Christoph Gohlkes fantastic website](https://www.lfd.uci.edu/~gohlke/pythonlibs/), 
build it yourself.
Installing a .whl:

```
python -m pip install *path to .whl file*
```

6. Start LSAT PMS
```
python startMenu_main.py
```

## Feedback

Bug reports are welcome! Please use GitHub issues to report bugs.
