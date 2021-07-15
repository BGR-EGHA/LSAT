# LSAT

LSAT (Landslide Susceptibility Assessment Tools) is a software to prepare and evaluate landslide susceptibility models. LSAT is the result of a german chinese
cooperation. It was developed at the german Federal Institute for Geosciences and Natural Resources.
LSAT currently only runs on Windows. LSAT uses Python3 and PyQt5.

LSAT aims to be an easy to use Toolkit. Giving the user more time to focus on their research instead of the inner workings of the tools they use.

LSAT is released under the GPLv3 license.

## How to run LSAT

The easiest way to get LSAT is to download the most recent release [here](https://github.com/BGR-EGHA/LSAT).

### Running LSAT from source

The command line examples work with Windows. The syntax differs slightly for Linux users.

1. Make sure you have Python 3.7 installed, if not you can get it from python.org or your package manager (Linux).
2. Navigate to the LSAT directory and open a PowerShell (Windows) or Terminal (Linux) window there.
3. Create a virtual environment
```
python -m venv venv
```
4. Activate the virtual envirnment (venv should appear in the command line, indicating you were successfull)
Windows:
```
.\venv\Scripts\activate
```
5. Install the required packages
```
python -m pip install -r requirements.txt
```

	Additionally to the packages listed in the requirements.txt you will need GDAL (3.3.0 tested).
	Unfortunately, GDAL can usually not simply be installed with a pip command.
	You can either download a .whl file from [Christoph Gohlkes fantastic website](https://www.lfd.uci.edu/~gohlke/pythonlibs/) (Windows), 
	build it yourself (Windows/Linux) or get it with your package manager (Linux).
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
