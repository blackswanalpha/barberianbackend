from sqlalchemy import create_engine, Column, Integer, String, MetaData, Table, text
from sqlalchemy.orm import sessionmaker, declarative_base
import datetime

def test_sqlalchemy_connection():
    """Test SQLAlchemy connection to PostgreSQL"""
    print("Testing SQLAlchemy connection to PostgreSQL...")

    try:
        # Create connection URL
        db_url = "postgresql://barberian_user:barberian_password@localhost:5432/barberian_db"

        # Create engine
        engine = create_engine(db_url)

        # Test connection
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"PostgreSQL version via SQLAlchemy: {version}")

        # Create metadata and base
        metadata = MetaData()
        Base = declarative_base()

        # Define a model
        class TestModel(Base):
            __tablename__ = 'sqlalchemy_test_table'

            id = Column(Integer, primary_key=True)
            name = Column(String(100), nullable=False)

            def __repr__(self):
                return f"<TestModel(id={self.id}, name='{self.name}')>"

        # Create table
        Base.metadata.create_all(engine)
        print("Created sqlalchemy_test_table successfully")

        # Create session
        Session = sessionmaker(bind=engine)
        session = Session()

        # Insert data
        test_entry = TestModel(name="SQLAlchemy Test Entry")
        session.add(test_entry)
        session.commit()
        print(f"Inserted test data with ID: {test_entry.id}")

        # Query data
        results = session.query(TestModel).all()
        print(f"Query results: {results}")

        # Clean up
        Base.metadata.drop_all(engine)
        print("Dropped sqlalchemy_test_table successfully")

        print("SQLAlchemy connection test completed successfully!")

        # Close session
        session.close()

        print("SQLAlchemy connection test completed successfully!")
        return True

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_sqlalchemy_connection()
