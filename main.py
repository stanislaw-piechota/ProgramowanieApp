import json
import os
import shutil
import threading
import time
from requests import get
from subprocess import Popen, PIPE
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from tkinter.ttk import Progressbar, Scrollbar
from PIL import ImageTk, Image

font=('Courier', 12, 'normal')
font2=('Courier',9,'normal')

class MyLabel(Label):
    def __init__(self, master, filename, logo):
        im = Image.open(filename)
        seq =  []
        try:
            while 1:
                seq.append(im.copy())
                im.seek(len(seq))
        except EOFError:
            pass

        try:
            self.delay = im.info['duration']
        except KeyError:
            self.delay = 100

        first = seq[0].convert('RGBA')
        self.frames = [ImageTk.PhotoImage(first)]
        master.geometry(f'{self.frames[0].width()}x{self.frames[0].height()}')

        Label.__init__(self, master, image=self.frames[0])

        lut = [1] * 256
        lut[im.info["transparency"]] = 0

        temp = seq[0]
        for image in seq[1:]:
            mask = image.point(lut, "1")
            temp.paste(image, None, mask)
            frame = temp.convert('RGBA')
            self.frames.append(ImageTk.PhotoImage(frame))

        self.idx = 0

        self.cancel = self.after(1000, self.play)

    def play(self):
        self.config(image=self.frames[self.idx])
        self.idx += 1
        if self.idx == len(self.frames):
            self.idx = 0
        self.cancel = self.after(self.delay, self.play)

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
        loginEntry.insert(0,"Fill this field")
        flag = False
    if passw=='' and not data['password']:
        passEntry.delete(0,END)
        passEntry.insert(0,"Fill this field")
        flag = False
    if repo=='' and not data['repoName']:
        repoEntry.delete(0,END)
        repoEntry.insert(0,"Fill this field")
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
        messagebox.showinfo('INFO','Settings saved', parent=root)
        toMain()

def read_data():
    with open('data.json') as f:
        return json.loads(f.read())

def on_enter(event):
    event.widget.config(bg='#28ffff')
def on_leave(event):
    event.widget.config(bg='#29baa6')

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
    actsList.insert(END,"Checking localisation"); cl("#cc9900");actsList.yview_moveto(2)
    root.update()
    if not os.path.exists(path):
        os.mkdir(path)
        actsList.insert(END,f"Creating folder {path}")
        root.update();actsList.yview_moveto(2)
    else:
        actsList.insert(END,f"Folder {path} exists")
        root.update();actsList.yview_moveto(2)
    if exsVar.get()=='all':
        for f in exs[fldsVar.get()]:
            with open(path+f'/{f}', 'w') as file:
                actsList.insert(END, f"Downloading ex. {f} from server")
                root.update();actsList.yview_moveto(2)
                file.write(json.loads(get(host, params={'auth':'07072005', 'loc':fldsVar.get(),'ex':f}).text)['solution'])
                actsList.insert(END, f"Created file {f} in {path}")
                actsList.yview_moveto(2)
                root.update()
    else:
        with open(path+f'/{exsVar.get()}', 'w') as file:
            actsList.insert(END, f"Downloading ex. {exsVar.get()} from server")
            root.update();actsList.yview_moveto(2)
            file.write(json.loads(get(host, params={'auth':'07072005', 'loc':fldsVar.get(),'ex':exsVar.get()}).text)['solution'])
            actsList.insert(END, f"Created file {exsVar.get()} in {path}")
            root.update();actsList.yview_moveto(2)
    actsList.insert(END,"Done"); cl("green");actsList.yview_moveto(2)

def checkCommit(*args):
    pass

def makeCommit(*args):
    global actsList,data,sureEntry,mainPath
    os.chdir(data['folderPath'])
    actsList.insert(END,"Checking local repo");cl('#cc9900');root.update();actsList.yview_moveto(2)
    if not os.path.exists(data['folderPath']+f'/.git'):
        actsList.insert(END,"Initializing local repo");cl("#cc9900");root.update();actsList.yview_moveto(2)
        with Popen(["git","init"],stdout=PIPE) as p:
            actsList.insert(END,"Local repo initialized"); cl('green');root.update();actsList.yview_moveto(2)
    else:
        actsList.insert(END,"Local repo exists");root.update();actsList.yview_moveto(2)
    with Popen(["git","ls-remote","--exit-code","origin"],stdout=PIPE,stderr=PIPE) as p:
        actsList.insert(END,"Checking remote");cl('#cc9900');root.update();actsList.yview_moveto(2)
        if not b"fatal" in p.stderr.read():
            actsList.insert(END,"Remote exists");root.update();actsList.yview_moveto(2)
        else:
            actsList.insert(END,"Remote origin not detected. Attempting to create");cl('#cc0000');root.update();actsList.yview_moveto(2)
            with Popen(["git","remote","add","origin",f"https://github.com/{data['login']}/{data['repoName']}"]) as p2:
                actsList.insert(END,"Remote added");cl('green');root.update();actsList.yview_moveto(2)
    with Popen(["git","add","."],stdout=PIPE) as p:
        actsList.insert(END,'Adding files to local repo');actsList.yview_moveto(2);root.update()
    with Popen(['git','commit','-m','\"'+sureEntry.get()+'\"'],stdout=PIPE) as p:
        actsList.insert(END, f"Created commit with message: {sureEntry.get()}");root.update();actsList.yview_moveto(2)
        with Popen(['git','push','-u','origin','master'],stdout=PIPE,stderr=PIPE,stdin=PIPE) as p2:
            if not p2.stdout.read()==b"":
                os.system('git push -u origin master')
                actsList.insert(END,'Pushed necessary files into GitHub');root.update();actsList.yview_moveto(2)
                actsList.insert(END,'Done');cl('green');root.update();actsList.yview_moveto(2)
            else:
                actsList.insert(END,'Detected unrelated histories. Attempting to fix');cl('#cc0000');root.update();actsList.yview_moveto(2)
                os.mkdir('copy')
                actsList.insert(END,'Moving files to: copy');root.update();actsList.yview_moveto(2)
                for file in os.listdir():
                    if file != '.git' and file!='copy':
                        shutil.move(file, f'copy/{file}')
                actsList.insert(END,'Sending pull request');cl('#cc9900');root.update();actsList.yview_moveto(2)
                with Popen(["git","pull","origin","master","--allow-unrelated-histories"],stdout=PIPE,stderr=PIPE) as p3:
                    actsList.insert(END,'Deleting request files');root.update();actsList.yview_moveto(2)
                    for file in os.listdir():
                        if file!='.git' and file != 'copy':
                            try:
                                os.remove(file)
                            except:
                                os.rmdir(file)
                    os.chdir('./copy')
                    actsList.insert(END,'Moving files back');root.update();actsList.yview_moveto(2)
                    for file in os.listdir():
                        shutil.move(file, f'../{file}')
                    actsList.insert(END,'Deleting folder: copy');root.update();actsList.yview_moveto(2)
                    os.chdir('../')
                    os.rmdir('copy')
                    if b"fatal" not in p3.stderr.read():
                        actsList.insert(END,'Request successful');cl('green');root.update();actsList.yview_moveto(2)
                        actsList.insert(END,'Retrying...');root.update();actsList.yview_moveto(2)
                        with Popen(['git','push','-u','origin','master'],stdout=PIPE,stderr=PIPE,stdin=PIPE) as p4:
                            if not p4.stdout.read()==b"":
                                os.system('git push -u origin master')
                                actsList.insert(END,'Pushed necessary files into GitHub');root.update();actsList.yview_moveto(2)
                                actsList.insert(END,'Done');cl('green');root.update();actsList.yview_moveto(2)
                            else:
                                actsList.insert(END,'Unable to solve. Retry or fix manually');cl('#cc0000');
                                root.update(); actsList.yview_moveto(2)
                    else:
                        actsList.insert(END,f'Request failed: {p3.stderr.read()}');cl('#cc0000')
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

from update import *
def load(l,r):
    opt = json.loads(get(host,params={'auth':'07072005','quests':'all'}).text)['quests']
    for i in range(len(opt)):
        exs[opt[i]] = json.loads(get(host,params={'auth':'07072005','loc':opt[i]}).text)['exercises']
        l.config(text=f"Gathering data from {opt[i]}")
    r.destroy()

lroot = Tk()
lroot.attributes("-topmost", 1)
lroot.geometry('400x300')
lroot.geometry(f'+{int(lroot.winfo_screenwidth()/2-200)}+{int(lroot.winfo_screenheight()/2-150)}')
lroot.overrideredirect(True)

MyLabel(lroot, 'loading1.gif', lroot).pack()
image = Image.open('logo.png')
image = image.resize((50, 50), Image.ANTIALIAS)
image = ImageTk.PhotoImage(image)
Label(image=image).place(relx=.4375,rely=.175,relwidth=.125,relheight=.167)
l = Label(lroot,font=font,text='Checking updates',bg='#1C273A',fg='white')
l.place(relx=0,rely=.6, relwidth=1, relheight=.1)
th = threading.Thread(target=load, args=(l,lroot,))
th.start()
lroot.mainloop()

root = Tk()
root["bg"] = "#1C273A"

def trace_change(*args):
    global exsVar, exsList, exs, fldsVar
    exsList.place_forget()
    exsVar.set(exs[fldsVar.get()][0])
    ex = [x for x in exs[fldsVar.get()]]
    ex.append('all')
    exsList = OptionMenu(root,exsVar,*ex)
    exsList.config(bd=0,bg='#29baa6',font=font2,fg='#1C273A')
    exsList.place(relx=.36,rely=.15,relwidth=.28,relheight=0.1)

data = read_data()
path = None
fldsVar = StringVar(root); fldsVar.set(list(exs.keys())[0])
fldsVar.trace("w", trace_change); FLD = [x for x in exs.keys()]
fldsList = OptionMenu(root, fldsVar, *FLD); fldsList.config(bd=0, bg='#29baa6',font=font2,fg='#1C273A')
exsVar = StringVar(root); exsVar.set(exs[fldsVar.get()][0])
ex = [x for x in exs[fldsVar.get()]]; ex.append('all')
exsList = OptionMenu(root,exsVar,*ex); exsList.config(bd=0,bg='#29baa6',fg='#1C273A',font=font2)
mainButton = Button(root,font=font,fg='#1C273A', text='Find exercises', bg='#29baa6',bd=0, comman=toEx)
setButton = Button(root,font=font,fg='#1C273A', text='Change settings', bg='#29baa6', bd=0, command=toSettings)
loginEntry, passEntry = Entry(root,fg='#1C273A',font=font2, bd=0, justify=CENTER), Entry(root,fg='#1C273A',font=font2, bd=0, justify=CENTER)
loginLabel, passLabel = Label(root,font=font,fg='white',bg='#1C273A', text='GitHub login: ',justify=RIGHT), Label(root,font=font,justify=RIGHT,fg='white',bg='#1C273A', text='GitHub password: ')
pathLabel, pathButton = Label(root,font=font,fg='white',bg='#1C273A',text='Local repo: ',justify=RIGHT),Button(root,font=font,fg='#1C273A',text='Select folder',bg='#29baa6',bd=0,command=showDialog)
repoLabel, repoEntry = Label(root,font=font,fg='white',bg='#1C273A',text='Repo name: ',justify=RIGHT),Entry(root,fg='#1C273A',font=font2,bd=0,justify=CENTER)
backMain = Button(root,font=font,fg='#1C273A',text='Go back',bg='#29baa6',bd=0,command=toMain)
setCnfBut = Button(root,font=font,fg='#1C273A',text='Save',bg='#29baa6',bd=0,command=saveSet)
cnfButton = Button(root,font=font,fg='#1C273A',text='Download',command=saveEx,bg='#29baa6',bd=0)
gitButton = Button(root,font=font,fg='#1C273A',text='Update repo',bd=0,bg='#29baa6',command=toGit)
cnfButton.bind('<Enter>',on_enter); cnfButton.bind('<Leave>', on_leave)
gitButton.bind('<Enter>',on_enter); gitButton.bind('<Leave>', on_leave)
mainButton.bind('<Enter>',on_enter); mainButton.bind('<Leave>', on_leave)
setButton.bind('<Enter>',on_enter); setButton.bind('<Leave>',on_leave)
pathButton.bind('<Enter>',on_enter); pathButton.bind('<Leave>',on_leave)
setCnfBut.bind('<Enter>',on_enter); setCnfBut.bind('<Leave>',on_leave)
backMain.bind('<Enter>',on_enter); backMain.bind('<Leave>',on_leave)
backEx = Button(root,font=font,fg='#1C273A',text='Go back',command=toEx,bd=0,bg='#29baa6')
backEx.bind('<Enter>',on_enter); backEx.bind('<Leave>',on_leave)
sureLabel,sureButton=Label(root,font=font2,fg='white',bg='#1C273A',text='Commit message: '),Button(root,font=font,fg='#1C273A',text='Start',bd=0,bg='#29baa6',command=makeCommit)
sureButton.bind('<Enter>',on_enter); sureButton.bind('<Leave>',on_leave)
sureEntry = Entry(root,fg='#1C273A',font=font2,bd=0,justify=CENTER)
errSetLabel = Label(root,font=font,fg='white',bg='#1C273A',text='Change settings before you start!!!')
aFrame = Frame(root); aScroll = Scrollbar(aFrame, orient=VERTICAL)
actsList = Listbox(
aFrame, font=font2,fg='#1C273A',yscrollcommand=aScroll.set)
aScroll.config(command=actsList.yview)
mainPath = os.getcwd()

root.geometry('600x400')
root.title('Programming')
root.iconbitmap('logo.ico')

for v in data.values():
    if v is None:
        errSetLabel.place(relx=0,rely=0,relwidth=1,relheight=.1)
from update import *
print(update())
toMain()

root.mainloop()
