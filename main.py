import json
import os
import shutil
import threading
import time
try:
    from requests import get
except:
    os.system('pip install requests')
    from requests import get
from subprocess import Popen, PIPE
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from tkinter.ttk import Progressbar, Scrollbar

def cl(c):
    global actsList
    actsList.itemconfig(END,fg=c)

def write_file(data):
    with open('data.json', 'w') as f:
        f.write(json.dumps(data))

def saveSet(*args):
    global path, passEntry, loginEntry,pathButton, data, errSetLabel, root,repoEntry
    login = loginEntry.get()
    passw = passEntry.get()
    repo = repoEntry.get()
    flag = True
    if login=='' and not data['login']:
        loginEntry.delete(0,END)
        loginEntry.insert(0,"Wypełnij to pole")
        flag = False
    if passw=='' and not data['password']:
        passEntry.delete(0,END)
        passEntry.insert(0,"Wypełnij to pole")
        flag = False
    if repo=='' and not data['repoName']:
        repoEntry.delete(0,END)
        repoEntry.insert(0,"Wypełnij to pole")
        flag = False
    if (path is None or path=='') and not data['folderPath']:
        pathButton.config(fg='red')
        flag=False
    if flag:
        pathButton.config(fg='black')
        if not data['folderPath'] and path!='':
            data['folderPath'] = path
        if not data['login'] and login!='':
            data['login'] = login
        if not data['password'] and passw!='':
            data['password'] = passw
        if not data['repoName'] and repo!='':
            data['repoName'] = repo
        errSetLabel.place_forget()
        write_file(data)
        messagebox.showinfo('INFO','Ustawienia zostały zapisane', parent=root)
        toMain()

def read_data():
    with open('data.json') as f:
        return json.loads(f.read())

def on_enter(event):
    event.widget.config(bg='#f5f5f5')
def on_leave(event):
    event.widget.config(bg='#e5e5e5')

def toSettings(*args):
    global mainButton,setButton,loginEntry,passEntry,loginLabel, passLabel,backMain,pathButton,pathLabel,\
    setCnfBut,repoLabel,repoEntry
    mainButton.place_forget(); setButton.place_forget()
    loginLabel.place(relx=.1,rely=.1,relwidth=.4,relheight=.1)
    loginEntry.place(relx=0.5,rely=0.1,relwidth=0.3,relheight=0.1)
    passLabel.place(relx=.1,rely=.25,relwidth=.4,relheight=.1)
    passEntry.place(relx=.5,rely=0.25,relwidth=0.3, relheight=.1)
    pathLabel.place(relx=.1,rely=.4,relwidth=0.4,relheight=.1)
    pathButton.place(relx=.5,rely=.4,relwidth=0.3,relheight=.1)
    repoLabel.place(relx=.1,rely=.55,relwidth=.4,relheight=.1)
    repoEntry.place(relx=.5,rely=.55,relwidth=.3,relheight=.1)
    setCnfBut.place(relx=.3,rely=.7,relwidth=.4,relheight=.1)
    backMain.place(relx=0,rely=.9,relwidth=1,relheight=.1)

def saveEx(*args):
    global exsVar, fldsVar, host, exs, data,actsList
    path = data['folderPath']+f'/{fldsVar.get()}'
    actsList.insert(END,"Sprawdzanie katalogu"); cl("#cc9900");actsList.yview_moveto(2)
    root.update()
    if not os.path.exists(path):
        os.mkdir(path)
        actsList.insert(END,f"Tworzenie dodatkowego katalogu {path}")
        root.update();actsList.yview_moveto(2)
    else:
        actsList.insert(END,f"Folder {path} istnieje")
        root.update();actsList.yview_moveto(2)
    if exsVar.get()=='wszystkie':
        for f in exs[fldsVar.get()]:
            with open(path+f'/{f}', 'w') as file:
                actsList.insert(END, f"Pobieranie zadania {f} z serwera")
                root.update();actsList.yview_moveto(2)
                file.write(json.loads(get(host, params={'auth':'07072005', 'loc':fldsVar.get(),'ex':f}).text)['solution'])
                actsList.insert(END, f"Utworzono plik {f} w folderze {path}")
                actsList.yview_moveto(2)
                root.update()
    else:
        with open(path+f'/{exsVar.get()}', 'w') as file:
            actsList.insert(END, f"Pobieranie zadania {exsVar.get()} z serwera")
            root.update();actsList.yview_moveto(2)
            file.write(json.loads(get(host, params={'auth':'07072005', 'loc':fldsVar.get(),'ex':exsVar.get()}).text)['solution'])
            actsList.insert(END, f"Utworzono plik {exsVar.get()} w folderze {path}")
            root.update();actsList.yview_moveto(2)
    actsList.insert(END,"Zrobione"); cl("green");actsList.yview_moveto(2)

def checkCommit(*args):
    pass

def makeCommit(*args):
    global actsList,data,sureEntry,mainPath
    os.chdir(data['folderPath'])
    actsList.insert(END,"Sprawdzanie lokalnego repo");cl('#cc9900');root.update();actsList.yview_moveto(2)
    if not os.path.exists(data['folderPath']+f'/.git'):
        actsList.insert(END,"Inicjowanie lokalnego repo");cl("#cc9900");root.update();actsList.yview_moveto(2)
        with Popen(["git","init"],stdout=PIPE) as p:
            actsList.insert(END,"Lokalne repo zainicjowane"); cl('green');root.update();actsList.yview_moveto(2)
    else:
        actsList.insert(END,"Lokalne repo istnieje");root.update();actsList.yview_moveto(2)
    with Popen(["git","ls-remote","--exit-code","origin"],stdout=PIPE,stderr=PIPE) as p:
        actsList.insert(END,"Sprawdzanie remote\'a");cl('#cc9900');root.update();actsList.yview_moveto(2)
        if not b"fatal" in p.stderr.read():
            actsList.insert(END,"Remote istnieje");root.update();actsList.yview_moveto(2)
        else:
            actsList.insert(END,"Nie wykryto remote'a origin. Próba utworzenia");cl('#cc0000');root.update();actsList.yview_moveto(2)
            with Popen(["git","remote","add","origin",f"https://github.com/{data['login']}/{data['repoName']}"]) as p2:
                actsList.insert(END,"Dodano remote");cl('green');root.update();actsList.yview_moveto(2)
    with Popen(["git","add","."],stdout=PIPE) as p:
        actsList.insert(END,'Dodawanie plików do lokalnego repo');actsList.yview_moveto(2);root.update()
    with Popen(['git','commit','-m','\"'+sureEntry.get()+'\"'],stdout=PIPE) as p:
        actsList.insert(END, f"Utworzono commit z wiadomością: {sureEntry.get()}");root.update();actsList.yview_moveto(2)
        with Popen(['git','push','-u','origin','master'],stdout=PIPE,stderr=PIPE,stdin=PIPE) as p2:
            if not p2.stdout.read()==b"":
                os.system('git push -u origin master')
                actsList.insert(END,'Dodano niezbędne pliki do repozytorium GitHub');root.update();actsList.yview_moveto(2)
                actsList.insert(END,'Zrobione');cl('green');root.update();actsList.yview_moveto(2)
            else:
                actsList.insert(END,'Wykryto nie powiązane historie. Próba naprawienia.');cl('#cc0000');root.update();actsList.yview_moveto(2)
                os.mkdir('copy')
                actsList.insert(END,'Przenoszenie plików do folderu: copy');root.update();actsList.yview_moveto(2)
                for file in os.listdir():
                    if file != '.git' and file!='copy':
                        shutil.move(file, f'copy/{file}')
                actsList.insert(END,'Próba wysłania żądania pull');cl('#cc9900');root.update();actsList.yview_moveto(2)
                with Popen(["git","pull","origin","master","--allow-unrelated-histories"],stdout=PIPE,stderr=PIPE) as p3:
                    actsList.insert(END,'Usuwanie plików żądania');root.update();actsList.yview_moveto(2)
                    for file in os.listdir():
                        if file!='.git' and file != 'copy':
                            try:
                                os.remove(file)
                            except:
                                os.rmdir(file)
                    os.chdir('./copy')
                    actsList.insert(END,'Przenoszenie plików do głównego katalogu');root.update();actsList.yview_moveto(2)
                    for file in os.listdir():
                        shutil.move(file, f'../{file}')
                    actsList.insert(END,'Usuwanie katalogu: copy');root.update();actsList.yview_moveto(2)
                    os.chdir('../')
                    os.rmdir('copy')
                    if b"fatal" not in p3.stderr.read():
                        actsList.insert(END,'Żądanie wykonane bez błędów');cl('green');root.update();actsList.yview_moveto(2)
                        actsList.insert(END,'Ponawianie procesu...');root.update();actsList.yview_moveto(2)
                        with Popen(['git','push','-u','origin','master'],stdout=PIPE,stderr=PIPE,stdin=PIPE) as p4:
                            if not p4.stdout.read()==b"":
                                os.system('git push -u origin master')
                                actsList.insert(END,'Dodano niezbędne pliki do repozytorium GitHub');root.update();actsList.yview_moveto(2)
                                actsList.insert(END,'Zrobione');cl('green');root.update();actsList.yview_moveto(2)
                            else:
                                actsList.insert(END,'Nie udało się rozwiązać problemu. Spróbuj ponownie...');cl('#cc0000');
                                root.update(); actsList.yview_moveto(2)
                    else:
                        actsList.insert(END,f'Żądanie zakończyło się błędem: {p3.stderr.read()}');cl('#cc0000')
                        os.chdir('../')
                        root.update();actsList.yview_moveto(2)
    os.chdir(mainPath)



def toGit(*args):
    global gitButton,backMain,data,backEx,fldsList,exsList,cnfButton,sureLabel,sureButton,sureEntry
    fldsList.place_forget(); exsList.place_forget()
    gitButton.place_forget(); backMain.place_forget()
    cnfButton.place_forget()
    sureLabel.place(relx=.06,rely=.15,relwidth=.27,relheight=.1)
    sureEntry.place(relx=.39,rely=.15,relwidth=.27,relheight=.1)
    sureButton.place(relx=.69,rely=.15,relwidth=.27,relheight=.1)
    backEx.place(relx=0,rely=.9,relwidth=1,relheight=.1)

def toEx(*args):
    global backMain,mainButton,setButton,exsList,fldsList,cnfButton,actsList,aFrame,aScroll,gitButton,backEx, \
    sureLabel, sureButton, sureEntry
    sureLabel.place_forget(); sureButton.place_forget()
    backEx.place_forget(); sureEntry.place_forget()
    exsList.place(relx=.36,rely=.15,relwidth=.28,relheight=0.1); fldsList.place(relx=0.04,rely=.15,relwidth=.28,relheight=.1)
    cnfButton.place(relx=.68,rely=.155,relwidth=.28,relheight=.09)
    mainButton.place_forget(); setButton.place_forget()
    aFrame.place(relx=.1,rely=.3,relwidth=.8, relheight=.55)
    actsList.place(relx=0,rely=0,relwidth=.97, relheight=1)
    aScroll.pack(side=RIGHT, fill=Y)
    gitButton.place(relx=.55,rely=.9,relwidth=.45,relheight=.1)
    backMain.place(relx=0,rely=.9,relwidth=.45,relheight=.1)

def toMain(*args):
    global mainButton,setButton,loginEntry,loginLabel,passEntry,passLabel,backMain,exsList,fldsList, \
    cnfButton,pathLabel,pathButton,setCnfBut,aFrame,repoLabel,repoEntry,gitButton
    pathLabel.place_forget(); pathButton.place_forget()
    exsList.place_forget(); fldsList.place_forget()
    loginLabel.place_forget();loginEntry.place_forget()
    passLabel.place_forget();passEntry.place_forget()
    backMain.place_forget(); cnfButton.place_forget()
    setCnfBut.place_forget(); aFrame.place_forget()
    repoLabel.place_forget(); repoEntry.place_forget()
    gitButton.place_forget()
    mainButton.place(relx=0.35,rely=0.4,relwidth=0.3, relheight=0.1)
    setButton.place(relx=0.35,rely=0.5,relwidth=0.3,relheight=0.1)

def showDialog(*args):
    global path,root
    path = filedialog.askdirectory(parent=root,initialdir='documents')

host = 'http://najlepszawgalaktyce.000webhostapp.com/api/'
exs = {}

def load(p,l,r):
    opt = json.loads(get(host,params={'auth':'07072005','quests':'all'}).text)['quests']
    p["maximum"] = len(opt)
    for i in range(len(opt)):
        exs[opt[i]] = json.loads(get(host,params={'auth':'07072005','loc':opt[i]}).text)['exercises']
        l["text"] = f"Pobieranie danych z folderu {opt[i]}"
        p["value"] += 1
    r.destroy()

lroot = Tk()
lroot.geometry('600x400')
lroot.title('Ładowanie danych...')
lroot.iconbitmap('logo.ico')

Label(lroot,text='Ładowanie...').place(relx=0,rely=.35,relwidth=1,relheight=.1)
p = Progressbar(lroot, length=100, mode='determinate')
p.place(relx=.1,rely=.45,relwidth=.8,relheight=0.1)
l = Label(lroot,text='')
l.place(relx=0,rely=.55, relwidth=1, relheight=.1)
th = threading.Thread(target=load, args=(p,l,lroot,))
th.start()

lroot.mainloop()

root = Tk()

def trace_change(*args):
    global exsVar, exsList, exs, fldsVar
    exsList.place_forget()
    exsVar.set(exs[fldsVar.get()][0])
    ex = [x for x in exs[fldsVar.get()]]
    ex.append('wszystkie')
    exsList = OptionMenu(root,exsVar,*ex)
    exsList.config(bd=0,bg='#e5e5e5')
    exsList.place(relx=.36,rely=.15,relwidth=.28,relheight=0.1)

data = read_data()
path = None
fldsVar = StringVar(root); fldsVar.set(list(exs.keys())[0])
fldsVar.trace("w", trace_change); FLD = [x for x in exs.keys()]
fldsList = OptionMenu(root, fldsVar, *FLD); fldsList.config(bd=0, bg='#e5e5e5')
exsVar = StringVar(root); exsVar.set(exs[fldsVar.get()][0])
ex = [x for x in exs[fldsVar.get()]]; ex.append('wszystkie')
exsList = OptionMenu(root,exsVar,*ex); exsList.config(bd=0,bg='#e5e5e5')
mainButton = Button(root, text='Znajdź zadanie', bg='#e5e5e5',bd=0, comman=toEx)
setButton = Button(root, text='Zmień ustawienia', bg='#e5e5e5', bd=0, command=toSettings)
loginEntry, passEntry = Entry(root, bd=0, justify=CENTER), Entry(root, bd=0, justify=CENTER)
loginLabel, passLabel = Label(root, text='Podaj login do GitHuba: '), Label(root, text='Podaj hasło do GitHuba: ')
pathLabel, pathButton = Label(root,text='Wybierz folder z zadaniami: '),Button(root,text='Wybierz folder',bg='#e5e5e5',bd=0,command=showDialog)
repoLabel, repoEntry = Label(root,text='Nazwa repo: '),Entry(root,bd=0,justify=CENTER)
backMain = Button(root,text='Wróć do ekranu głównego',bg='#e5e5e5',bd=0,command=toMain)
setCnfBut = Button(root,text='Zapisz',bg='#e5e5e5',bd=0,command=saveSet)
cnfButton = Button(root,text='Pobierz',command=saveEx,bg='#e5e5e5',bd=0)
gitButton = Button(root,text='Zaktualizuj repo',bd=0,bg='#e5e5e5',command=toGit)
cnfButton.bind('<Enter>',on_enter); cnfButton.bind('<Leave>', on_leave)
gitButton.bind('<Enter>',on_enter); gitButton.bind('<Leave>', on_leave)
mainButton.bind('<Enter>',on_enter); mainButton.bind('<Leave>', on_leave)
setButton.bind('<Enter>',on_enter); setButton.bind('<Leave>',on_leave)
pathButton.bind('<Enter>',on_enter); pathButton.bind('<Leave>',on_leave)
setCnfBut.bind('<Enter>',on_enter); setCnfBut.bind('<Leave>',on_leave)
backMain.bind('<Enter>',on_enter); backMain.bind('<Leave>',on_leave)
backEx = Button(root,text='Wróć do zadań',command=toEx,bd=0,bg='#e5e5e5')
backEx.bind('<Enter>',on_enter); backEx.bind('<Leave>',on_leave)
sureLabel,sureButton=Label(root,text='Podaj wiadomość commita'),Button(root,text='Start',bd=0,bg='#e5e5e5',command=makeCommit)
sureButton.bind('<Enter>',on_enter); sureButton.bind('<Leave>',on_leave)
sureEntry = Entry(root,bd=0,justify=CENTER)
errSetLabel = Label(root,text='Twoje ustawienia nie są skonfigurowane !!!',fg='red')
aFrame = Frame(root); aScroll = Scrollbar(aFrame, orient=VERTICAL)
actsList = Listbox(aFrame, yscrollcommand=aScroll.set)
aScroll.config(command=actsList.yview)
mainPath = os.getcwd()

root.geometry('600x400')
root.title('Programowanie')
root.iconbitmap('logo.ico')

for v in data.values():
    if v is None:
        errSetLabel.place(relx=0,rely=0,relwidth=1,relheight=.1)

toMain()

root.mainloop()
