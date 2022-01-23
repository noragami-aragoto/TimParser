import os

def update():
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    os.system(f'cd  {ROOT_DIR}')
    os.system(f'git status')
    os.system('git pull origin master')