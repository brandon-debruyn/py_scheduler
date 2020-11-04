import sqlite3

def initialize_db():
	# initialize db on program start
	conn = sqlite3.connect("schedule.db")
	c = conn.cursor()

def create_table(schedule_name):
	# create table
	conn = sqlite3.connect("schedule.db")
	c = conn.cursor()

	c.execute(f'''CREATE TABLE {schedule_name}
					(id INTEGER PRIMARY KEY AUTOINCREMENT, time_start REAL NOT NULL, time_end REAL NOT NULL, name TEXT NOT NULL, description TEXT)''')

	conn.commit()
	conn.close()
	print(f"Success! {schedule_name} was created...")

def disconnect_db():
	# save and close db
	conn.commit()
	conn.close()