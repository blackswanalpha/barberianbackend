import psycopg2

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
