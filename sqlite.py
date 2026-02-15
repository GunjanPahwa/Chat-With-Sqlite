import sqlite3 #allows python to interact with SQLite databases
##connect to sqlte
connection=sqlite3.connect("student.db") #connecting to a database file named student.db
#if the file does not exist then sqlite wil create it automatically
#The variable connection represents the connection object, which is used to interact with the database

#create a cursor object to insert, record, create table
cursor=connection.cursor()
#A cursor is like a handle that lets you execute SQL commands on the database.

#create the table
table_info="""
create table STUDENT(NAME VARCHAR(25), CLASS VARCHAR(25),
SECTION VARCHAR(25), MARKS INT)
"""
cursor.execute(table_info)

##Insert some more records
cursor.execute('''Insert Into STUDENT values('Krish','Data Science','A',90)''')
cursor.execute('''Insert Into STUDENT values('John','Data Science','B',100)''')
cursor.execute('''Insert Into STUDENT values('Mukesh','Data Science','A',86)''')
cursor.execute('''Insert Into STUDENT values('Jacob','DEVOPS','A',50)''')
cursor.execute('''Insert Into STUDENT values('Dipesh','DEVOPS','A',35)''')

##Display all the recors
print("The inserted records are")
data=cursor.execute('''Select * from STUDENT''')
for row in data:
    print(row)

#Commit your changes in the database
connection.commit() #This saves all the changes made to the database.
connection.close()
