import psycopg2
from psycopg2 import sql

def test_postgres_connection():
    """Test direct PostgreSQL connection"""
    print("Testing direct PostgreSQL connection...")
    
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            dbname="barberian_db",
            user="barberian_user",
            password="barberian_password",
            host="localhost",
            port="5432"
        )
        
        # Create a cursor
        cur = conn.cursor()
        
        # Execute a test query
        cur.execute("SELECT version();")
        
        # Fetch the result
        version = cur.fetchone()
        print(f"PostgreSQL version: {version[0]}")
        
        # Create a test table
        cur.execute(
            sql.SQL("""
            CREATE TABLE IF NOT EXISTS test_table (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
        )
        conn.commit()
        print("Created test_table successfully")
        
        # Insert data
        cur.execute(
            sql.SQL("""
            INSERT INTO test_table (name) VALUES (%s) RETURNING id
            """),
            ["Test entry"]
        )
        inserted_id = cur.fetchone()[0]
        conn.commit()
        print(f"Inserted test data with ID: {inserted_id}")
        
        # Query data
        cur.execute("SELECT * FROM test_table")
        rows = cur.fetchall()
        print(f"Query results: {rows}")
        
        # Clean up
        cur.execute("DROP TABLE test_table")
        conn.commit()
        print("Dropped test_table successfully")
        
        # Close cursor and connection
        cur.close()
        conn.close()
        
        print("PostgreSQL connection test completed successfully!")
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    # Test direct PostgreSQL connection
    test_postgres_connection()
