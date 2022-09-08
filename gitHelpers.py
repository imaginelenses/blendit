import os
from io import StringIO

from dulwich import porcelain as git
from dulwich.errors import NotGitRepository

def getCommits(path):
    """Returns a list of dicts of commits"""
    output = StringIO()

    try:
        git.log(path, outstream=output)
    except NotGitRepository:
        return []

    commits = []
    commitsStr = output.getvalue().split("--------------------------------------------------")
    for commit in commitsStr:
        if not commit:
            continue

        commitDict = {}
        pairs = commit.split("\n")
        for pair in pairs:
            if not pair:
                continue
            
            split = pair.split(": ", 1)
            length = len(split)
            if length == 2:
                commitDict[split[0].lower()] = split[1].strip(" \t\n\r")
            elif length == 1:
                commitDict["message"] = pair

        commits.append(commitDict)

    output.close()

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
    """Set user.name and user.email to the given Dulwich Repo object"""

    config = repo.get_config()
    config.set(("user"), "name", name)
    config.set(("user"), "email", email)
    config.write_to_path(config.path)
    repo.close()