# jtodo
Todo App made in Python with the Curses Library. Inspired by Clickup.
Menu List navigation is done with Vim keys (j to scroll down; k to scroll up)

# Window Stack
The Window Stack is structured as follows:
```
Home
  Task List
    Task
      Comments
      SubTasks
        ...
```

The Todo App's data is stored persistently in and Sqlite3 Database

DB Schema:
```
tblTaskList
  TaskListID    : Integer  : Primary Key
  TaskListName  : Text     : Required

tblTask
  TaskID        : Integer  : Primary Key
  TaskListID    : Integer  : Optional
  ParentTaskID  : Integer  : Optional
  TaskName      : Text     : Required
  TaskDate      : Text     : Required
  TaskStatus    : Integer  : Required
  TaskPriority  : Integer  : Required
  TaskDesc      : Text     : Required

tblComment
  CommentID     : Integer  : Primary Key
  TaskID        : Integer  : Required
  CommentDate   : Text     : Required
  CommentBody   : Text     : Required
```
