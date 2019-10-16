# Wine-recommendation-engine

A wine recommendation engine devloped by Grant Clark, Andrew Francis, and Catherine McSorley for Text Analytics at the Institute for Advanced Analyics.  

# Local Development
## Requirements
 - Python 3.7.3
 - Pip
 - Virtualenv (recommended) (or any other virtual environment such as conda)
 
 ## Setup
- Create a virtual environment and clone the repo
```
$ virtualenv -p /usr/bin/python3.6 venv
$ source venv/bin/activate
```
--- OR ---
```
$ conda create -n env python=3.7.3 anaconda
$ conda activate env
```
--- THEN ---
```
$ git clone https://github.com/gclark422/Wine-recommendation-engine.git
$ cd Wine-recommendation-engine
```
- Install requirements
```
$ pip install -r requirements.txt
```
- Run file in terminal
```
$ python main.py
```
- Open localhost:5000 in your favorite browser (127.0.0.1:5000)
