from __init__ import CURSOR, CONN
from department import Department
from employee import Employee


class Review:

    # Dictionary of objects saved to the database.
    all = {}
    def __init__(self, year, summary, employee_id, id=None):
        self.id = id
        self.year = year
        self.summary = summary
        self.employee_id = employee_id
    @property
    def employee_id(self):
        return self._employee_id
    @employee_id.setter
    def employee_id(self, employee_id):
        employee_exists = CURSOR.execute("SELECT id FROM employees WHERE id = ?", (employee_id,)).fetchone()
        if not employee_exists:
            raise ValueError(f"Employee with id {employee_id} does not exist.")
        self._employee_id = employee_id
    @property
    def year(self):
        return self._year
    
    @year.setter
    def year(self,year):
        if isinstance(year, int) and year >= 2000:
            self._year = year
        else:
            raise ValueError("expected integer greater than or equal to 2000") 
    @property
    def summary(self):
        return self._summary
    @summary.setter
    def summary(self, summary):
        if not summary or len(summary) < 0:
            raise ValueError("summary must not be empty")
        self._summary = summary

    def __repr__(self):
        return (
            f"<Review {self.id}: {self.year}, {self.summary}, "
            + f"Employee: {self.employee_id}>"
        )

    @classmethod
    def create_table(cls):
        """ Create a new table to persist the attributes of Review instances """
        sql = """
            CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY,
            year INT,
            summary TEXT,
            employee_id INTEGER,
            FOREIGN KEY (employee_id) REFERENCES employee(id) ON DELETE CASCADE) 
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        """ Drop the table that persists Review  instances """
        sql = """
            DROP TABLE IF EXISTS reviews;
        """
        CURSOR.execute(sql)
        CONN.commit()

    def save(self):
        """ Insert a new row with the year, summary, and employee id values of the current Review object.
        Update object id attribute using the primary key value of new row.
        Save the object in local dictionary using table row's PK as dictionary key"""
        if self.id is None:
            CURSOR.execute('''
                INSERT INTO reviews (year, summary, employee_id)
                VALUES (?, ?, ?)
            ''', (self.year, self.summary, self.employee_id))
            CONN.commit()
            self.id = CURSOR.lastrowid
        else:
            CURSOR.execute('''
                UPDATE reviews
                SET year = ?, summary = ?, employee_id = ?
                WHERE id = ?
            ''', (self.year, self.summary, self.employee_id, self.id))
            CONN.commit()
        Review.all[self.id] = self

    @classmethod
    def create(cls, year, summary, employee_id, id=None):
        """ Initialize a new Review instance and save the object to the database Return the new instance """
        review = cls(year, summary, employee_id)
        review.save()
        return review
    @classmethod
    def instance_from_db(cls, row):
        """Return an Review instance having the attribute values from the table row."""
        # Check the dictionary for  existing instance using the row's primary key
        review = cls.all.get(row[0])
        if review:
            review.year = row[1]
            review.summary = row[2]
            review.employee_id = row[3]
        else:
            review = cls(row[1], row[2], row[3])
            review.id = row[0]
            cls.all[review.id] = review
        return review
   

    @classmethod
    def find_by_employee_id(cls, employee_id):
        query = "SELECT *  FROM reviews WHERE employee_id = ?"
        CURSOR.execute(query, (employee_id,))
        rows = CURSOR.fetchall()
        return [cls.instance_from_db(row) for row in rows]

    def update(self):
        """Update the table row corresponding to the current Review instance."""
        if self.id is not None:
                CURSOR.execute('''
                    UPDATE reviews
                    SET year =?, summary = ?, employee_id = ?
                    WHERE id = ?
                ''', (self.year, self.summary, self.employee_id, self.id))
                CONN.commit()
        else:
            raise ValueError("Cannot update a review that hasn't been saved to the database")


    def delete(self):
        """Delete the table row corresponding to the current Review instance,
        delete the dictionary entry, and reassign id attribute"""
        if self.id is not None:
            CURSOR.execute('''
                DELETE FROM reviews
                WHERE id = ?
            ''', (self.id,))
            CONN.commit()
            if self.id in Review.all:
                del Review.all[self.id]
            self.id = None
        else:
            raise ValueError("This review does not exist in the database")

    @classmethod
    def get_all(cls):
        """Return a list containing one Review instance per table row"""
       
        rows =  CURSOR.execute("SELECT * FROM reviews").fetchall()
        print(rows)
        return [cls.instance_from_db(row) for row in rows]
    @classmethod
    def find_by_id(cls, review_id):
        sql = "SELECT * FROM reviews WHERE id = ?"
        row = CURSOR.execute(sql, (review_id,)).fetchone()
        if row:
            return cls.instance_from_db(row)
        return None

