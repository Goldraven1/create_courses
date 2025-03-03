import psycopg2

bd = "hackathonusers"
def main():
    try:
        # пытаемся подключиться к базе данных
        conn= psycopg2.connect(dbname=bd, user='postgres', host='95.31.138.156', port='54320', password='111LZo0l4S7dzO0PXA3KOkasw2rcMtO46hY2FbUPxS')
        print('connect')
    except Exception as e:
        # в случае сбоя подключения будет выведено сообщение в STDOUT
        print(f'Can`t establish connection to database {e}')
        return
    

def CREATE():
    conn= psycopg2.connect(dbname='postgres',
    user='postgres', host='95.31.138.156', port='54320',
    password='111LZo0l4S7dzO0PXA3KOkasw2rcMtO46hY2FbUPxS')
    conn.autocommit = True 
    cur = conn.cursor()
    cur.execute(f'CREATE DATABASE {bd}')
    conn.commit()
    cur.close()
    conn.close()
    print(f"CREATE {bd}")



def destroyed():
    conn= psycopg2.connect(dbname='postgres',
    user='postgres', host='95.31.138.156', port='54320',
    password='111LZo0l4S7dzO0PXA3KOkasw2rcMtO46hY2FbUPxS')
    conn.autocommit = True 
    cur = conn.cursor()
    cur.execute("DROP DATABASE IF EXISTS hackathonusers;")
    conn.commit()
    conn.close()
    cur.close()
    print(f"destroyed {bd}")



def tables():

    #1 Таблица Users:
    cur.execute("""CREATE TABLE Users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(50) NOT NULL,
        email VARCHAR(100) NOT NULL,
        password VARCHAR(512) NOT NULL,
        role VARCHAR(50) NOT NULL,
        phone_number VARCHAR(20),
        registration_date TIMESTAMP NOT NULL DEFAULT NOW(),
        image_path VARCHAR(255),
        gender VARCHAR(10),
        confirmed BOOLEAN);
        """
    )

    #2 Таблица Categories:
    cur.execute("""CREATE TABLE Categories (
        category_id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        description TEXT);
                
        """
    )

    #3 Таблица Courses:
    cur.execute("""CREATE TABLE Courses (
        course_id SERIAL PRIMARY KEY,
        category_id INT REFERENCES Categories(category_id),
        title VARCHAR(255) NOT NULL,
        description TEXT,
        price DECIMAL(10, 2) NOT NULL,
        duration INT,
        pages INT,
        photos VARCHAR(255),
        videos VARCHAR(255)),
        levls VARCHAR(64),;
        """
    )

    #4 Таблица Materials:
    cur.execute("""CREATE TABLE Materials (
        material_id SERIAL PRIMARY KEY,
        course_id INT REFERENCES Courses(course_id),
        category_id INT REFERENCES Categories(category_id),
        title VARCHAR(255) NOT NULL,
        type VARCHAR(100),
        content TEXT);
        """
    )

    #5 Таблица Orders:
    cur.execute("""CREATE TABLE Orders (
        order_id SERIAL PRIMARY KEY,
        user_id INT REFERENCES Users(id),
        course_id INT REFERENCES Courses(course_id),
        order_date TIMESTAMP NOT NULL DEFAULT NOW(),
        status VARCHAR(50) DEFAULT 'pending');
        """
    )

    #6 Таблица Reviews:
    cur.execute("""CREATE TABLE Reviews (
        review_id SERIAL PRIMARY KEY,
        user_id INT REFERENCES Users(id),
        course_id INT REFERENCES Courses(course_id),
        rating INT,
        comment TEXT);
        """
    )

    #7 Таблица User_Progress:
    cur.execute("""CREATE TABLE User_Progress (
        user_progress_id SERIAL PRIMARY KEY,
        user_id INT REFERENCES Users(id),
        course_id INT REFERENCES Courses(course_id),
        lesson_id INT,
        completed BOOLEAN);
        """
    )

    #8 Таблица Messages:
    cur.execute("""CREATE TABLE Messages (
        message_id SERIAL PRIMARY KEY,
        sender_id INT REFERENCES Users(id),
        receiver_id INT REFERENCES Users(id),
        message_content TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
        """
    )

    #9 Таблица Lessons:
    cur.execute("""CREATE TABLE Lessons (
        lesson_id SERIAL PRIMARY KEY,
        course_id INT REFERENCES Courses(course_id),
        title VARCHAR(255) NOT NULL,
        description TEXT,
        duration INT,
        content TEXT);
        """
    )

    #10 Таблица Payments:
    cur.execute("""CREATE TABLE Payments (
        payment_id SERIAL PRIMARY KEY,
        order_id INT REFERENCES Orders(order_id),
        payment_date TIMESTAMP NOT NULL DEFAULT NOW(),
        amount DECIMAL(10, 2) NOT NULL,
        payment_method VARCHAR(100));
        """
    )


    #11 Таблица :billing_address
    cur.execute("""CREATE TABLE billing_address (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES Users(id),  
    order_id INT REFERENCES Orders(order_id),  
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    username VARCHAR(50),
    email VARCHAR(100),
    address VARCHAR(255),
    address2 VARCHAR(255),
    country VARCHAR(100),
    zip VARCHAR(20),
    payment_method VARCHAR(100),
    name_on_card VARCHAR(100),
    credit_card_number VARCHAR(20),
    expiration_date VARCHAR(10),
    payment_amount DECIMAL(10, 2),  
    payment_date TIMESTAMP,         
    payment_status VARCHAR(50)      
);

        """
    )

    




try:
    CREATE()
    print("first create")
    conn= psycopg2.connect(dbname=bd,
    user='postgres', host='95.31.138.156', port='54320',
    password='111LZo0l4S7dzO0PXA3KOkasw2rcMtO46hY2FbUPxS')
    cur = conn.cursor()
    tables()
    conn.commit()
    conn.close()
    cur.close()
    print("table created")

except:
    print("the table has already been created. deletion")
    destroyed()
    CREATE()
    conn= psycopg2.connect(dbname=bd,
    user='postgres', host='95.31.138.156', port='54320',
    password='111LZo0l4S7dzO0PXA3KOkasw2rcMtO46hY2FbUPxS')
    cur = conn.cursor()
    tables()
    conn.commit()
    conn.close()
    cur.close()
    print("table created")



