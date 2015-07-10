HabiTrello
==========
[![Code Climate](https://codeclimate.com/repos/5548e8e86956801233001bdb/badges/d525bdbb4e765943c51e/gpa.svg)](https://codeclimate.com/repos/5548e8e86956801233001bdb/feed)

Usage
=====
```
$ python run.py -h
usage: run.py [-h] [--skip-todos] [--skip-dailies] [--skip-habits]

Sync HabitRPG and Trello tasks!

optional arguments:
  -h, --help      show this help message and exit
  --skip-todos    Skip processing Todos
  --skip-dailies  Skip processing Dailies
  --skip-habits   Skip processing Habits
```

Description
===========

As a user of HabitRPG and Trello, I long for the ability to "sync" the tasks between the two. 
I also use Trello for more of my day to day task management, so I want HabitRPG to be controlled from Trello. 
This python program will read the Trello cards in the board "Habit RPG" and tasks in Habit RPG itself to properly sync tasks, as well as determine if they've been completed or not.
If a Card exists in Trello but not in Habit RPG, it will be created in Habit RPG and it's task type will be determined by the list it is in.
If a Task exists in Habit RPG but not in Trello, a card will be added for the related task, in the list depending on the task type.
Each card in Trello has a checklist. For Dailies and Todos they simply have a box to mark the task Completed.
Habits have an Up and / or Down corresponding to the Habit in HabitRPG, and you simply have to mark the corresponding box.

Feature List
============
Currently Working:
 * Two way Sync
 * Up/Down Habits
 * Complete Todos
 * Complete Dailies
 * Label Habits for Up and/or Down

Instructions
============

First off, you need Python installed. You will also need py-trello and pyhabit to be installed.  
You can find those repositories on GitHub as well as in Pip.

To make sure all of the requirements are satisfied, run  
```
    sudo pip install -r requirements.txt
```

or your OS equivalent.

To use HabiTrello, first you need your API key and UUID from [HabitRPG](https://habitrpg.com/#/options/settings/api). Place them in the corresponding variables in habitrello/keys.py.

Next, you need your [Trello api keys](https://trello.com/1/appKey/generate). Place those in the habitrello/keys.py file, in the corresponding spaces.

Next, if you run python run.py, it will prompt you to walkthrough the steps to generate the OAuth tokens for Trello. After these are generated, they're printed out. You must then copy these and paste them in to habitrello/keys.py in the final two spots.

Then simply run  
```
python run.py
```

You can also pass the flags
```
    --skip-todos
    --skip-dailies
    --skip-habits
```
The flags each indicate whether or not to process the corresponding set of tasks. 
This is useful if you want them to be processed independently or you want to do a manual processing.  
Ideally, you would set up a timed task such as a CRON job to run every 5 minutes or so.
HabiTrello should create the board, lists, and populate them with your dailies, habits, and todos automatically
for you.

I would like to warn that this is largely still a Work In Progress. If you value your HabitRPG avatar, I would recommend against using this in its present state.

Credits
=======
[pyhabit](https://github.com/elssar/pyhabit)  
[py-trello](https://github.com/sarumont/py-trello) - I'm using my own fork because the API seems to be slightly outdated for some functionality I need
