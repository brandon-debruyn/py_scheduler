'''
Program Description: This is a console-only schedule creator, with functionality 
					 using a sqlite3.

Author: brandonlee-db

'''
from datetime import *
import os
from datetime import *
import sqlite3
from prettytable import PrettyTable

# simple console clear function
clear = lambda: os.system('cls')

def add_task(schedule_name):

	# task name
	task_name = str(input("\nEnter your task name\n"))

	# task description (optional)
	description = str(input("Enter a task description (optional press ENTER to skip)\n"))

	# time start
	time_start_hours = float(input("Enter Start hour: (enter between 00 and 24)\n"))
	time_start_minutes = float(input("Enter Start Minutes: (enter between 00 and 59)\n"))

	# time end
	time_end_hours = float(input("Enter Finish hour: (enter between 00 and 24)\n"))
	time_end_minutes = float(input("Enter Finish minutes: (enter between 00 and 59)\n"))

	# connect to db
	conn = sqlite3.connect("schedule.db")
	c = conn.cursor()

	c.execute(f'''INSERT INTO {schedule_name}(time_start_hours, time_start_minutes, time_end_hours, time_end_minutes, name, description) VALUES(?,?,?,?,?,?)''', 
		(time_start_hours, time_start_minutes, time_end_hours, time_end_minutes, task_name, description))
	
	conn.commit()
	conn.close()

	clear()
	print("\nSuccess! Your Task was added...\n")

	# redisplay schedule
	view_schedule(schedule_name)

	# close db - user decision to add another task or view schedule
	new_or_continue = input("Do you want to add another task? Y / N")

	# if yes rerun func add_task else return to on_run
	if new_or_continue.lower() == "y":
		add_task(schedule_name)
	else:
		on_run()

def create_schedule():
	# get schedule name 
	get_schedule_name = str(input("\nEnter a Schedule Name to create(only one word names):"))

	# create schedule with selected name {get_schedule_name}
	conn = sqlite3.connect("schedule.db")
	c = conn.cursor()
	
	c.execute(f'''CREATE TABLE {get_schedule_name} (name_id INTEGER PRIMARY KEY, time_start_hours REAL NOT NULL, time_start_minutes REAL NOT NULL, time_end_hours REAL NOT NULL, time_end_minutes REAL NOT NULL, name TEXT NOT NULL, description TEXT)''')
	
	# clear command line
	clear()

	print(f"\nSuccess! {get_schedule_name} was created...\n")

	conn.commit()
	conn.close()

	# close db - continue to add task to {get_schedule_name}
	add_task_decision = input(f"Do you want to add a Task to {get_schedule_name}? ENTER Y / N\n")

	if add_task_decision.lower() == "y":
		add_task(get_schedule_name)

def view_schedule(schedule_name):
	# init PrettyTable
	schedule_table = PrettyTable()
	schedule_table.field_names = ["Task Name: ", "Task Description: ", "From: ", "To: "]

	# connect and create base layout for table
	conn = sqlite3.connect('schedule.db')
	c = conn.cursor()
	
	# select all columns and assign var to each
	# -----> Add checks for time to add 0 if entry is 0 <------------
	select_all_cols = c.execute(f"SELECT * FROM {schedule_name} ORDER BY time_start_hours")

	for col in c.fetchall():
		taskName = col[5]
		taskDesc = col[6]
		timeStartH = int(col[1])
		timeStartM = int(col[2])
		timeEndH = int(col[3])
		timeEndM = int(col[4])		

		# Fix time to be consistent accross 24 hour day span
		if not (timeStartH >= 10):
			timeStartH = "0" + str(timeStartH)	

		if not (timeStartM >= 10):
			timeStartM = "0" + str(timeStartM)
			
		if not (timeEndH >= 10):
			timeEndH = "0" + str(timeEndH)
			
		if not (timeEndM >= 10):
			timeEndM = "0" + str(timeEndM)
			

		_time_start = str(timeStartH) + ":" + str(timeStartM)
		_time_end = str(timeEndH) + ":" + str(timeEndM)

		# add rows to schedule table
		schedule_table.add_row([taskName, taskDesc, _time_start, _time_end])

	# return schedule table with table name
	print(f"Schedule Name: {schedule_name}")
	print(schedule_table)

	conn.commit()
	conn.close()

	# Add or Delete Task from current {schedule_name} table else return to main loop
	edit_current_table = input(f"Enter A - To add a task to {schedule_name}\nEnter D - To delete a task from {schedule_name}\nPress 'Enter' to return to Main Menu:\n")

	if edit_current_table.lower() == "a":
		add_task(schedule_name)
	elif edit_current_table.lower() == "d":
		delete_taskRow(schedule_name)
	elif edit_current_table == '':
		clear()
		on_run()
	else:
		clear()
		print("Sorry, Invalid input...")
		view_schedule(schedule_name)

def delete_schedule(schedule_name):
	# connect and create cursor
	conn = sqlite3.connect("schedule.db")
	c = conn.cursor()

	# schedule_name validation check in main loop -> no need for IF EXIST
	c.execute(f'''DROP TABLE {schedule_name}''')

	# no need for commit -> rather safe than sorry :>
	conn.commit()
	conn.close()

	# clear console -> return to loop
	clear()
	print("You have Succesfully deleted: ", schedule_name)

	on_run()
	
def delete_taskRow(schedule_name):	
	# get task name to be deleted 
	task_name = input("Enter the task name to be Deleted: ")

	# check if task exist in {schedule_name}
	if check_if_task_exist(schedule_name, task_name):
		# connect and create cursor to db
		conn = sqlite3.connect("schedule.db")
		c = conn.cursor()

		c.execute(f'''DELETE FROM {schedule_name} WHERE name=(?)''', (task_name,))

		conn.commit()
		conn.close()

		clear()
		print(f"Success... {task_name} was deleted.\n")
		view_schedule(schedule_name)
	else:
		clear()
		print("Sorry, that task does not exist...\n")	
		view_schedule(schedule_name)
	
def list_schedules():
	# list all tables in database - where tables = schedules
	conn = sqlite3.connect("schedule.db")
	c = conn.cursor()

	# get all tables
	c.execute('''SELECT name FROM sqlite_master WHERE type="table";''')
	list_schedules = c.fetchall()

	# get each table in list element + add element to pretty table for display
	get_tables = PrettyTable()
	get_tables.field_names = ["My Schedules"]

	for schedule in list_schedules:
		for i in schedule:
			get_tables.add_row([i])
	print(get_tables)

	conn.commit()
	conn.close()

def check_if_task_exist(schedule_name, schedule_task):
	# check if task exist in table
	conn = sqlite3.connect("schedule.db")
	c = conn.cursor()

	c.execute(f"SELECT count(*) FROM {schedule_name} WHERE name = ?", (schedule_task,))
	data = c.fetchone()[0]

	if not data == 0:
		return True
	else:
		return False
	
	conn.commit()
	conn.close()

def check_if_table_exist(schedule_name):
	# check if table exist in db
	conn = sqlite3.connect('schedule.db')
	c = conn.cursor()

	# count table -> for validity
	c.execute(f'''SELECT count(name) FROM sqlite_master WHERE type="table" AND name="{schedule_name}"''')
	
	# return bool if count == 1
	if c.fetchone()[0] == 1:
		return True
	else:
		return False

	conn.commit()
	conn.close()

def create_db():
	# creates database for application -> set to different python file on final
	conn = sqlite3.connect("schedule.db")
	conn.commit()
	conn.close()

def on_run():

	if not os.path.isfile("schedule.db"):
		create_db()

	# list Schedules
	list_schedules()

	# User Decision 
	init_input = input("\nPress C - To Create a new schedule.\nPress A - To Add a task to a schedule.\nPress V - to View a schedule.\nPress X - To delete a Schedule\n")

	if init_input.lower() == "c":
		# clear console
		clear()

		# initialize create_schedule()
		create_schedule()

	elif init_input.lower() == "a":
		# list all schedules
		clear()
		list_schedules()
		# get schedule to be added from user
		get_table_name = input("Enter the name of the schedule you want to add an Task to: ")

		# if check if table exist return True -> run add_task function else error
		if check_if_table_exist(get_table_name):
			# run add_task function
			view_schedule(get_table_name)
			add_task(get_table_name)
		else:
			# return back to on_run loop
			print("\nThat Table does not exit, please try again...\n")
			on_run()

	elif init_input.lower() == "v":
		# list all schedules
		clear()
		list_schedules()

		# get selected schedule from user
		get_table_name = input("Type in your selected Schedule: \n")

		# check if schedule exist in db
		if check_if_table_exist(get_table_name):
			clear()
			view_schedule(get_table_name)
		else:
			print("\nThat Table could not be found, please try again...\n")
			on_run()

	elif init_input.lower() == "x":
		# list all schedules
		clear()
		list_schedules()

		# get schedule name
		get_table_name = input("Enter the name of the schedule you want to DELETE: ")

		# check if schedule exist in db
		if check_if_table_exist(get_table_name):
			delete_schedule(get_table_name)
		else:
			# return back to on_run loop
			print("\nThat Table name could not be found, please try again...\n")
			on_run()

	else:
		clear()
		print("\nError, Enter a valid key...\n\n")
		on_run()

on_run()