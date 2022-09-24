# Blendit (Blender + Git)

A [Git](https://git-scm.com/) integration for [Blender](https://www.blender.org/).

![Blendit](https://raw.githubusercontent.com/imaginelenses/blendit/main/splash.png)

Blendit brings ***Version Control*** to Blender.

## Version Control
Version Control helps you track different versions of your project. Working on a project overtime you may want to keep track of which changes were made, by whom, and when those changes were made.

Version control has been standard practice in software development to keep track of changes mode to source code for years now. However, when it comes to working with files other than textual files you usually out of luck.

While Git and other Version Control Systems (VCS) can track `.blend` (binary) files it does not make much sense as they are designed for textual files.

That said, according to [Sybren](https://github.com/sybrenstuvel/) on [Blender Stack Exchange](https://blender.stackexchange.com/a/108186/154740), Blender Institute uses [Subversion](https://subversion.apache.org/).
> At the Blender Institute / Blender Animation Studio we use Subversion for our projects. It works fine for blend files, but you have to make sure they are not compressed. Compression can cause the entire file to be different when only a single byte changed, whereas in the uncompressed blend file only that one byte will differ. As a result, binary diffs will be much smaller, and your repository will be faster to work with.

## How does Blendit work?

Instead of tracking the `.blend` (binary) files itself, Blendit tracks the *changes* you make to the `.blend` file in real time. It does so by keeping track of the python commands, from the [Blender API](https://docs.blender.org/api/current/index.html), used to make changes.

Each time you open a Blendit project, it regenerates the `.blend` files. This means you can delete the `.blend` file and still retain the project.

This way we only track a textual (`.py`) file as Git was intended to be used. 

In theory the size of the entire project should be lower than using any other VSC.

## Getting Started

1. Download Blendit `.zip` file from [here](https://github.com/imaginelenses/blendit/archive/refs/tags/v0.1.0-alpha.zip).

2. Install Blendit [Application Template](https://docs.blender.org/manual/en/latest/advanced/app_templates.html#app-templates).
        
   
   - Open Blender and click the `Blender Menu ▸ Install Application Template` submenu

        <img class="img-fluid mb-3 rounded shadow-lg" src="https://github.com/imaginelenses/blenditSite/blob/main/src/assets/installTemp.png" alt="Blender Menu">

   - Select the downloaded `.zip` file.

3. Blendit Application templates can be selected from the splash screen or `File ▸ New` submenu.

    <img class="img-fluid mb-3 rounded shadow-lg" src="https://github.com/imaginelenses/blenditSite/blob/main/src/assets/openBlendit.png" alt="Blender Menu">

    **Note**: The first time you open Blendit it will take a some time to load.

    **For Windows**: Run Blender as administrator the first time you open Blendit.

### New Project

- Create a new Project from the splash screen or `File ▸ New Project` submenu.

    <img class="img-fluid mb-3 rounded shadow-lg" src="https://github.com/imaginelenses/blenditSite/blob/main/src/assets/fileMenuNewProject.png" alt="Blender Menu">

- Select a *location* to save the project and type the *name* of the project in the bottom.

    <img class="img-fluid mb-3 rounded shadow-lg" src="https://github.com/imaginelenses/blenditSite/blob/main/src/assets/newProject.png" alt="Blender Menu" loading="lazy">

- Provide your *username* and *email*, on the right, to keep track of who made what changes.
    
    **Note**: If you have use Git and have a global git config file, theses details are auto-filled.


### Open Project

- Open a Project from the splash screen or `File ▸ Open Project` submenu.

    <img class="img-fluid mb-3 rounded shadow-lg" src="https://github.com/imaginelenses/blenditSite/blob/main/src/assets/fileMenuOpenProject.png" alt="Blender Menu" loading="lazy">
    
- Locate the project you want to open.
    
    <img class="img-fluid mb-3 rounded shadow-lg" src="https://github.com/imaginelenses/blenditSite/blob/main/src/assets/openProject.png" alt="Blender Menu" loading="lazy">

    **Note**: The *username* and *email* details shown are of the previous *commiter* - if that isn't you do change it.

### Commits

- Commits are process of saving snapshots of your project.
- Create a new Commit from the *Blendit* panel in the *Properties* area, under *Active Tools and Workspace settings* tab.

    <img class="img-fluid mb-3 rounded shadow-lg" src="https://github.com/imaginelenses/blenditSite/blob/main/src/assets/blenditPanel.png" alt="Blender Menu" loading="lazy">

- Each Commit requires an accompanying *Commit Message* describing the commit

### Revert Commit

- You can go back time by reverting to a Commit from the past.
- Revert to a Commit by first selecting it from the list of Commits under the *Branch* subpanel and clicking `Revert to Commit` button
  
    <img class="img-fluid mb-3 rounded shadow-lg" src="https://github.com/imaginelenses/blenditSite/blob/main/src/assets/revertCommit.png" alt="Blender Menu" loading="lazy">
  
### Branches

- Branches are the forks in the road, so to speak.
- Create a new Branch by clicking `+` button next to the Branches dropdown in the *Branches* subpanel.

    <img class="img-fluid mb-3 rounded shadow-lg" src="https://github.com/imaginelenses/blenditSite/blob/main/src/assets/newBranch.png" alt="Blender Menu" loading="lazy">

- Change to that Branch by selecting it from the Branches list dropdown.

    <img class="img-fluid mb-3 rounded shadow-lg" src="https://github.com/imaginelenses/blenditSite/blob/main/src/assets/branchList.png" alt="Blender Menu" loading="lazy">

Here is an extract from the [About Git](https://git-scm.com/about) website. While this is written targeting *Software Development*, most of these points are applicable to *creative workflows* too.

> - **Frictionless Context Switching.** Create a branch to try out an idea, commit a few times, switch back to where you branched from, apply a patch, switch back to where you are experimenting, and merge it in.
> - **Role-Based Codelines.** Have a branch that always contains only what goes to production, another that you merge work into for testing, and several smaller ones for day to day work.
> - **Feature Based Workflow.** Create new branches for each new feature you're working on so you can seamlessly switch back and forth between them, then delete each branch when that feature gets merged into your main line.
> - **Disposable Experimentation.** Create a branch to experiment in, realize it's not going to work, and just delete it - abandoning the work—with nobody else ever seeing it (even if you've pushed other branches in the meantime).
> <img src="https://git-scm.com/images/about/branches@2x.png" alt="Git Branching" width="500">

### Assets

- All assets like materials, textures, etc. should be stored within the `/assets` folder within the project.
- **Note:** Changes made to the `/assets` folder is ***not***  tracked by Blendit.

## Dependencies

- Blendit uses [pygit2](https://github.com/libgit2/pygit2) for *Git Plumbing*.
- pygit2 is installed automatically using pip when you first open Blendit. 
- Therefore Blendit requires an internet connection when you open it for the first time.

## License

Like Blender and Git, Blendit is also licensed under the GNU General Public License. 

See [Full License](https://github.com/imaginelenses/blendit/blob/main/LICENSE).


#
*Splash screen image was made following [CG Geek's tutorial](https://youtu.be/72LPW4S8bns).*
