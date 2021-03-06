#!/usr/bin/python

import MySQLdb
import cgi, cgitb


import optparse
# Get options
opt = optparse.OptionParser()
opt.add_option("-U", "--user", 
               action="store", 
               type="string", 
               help="user account to use for login", 
               dest="user")
opt.add_option("-P", "--password", 
               action="store", 
               type="string", 
               help="password to use for login", 
               dest="password")
opt.add_option("-d", "--dbact", 
               action="store", 
               type="string", 
               help="kind of db action to be affected", 
               dest="dbact")
opt.add_option("-D", "--dbname", 
               action="store", 
               type="string", 
               help="name of db to be affected", 
               dest="dbname")
opt.add_option("-t", "--tbact", 
               action="store", 
               type="string", 
               help="kind of table action to be affected", 
               dest="tbact")
opt.add_option("-Q", "--tbdbact", 
               action="store", 
               type="string", 
               help="name of database containing table to be affected", 
               dest="tbdbname")
opt.add_option("-N", "--tbname", 
               action="store", 
               type="string", 
               help="name of table to be affected", 
               dest="tbname")
opt.add_option("-q", "--qact", 
               action="store", 
               type="string", 
               help="kind of query to affect", 
               dest="qact")
opt.add_option("-Z", "--qdbname", 
               action="store", 
               type="string", 
               help="database to be used for query", 
               dest="qdbname")
opt.add_option("-Y", "--qtbname", 
               action="store", 
               type="string", 
               help="table to be used for query", 
               dest="qtbname")
opt.add_option("-c", "--columns", 
               action="store", 
               type="string", 
               help="columns to be used in query", 
               dest="columns")    
opt.add_option("-v", "--values", 
               action="store", 
               type="string", 
               help="values to be used in query", 
               dest="values")
opt, args = opt.parse_args()

# form = cgi.FieldStorage()
# user = form.getvalue('user')
# password = form.getvalue('password')

# dbact = form.getvalue('dbact')
# dbname = form.getvalue('dbname')

# tbact = form.getvalue('tbact')
# tbdbname = form.getvalue('tbdbname')
# tbname = form.getvalue('tbname')

# qact = form.getvalue('qact')
# qdbname = form.getvalue('qdbname')
# qtbname = form.getvalue('qtbname')
# columns = form.getvalue('columns')
# values = form.getvalue('values')


def connectNoDB(user, password):
    """Creates a database connection and returns the cursor.  Host is hardwired to 'localhost'."""
    try:
        host = 'localhost'
        mydb = MySQLdb.connect(host, user, password)
        cur = mydb.cursor()
        return cur
    except MySQLdb.Error:
        print "There was a problem in connecting to the database.  Please ensure that the database exists on the local host system."
        raise MySQLdb.Error
    except MySQLdb.Warning:
        pass

def connection(user, password, database):
    """Creates a database connection and returns the cursor.  Host is hardwired to 'localhost'."""
    try:
        host = 'localhost'
        mydb = MySQLdb.connect(host, user, password, database)
        cur = mydb.cursor()
        return cur
    except MySQLdb.Error:
        print "There was a problem in connecting to the database.  Please ensure that the database exists on the local host system."
        raise MySQLdb.Error
    except MySQLdb.Warning:
        pass



def execute(statement, cursor, type):
    """Attempts execution of the statement resulting from MySQLStatement.form()."""
    while True:
        try:
            cursor.execute(statement)
            if type == "select":
                # Run query
                output = cursor.fetchall()
                results = ""
                data = ""
                for record in output:
                    for entry in record: 
                        data = data + '\t' + str(entry) 
                    data = data + "\n"
                results = results + data + "\n"
            elif type == "insert":
                results = "Your information was inserted with the following SQL statement: %s;" %(statement)
            elif type == "create-db":
                results = "The following statement has been processed to ensure the database exists: %s;" %(statement)
            elif type == "create-tb":
                results = "The following statement has been processed to ensure the table exists: %s;" %(statement)
            elif type == "drop-db":
                results = "The following statement has been processed to ensure the removal of the database: %s;" %(statement)
            elif type == "drop-tb":
                results = "The following statement has been processed to ensure the removal of the table: %s;" %(statement)
            return results


        # OperationalError
        except MySQLdb.Error, e :
            # Generic error-handling for the sake of brevity.
            # Refer to the chapter on exception-handling for a
            # more complete implementation.
            print "Some of the information you have passed is not valid.  Please check it before trying to use this program again."
            print "The exact error information reads as follows: %s" %(e)
            raise
            
        except MySQLdb.Warning:
            pass                

        except Warning:
            pass                


class HTMLPage:
    def __init__(self):
        """Creates an instance of a web page object."""
        self.Statement = []

    def header(self):
        """Prints generic HTML header with title of application."""
        output = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Frameset//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-frameset.dtd"> 
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en" dir="ltr"> 
<head> 
<title>PyMyAdmin 0.001</title> 
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" /> 
</head> 
<body> 
"""
        return output


    def footer(self):
        """Print generic HTML footer to ensure every page closes neatly."""
        output = """
</body> 
</html> 
"""
        return output

    def body(self):
        output = ""
        title = "<h1>PyMyAdmin Results</h1>"
        output = output + title + "<br>" + self.message
        return output

    def message(self, message):
        self.message = message
            
    def page(self):
        """Creates webpage from output."""
        header = self.header()
        body = self.body()
        footer = self.footer()
        output = header + body + footer
        return output
            


def dbaction(act, name, cursor):
    if act == "create":
        statement = "CREATE DATABASE IF NOT EXISTS %s" %(name)
        output = execute(statement, cursor, 'create-db')
    elif act == "drop":
        statement = "DROP DATABASE IF EXISTS %s" %(name)        
        output = execute(statement, cursor, 'drop-db')
    else:
        output = "Bad information."
    return output

def tbaction(act, db, name, columns, types, user, password):
    cursor = connection(user, password, db)

    if act == "create":
        tname = name + "("
        columns = columns.split(',')
        types = types.split(',')
        for i in xrange(0, len(columns)):
            col = columns[i].strip()
            val = types[i].strip()
            tname = tname + col + " " + val
            if i == len(columns)-1:
                tname = tname + ")"
            else:
                tname = tname + ", "
        statement = "CREATE TABLE IF NOT EXISTS %s" %(tname)
        results = execute(statement, cursor, 'create-tb')
    elif act == "drop":
        statement = "DROP TABLE IF EXISTS %s" %(name)       
        results = execute(statement, cursor, 'drop-tb')
    return results

def qaction(qact, db, tb, columns, values, user, password):
    cursor = connection(user, password, db)

    tname = tb + "("
    columns = columns.split(',')
    values = values.split(',')
    cols = ""
    vals = ""
    for i in xrange(0, len(columns)):
        col = columns[i].strip()
        val = values[i].strip()
        cols = cols + col
        vals = vals + "'" + val + "'"
        if i != len(columns)-1:
            cols = cols + ", "
            vals = vals + ", "
    if qact == "select":
        statement = "SELECT * FROM %s WHERE %s = %s" %(tb, cols, vals)
        results = execute(statement, cursor, 'select')        
    elif qact == "insert":
        statement = "INSERT INTO %s (%s) VALUES (%s)" %(tb, cols, vals)
        results = execute(statement, cursor, 'insert')
    return results


def main():
    """The main function creates and controls the MySQLStatement instance in accordance with the user's input."""
    output = ""

    while 1:
        try:
            cursor = connectNoDB(opt.user, opt.password)
            authenticate = 1
        except:
            output = "Bad login information.  Please verify the username and password that you are using before trying to login again."
            authenticate = 0

        if authenticate == 1:
            errmsg = "You have not specified the information necessary for the action you chose.  Please check your information and specify it correctly in the dialogue."

            if opt.dbact is not None:
                output = dbaction(opt.dbact, opt.dbname, cursor)
            elif opt.tbact is not None:
                output = tbaction(opt.tbact, opt.tbdbname, opt.tbname, opt.columns, opt.values, opt.user, opt.password)
            elif opt.qact is not None:
                output = qaction(opt.qact, opt.qdbname, opt.qtbname, opt.columns, opt.values, opt.user, opt.password)
            else: 
                output = errmsg

        printout = HTMLPage()
        printout.message(output)
        output = printout.page()

        print output
        break

if __name__ == '__main__':
    main()