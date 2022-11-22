from os import walk
import os
import sqlite3
import hashlib

def getFileHashMD5(filename):
    m = hashlib.sha1()
    with open(filename, 'rb', 1024*1024) as fh:
          while True:
            data = fh.read(1024*1024)
            if not data:
                break
            m.update(data)
    return m.hexdigest()


conn = sqlite3.connect('Dirsv2.db')
print("Opened database successfully")
#conn.execute('''DROP TABLE IF EXISTS Dirs''')
conn.execute('''CREATE  TABLE IF NOT EXISTS Folders 
        ("folderid"             integer primary key autoincrement,
        "FolderName"          TEXT,
        "Path"              TEXT    NOT NULL, 
        "Parent"            INTEGER NOT NULL,   
        "size"              BIGINT  DEFAULT 0
       
    )''')
conn.execute('''CREATE  TABLE IF NOT EXISTS Files 
        ("fileid"             integer primary key autoincrement,
        "Filename"          TEXT,
        "Path"              TEXT    NOT NULL,        
        "hashfile"              TEXT    DEFAULT NULL,
        "folderid"            INTEGER NOT NULL,     
        "fileExt"           TEXT DEFAULT NULL,
        "size"              BIGINT  DEFAULT 0,
        PRIMARY             KEY("fileid")
    )''')
print("Table created successfully")

folder_list = {}
node = 1
fileExt = ""
my_path = "d:\\bidv"
for (dirpath, dirnames, filenames) in walk(my_path):
    # Always starts by opening/viewing a folder
    isFolder = 1

    # Current file name is the last name in the path. Stripped for backslashes, but getting one back at the end
    curr_filename = dirpath.split("\\")[-1] + "\\"

    parent_node = 1

    # A folders parent folder
    parent_folder_of_folder = dirpath.split("\\")
    # Adding back the stripped backslash to make its name more visible as a folder
    pfof_name = ""
    for i in parent_folder_of_folder[:-1]:
        pfof_name += i + "\\"

    # Adds only dirpath if it does not exist, and because folderlist is hardcoded at first index, we'll skip it.
    if dirpath not in folder_list:
        match = {node: dirpath}
        folder_list[str(node)] = dirpath

    for key, value in folder_list.items():
        # Makes parent node set to its belonging index and checks if it is a folder to avoid a folder to be set as
        # its own parent.
        if dirpath == value and isFolder == 0:
            parent_node = key
            break
        # Sets parent_node to the key of its parent folder by checking that it is a folder and what the splitted
        # output of its path up to its folder name is equal to.
        elif (pfof_name.rstrip("\\")) == value and isFolder == 1:
            parent_node = key
            break
    # Parameters to execute for folders
    params = (curr_filename, dirpath, parent_node)
    cursor=conn.cursor()    
    cursor.execute('''INSERT INTO Folders (FolderName,Path,Parent) VALUES (?, ?, ?)''', params)
    print(cursor.lastrowid)
     
    # Iterate over every file inside a folder
    for i in filenames:
        # Starting file iteration - turn isFolder to False.
        isFolder = 0
        curr_filename = i

        # Iterate over our folder list to check for a match of current file's parent folder. Break when found.
        for key, value in folder_list.items():
            if dirpath == value:
                parent_node = key
                print(key, value)
                break

        # If current file is not a folder and contains a "dot" which may indicate to be an extension, save its ext.
        # Works only for explicit files thus far. Not reading file-headers at all.
        if isFolder == 0 and "." in curr_filename.split("\\")[-1]:
            fileExt = curr_filename.split(".")[-1]
        
        
        filesize = os.path.getsize(dirpath + "\\" + curr_filename)
       # hashfile = getFileHashMD5(dirpath + "\\" + curr_filename)
        # Parameters to execute in sqlite for files
        params = (curr_filename, dirpath + "\\" + curr_filename, parent_node, fileExt, filesize)
        cursor.execute('''INSERT INTO Files (Filename,Path,folderid,fileExt,size)  VALUES (?, ?, ?, ?, ?)''', params)
        conn.commit()
        # Node iteration to keep up with
        node += 1
        # File iteration done, next up is folder, unless more iterations
        isFolder = 1
        # Make file extension to NULL
        fileExt = ""
    node += 1
conn.commit()
print("Records created successfully")
conn.close()