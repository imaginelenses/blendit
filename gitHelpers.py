import os
from datetime import datetime, timezone, timedelta

import pygit2 as git
from pygit2._pygit2 import GitError

# Format: Fri Sep  2 19:36:07 2022 +0530
GIT_TIME_FORMAT = "%c %z"


def getLastModifiedStr(date):
    """
    Returns last modified string
    date: offset-aware datetime.datetime object
    """

    # Get time difference            
    now = datetime.now(timezone.utc)    
    delta = now - date

    output = ""

    days = delta.days
    if days <= 0:
        hours = delta.seconds // 3600
        if hours <= 0:
            mins = (delta.seconds // 60) % 60
            if mins <= 0:
                secs = delta.seconds - hours * 3600 - mins * 60
                if secs <= 0:
                    output = "now"
                
                # Secs
                elif secs == 1:
                    output = f"{secs} sec"
                else:
                    output = f"{secs} sec"

            # Mins
            elif mins == 1:
                output = f"{mins} min"
            else:
                output = f"{mins} mins"

        # Hours
        elif hours == 1:
            output = f"{hours} hr"
        else:
            output = f"{hours} hrs"
    
    # Days
    elif days == 1:
        output = f"{days} day"
    else:
        output = f"{days} days"

    return output


def commit(repo, message):
    """Add all and commit changes to current branch"""

    repo.index.add_all()
    repo.index.write()
    tree = repo.index.write_tree()
    
    try:
        # Assuming prior commits exist
        ref = repo.head.name
        parents = [repo.head.target]
    except GitError:
        # Initial Commit
        ref = "HEAD"
        parents = []
    
    repo.create_commit(
        ref,
        repo.default_signature,
        repo.default_signature,
        message,
        tree,
        parents,
    )


def getCommits(repo):
    """Returns a list commit objects"""

    commits = []
    last = repo[repo.head.target]
    for commit in repo.walk(last.id, git.GIT_SORT_TIME):
        timezoneInfo = timezone(timedelta(minutes=commit.author.offset))
        datetimeString = datetime.fromtimestamp(float(commit.author.time), 
                                    timezoneInfo).strftime(GIT_TIME_FORMAT)

        commitDict = {}
        commitDict["id"] = commit.hex
        commitDict["name"] = commit.author.name
        commitDict["email"] = commit.author.email
        commitDict["date"] = datetimeString
        commitDict["message"] = commit.message.strip(" \t\n\r")

        commits.append(commitDict)

    return commits

def makeGitIgnore(path):
    """Generates .gitignore file for Blendit project at given path"""
    
    content = (
        "# Blendit\n"
        "assets/\n"
        "*.blend\n"
        "*.blend*\n"
        "\n"
        "# Python\n"
        "# Byte-compiled / optimized / DLL files\n"
        "__pycache__/\n"
        "*.py[cod]\n"
        "*$py.class\n"
        "\n"
        "# C extensions\n"
        "*.so\n"
    )

    with open(os.path.join(path, ".gitignore"), "w") as file:
        file.write(content)

def configUser(repo, name, email):
    """Set user.name and user.email to the given Repo object"""

    repo.config["User.name"] = name
    repo.config["User.email"] = email