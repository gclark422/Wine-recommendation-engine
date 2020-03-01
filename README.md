# Wine-recommendation-engine

A wine recommendation engine devloped by Grant Clark, Andrew Francis, Catherine McSorley, Yao Sun, and Urbain Nounagnon for Text Analytics at the Institute for Advanced Analyics.  

# Local Development
## Requirements
 - Python 3.7.3
 - Pip
 - Virtualenv (Optional but recommended) (any other virtual environment such as conda works too)
 
 ## Setup
- Create a virtual environment (optional) and clone the repo
```
$ virtualenv -p /usr/bin/python3.7 venv
$ source venv/bin/activate
```
--- OR ---
```
$ conda create -n env python=3.7.3 anaconda
$ source activate env
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
- Run file in terminal/any IDE you want
```
$ python main.py
```
- Open localhost:5000 in your favorite browser (127.0.0.1:5000)
- The site takes several seconds(up to a minute) to perform all the preprocessing so just let it load
haha