HabiTrello
==========

As a user of HabitRPG and Trello, I long for the ability to "sync" the tasks between the two. I also use Trello for more of my day to day task management, so I want HabitRPG to be controlled from Trello. This python script will read the Trello cards in the "Habit RPG" board and the "Dailies", "Habits", and "Todos" lists to determine if a user has finished a daily, habit, or todo. If a card is present, it is assume to be uncomplete. If it isn't there, or if an entire list is closed, or the entire board, then the tasks at each level are considered complete. 

Credits
=======
py-trello - https://github.com/sarumont/py-trello
py-habit - https://github.com/elssar/pyhabit
