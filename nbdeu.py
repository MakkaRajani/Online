():
    cursor=mysql.connection.cursor()
    cursor.execute('select count(*) from admin')
    count=cursor.fetchone()[0]
    cursor.close()
    if(count>=0):
        return 'admin already registered'
    
