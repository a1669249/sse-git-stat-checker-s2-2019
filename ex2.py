import sys
import os
import re
from git import Repo

GITFOLDER = '/mnt/e/Documents/GitHub/' # Change this to the directory where you store your Repo's

def printInfo():
	print("a. Message and title")
	print(commit.message)
	
	print("\nb. Files")
	print(len(fileList))
	for file in fileList:
		print(file);
	
	print("\nc. Directories")
	print(len(dirList))
	for directory in dirList:
		print(directory)

	print("\nd. Lines Deleted")
	print(deletedLines)

	print("\ne. Lines Added")
	print(addedLines)

	print("\nf. Lines Deleted (No Comments/Blanks)")
	print(deletedLines-nonDeletions)

	print("\ng. Lines Added (No Comments/Blanks)")
	print(addedLines-nonAdditions)

	print("\nh. Days Since Previous Commit")
	for file, time in zip(fileList,timeDiff):
		print(file+': '+"{:.1f}".format(time/86400))
	
	print("\ni. Commits Per File")
	for file, commits in zip(fileList,numCommits):
		print(file+': '+str(commits))
	
	print("\nj. Developers On Each File")
	for file, authors in authorPerFile.items():
		authorStr = "";
		for a in authors:
			authorStr += a+', '

		print(file+': '+authorStr[:-2])
	
	print("\nk. Commits Per Developer");
	for author, commits in authorAndCommits.items():
		print(author+': '+str(commits))

if len(sys.argv) != 3:
	print("Arguments:\n\t1. Repo folder name\n\t2. Commit name/number")
	sys.exit()

repoFolder = sys.argv[1]
commitName = sys.argv[2]

# GitPython objects
repo = Repo(GITFOLDER+repoFolder)
commit = repo.commit(commitName);

fileList = []
dirList = []
deletedLines = 0
addedLines = 0
nonDeletions = 0
nonAdditions = 0
timeDiff = []
numCommits = []
authorPerFile = {}
authorAndCommits = {}

for file in commit.stats.files:
	dirName = os.path.dirname(file);
	fileName = os.path.basename(file);
	
	fileList.append(fileName)

	authorPerFile[fileName] = []

	if dirName not in dirList:
		dirList.append(dirName)

	time1 = int(repo.git.log(commit,'--', file,n=1,format="%cd",date='unix'))
	time2 = int(repo.git.log(commit,'--', file,n=1,skip=1,format="%cd",date='unix'))
	timeDiff.append(time1-time2);

	numCommits.append(len(repo.git.log(commit, '--', file,format="%cd").splitlines())-1)
	
	authors=repo.git.log(commit, '--',file,format="%an").split("\n")
	for a in authors:
		if a not in authorPerFile[fileName]:
			authorPerFile[fileName].append(a)
		authorAndCommits[a] = authorAndCommits.get(a,0) + 1


deletedLines = commit.stats.total['deletions']
addedLines += commit.stats.total['insertions']

changes = repo.git.show(commitName)

for line in changes.splitlines():
	if line:
		if line[0] == '-':
			if len(line) < 2:
				nonDeletions += 1 # Blank line deletion
			elif line[1] != '-' and re.match('^(\/\/)|^(\/\*)|^#|^\*',line[1:].strip()):
				nonDeletions += 1 # Comment deletion
		elif line[0] == '+':
			if len(line) < 2:
				nonAdditions += 1 # Blank line addition
			elif line[1] != '+' and re.match('^(\/\/)|^(\/\*)|^#|^\*',line[1:].strip()):
				nonAdditions += 1 # Comment addition

printInfo()