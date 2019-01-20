import sqlite3
from uuid import uuid4
import random
from datetime import datetime
#from pyzbar.pyzbar import decode

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
		## add a new user into the database
		## if the user exists, then print some info,
		## return token for a new user
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

	def user_login(self, token):
		## check user token is valid of not
		scripts = "select token from users where token = (?)"
		token = self.execute_scripts(scripts, token)
		if token is not None:
			return True 
		## 
		print("Wrong token!")
		return False

	def create_event(self, organizer_id, event_name, venue_name,date_time, description):
		## 10 for pending; 1 for approve; 0 for reject;
		event_id = random.randint(1000, 9999)
		venue_id = random.randint(1000, 9999)
		scripts = "insert into events (event_id, organizer_id, event_name, venue_id, venue_name, date_time,  description, visible_status,total_attendee ) values (?,?, ?,?,?,?,?,1,0)"
		args = (event_id,  organizer_id, event_name, venue_id,  venue_name, datetime.now().strftime('%Y %b-%d %H:%m:%S'), description)
		self.conn.execute(scripts, args)
		self.conn.commit()

		## return event_id, event_name
		return (args[0], args[2])

	def generate_all_pending_events(self):
		stmt = 'select event_id, event_name from events where visible_status = 10'
		cursor = self.conn.execute(stmt)
		self.conn.commit()
		return cursor.fetchall()

	def generate_all_approved_events(self):
		stmt = 'select event_id, event_name from events where visible_status = 1'
		cursor = self.conn.execute(stmt)
		self.conn.commit()
		return cursor.fetchall()

	def register_for_event(self, userinput, user_token):
		event_id = userinput[-4:]
		action = userinput[1:9]
		print(event_id, action)
		if action == 'register':
			stmt = "insert into user_booking (event_id, user_id) values(?), (select user_id from users where token = (?))) "
			args = (event_id, user_token)
			self.conn.execute(stmt, args)
			self.conn.commit()

	def generate_events_of_user(self, token):
		## manage created events by this user_id
		stmt = 'select a.event_id from events a join users c on a.organizer_id = c.user_id where c.token = (?)'
		args = (token,)
		cursor = self.conn.execute(stmt, args)
		self.conn.commit()
		results = [str(max(x)) for x in cursor.fetchall()]
		if len(results):
			return results
		return 

	def admin_manage_events(self, user_token, userinput):
		stmt1 = 'select name from users where token= (?)'
		user_name = self.execute_scripts(stmt1, user_token)
		print(user_name)
		if user_name == 'root':
			event_id = userinput[-4:]
			args = None
			if 'approve' in userinput:
				visible_status = '1'
			elif 'reject' in userinput:
				visible_status = '0'

			stmt = 'update events set visible_status = (?) where event_id = (?)'
			args = (visible_status,event_id)
			self.conn.execute(stmt, args)
			self.conn.commit()
		else:
			print("Can't change admin")

	#def mark_attendance(self, qr_image, user_id):
		#return str(decode(qr_image)[0].data)[2:-1]




el = DB()
# el.setup()
# el.add_user('crazyethan')
# # el.execute_scripts('SELECT * FROM users where name = (?)', 'zzz686970')
# el.create_event('ethan', 'top secret.', 'floor 1','20180101110102', 'Beijing to roll out unlimited electronic subway tickets')
# el.create_event('cpf', 'teaching assistant.', 'floor 2','20180101110102', 'The commission added however that no refunds can be issued once the tickets are activated online.')

# el.create_event('yuqing', 'hydrogen bomb', 'floor 3','20180101110102', 'Luxury pet hotels thriving during Spring Festival')


