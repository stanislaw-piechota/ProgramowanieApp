from requests import get
from json import loads
import difflib
import os

file = loads(get('http://najlepszawgalaktyce.000webhostapp.com/api/',params={'auth':'07072005','update':'py'}).text)['update']
fileUrl = 'http://najlepszawgalaktyce.000webhostapp.com/api/main.zip'

def update():
    with open('main.py') as f:
        for i,s in enumerate(difflib.ndiff(f.read(), file)):
            if s[0]==' ':
                continue
            else:
                if s[-1]!='\r':
                    print(print(s[-1]))
                    return True
    return False

def updater(path):
    os.system(f'powershell Invoke-WebRequest {fileUrl} -OutFile {path}/main.zip')
    os.system(f'powershell Expand-Archive {path}/main.zip .')
    os.system('del main.zip')

if __name__ == '__main__':
    print(update())
