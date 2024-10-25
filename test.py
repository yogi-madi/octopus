from models.base_model import BaseModel
from db.database import Database

# Step 1: Initialize database
db = Database(host="localhost", user="root", password="Test1234", database="test_db")
BaseModel.set_db(db)
class User(BaseModel):
    name = None
    email = None
    def __init__(self,**kwargs):
        for i in kwargs:
            # self.i = kwargs[i]
            self.__setattr__(i, kwargs[i])
        super().__init__()
    _fields = {
        'user_id': 'INT AUTO_INCREMENT PRIMARY KEY',
        'name': 'VARCHAR(275)',
        'email': 'VARCHAR(350)',
    }

# Step 2: Create tables
# User.create_table()

# # # Step 3: Insert data
# user = User(name="John Doe", email="john@example.com")
# user.save()
User.alter_table()
# # Step 4: Query data
# all_users = User.all()
# print("All Users:", all_users)

# # Step 5: Update data
# user_to_update = User.find_by_id(1)
# if user_to_update:
#     user_to_update.update(name="Jane Doe")

# # Step 6: Delete data
# user_to_delete = User.find_by_id(1)
# if user_to_delete:
#     user_to_delete.delete()

# Step 7: Close database
# db.close()
