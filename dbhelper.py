import sqlite3
from uuid import uuid4

class DB:

	def __init__(self, dbname="telegram_bot.db"):
		self.dbname = dbname
		self.conn = sqlite3.connect(dbname)

	def setup(self):
		file = open('Scripts/sql_scripts/schema.sql', 'r').read()
		# tblstmt = "CREATE TABLE if not exists users (user_id integer primary key AUTOINCREMENT, name varchar (255) not null, token varchar(100));"
		# eventstmt = "CREATE TABLE if not exists events (event_id integer primary key AUTOINCREMENT, title varchar(255) not null, venue varchar(255), date_slot datetime not null, time_slot time not null, organiser varchar (255) not null, description varchar(255), status int not null, cur_attendance integer);" 
		# attendstmt = "CREATE TABLE if not exists attendance(user_id varchar(255) not null, event_id varchar(255) not null, user_status integer);"
		cur = self.conn.cursor()
		cur.executescript(file)
		# self.conn.execute(eventstmt)
		# self.conn.execute(attendstmt)
		self.conn.commit()

	def execute_scripts(self, scripts, parameter):
		args = (parameter,)
		cursor = self.conn.execute(scripts, args)
		self.conn.commit()
		return cursor.fetchone()

			# def delete_item(self, item_text, owner):
	# 	stmt = "DELETE FROM items WHERE description = (?) AND owner = (?)"
	# 	args = (item_text, owner )
	# 	self.conn.execute(stmt, args)
	# 	self.conn.commit()

	def add_user(self, name):
		scripts = "select * from users where name = (?)"
		user = self.execute_scripts(scripts, name)

		#check if user is not none and hashed+salted input = stored password
		if user is not None:
			print("This user is already registered!")
			#Issues a token
		else:
			stmt = "INSERT INTO users (user_id, name, token) VALUES (null, ?,?)"
			args = (name, str(uuid4())[:8])
			self.conn.execute(stmt, args)
			self.conn.commit()
			return args[1]

	def create_event(self, title, date, time, ):
		pass

	def generate_all_approved_events(self):
		# stmt = 'select title, date, time, venue, description,  from events values'
		stmt = 'select * from events'
		cursor = self.conn.execute(stmt)
		self.conn.commit()
		return crusor.fetchall()




el = DB()
# el.setup()
# el.add_user('crazyethan')
# el.execute_scripts('SELECT * FROM users where name = (?)', 'zzz686970')
