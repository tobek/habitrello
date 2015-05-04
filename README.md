HabiTrello
==========

As a user of HabitRPG and Trello, I long for the ability to "sync" the tasks between the two. I also use Trello for more of my day to day task management, so I want HabitRPG to be controlled from Trello. This python script will read the Trello cards in the "Habit RPG" board and the "Dailies", "Habits", and "Todos" lists to determine if a user has finished a daily, habit, or todo. If a card is present, it is assumed to be incomplete. If it isn't there, or if an entire list is closed, or the entire board, then the tasks at each level are considered complete. 

Instructions
============

To make sure all of the requirements are satisfied, run
  sudo pip install -r requirements.txtx

To use HabiTrello, first you need your API key and UUID from [HabitRPG](https://habitrpg.com/#/options/settings/api). Place them in the corresponding variables in keys.py.

Next, you need your [Trello api keys](https://trello.com/1/appKey/generate). Place those in the keys.py file, in the corresponding spaces.

Next, if you run python habitrello.py, it will prompt you to walkthrough the steps to generate the OAuth tokens for Trello. After these are generated, they're printed out. You must then copy these and paste them in to keys.py in the final two spots.

Then simply run python habitrello.py  
Ideally, you would set up a timed task such as a Cron job to run just before midnight.  
HabiTrello should create the board, lists, and populate them with your dailies, habits, and todos automatically
for you.

I would like to warn that this is largely still a Work In Progress. If you value your HabitRPG avatar, I would recommend against using this in its present state.

Credits
=======
[py-habit](https://github.com/elssar/pyhabit) - I'm currently using my own fork of this
because it's old and doesn't appear to be maintained.
[py-trello](https://github.com/sarumont/py-trello) - Additionally using my own fork
