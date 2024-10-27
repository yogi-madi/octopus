from models.base_model import BaseModel
from db.database import Database
from models.base_field import Text, String, Integer, JSON, UUID, Boolean
# Step 1: Initialize database
db = Database(host="localhost", user="yogi", password="Test_1234#", database="test")
BaseModel.set_db(db)

class Employee(BaseModel):
    id = UUID(primary_key=True)
    name = Text(null=False)
    email = String(unique=False, max_len=80)
    bio = Text()
    # age = Integer()
    # user_id = Integer(auto_increment=True, primary_key=True)
    meta = JSON(null=True)
    test = Boolean()
    gender = String(possible_values=["Male","Female","Other"])
    # def __init__(self,**kwargs):
    #     for i in kwargs:
    #         # self.i = kwargs[i]
    #         self.__setattr__(i, kwargs[i])
    #     super().__init__()
    # _fields = {
    #     'user_id': 'INT AUTO_INCREMENT PRIMARY KEY',
    #     'name': 'VARCHAR(275)',
    #     'email': 'VARCHAR(350)',
    # }
# emp = Employee()
# emp.name = "test"
# emp.age = 20
# print(emp.__dict__, emp.get_properties())
# Step 2: Create tables
# Employee.create_table()

# # # Step 3: Insert data
# user = Employee(name="John Doe", email="john@example.com")
# user.save()
Employee.alter_table()
# # Step 4: Query data
# all_users = Employee.all()
# print("All Users:", all_users)

# # Step 5: Update data
# user_to_update = Employee.find_by_id(1)
# if user_to_update:
#     user_to_update.update(name="Jane Doe")

# # Step 6: Delete data
# user_to_delete = User.find_by_id(1)
# if user_to_delete:
#     user_to_delete.delete()

# Step 7: Close database
# db.close()
