import json
import hashlib
from abc import ABC, abstractmethod
from datetime import datetime
import unittest
#----------------------------------------------------------------WORKOUT--------------------------------------------------------------------------
#abstract base class for all workout types (requirement:anstraction )
class Workuot(ABC):
    def __init__(self, name, duration, calories_burned=None, completed_at=None):
        self.name=name
        self.duration=duration
        self.calories_burned= calories_burned if calories_burned is not None else duration*5
        self.compleded_at=completed_at if completed_at is not None else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    #abstract method that must be implemented dy other class
    @abstractmethod
    def perform(self):
        pass
    def to_dict(self):
        return{
            "type": "cardio" if isinstance(self, Cardio) else "strenght",
            "name": self.name,
            "duration":self.duration,
            "calories_burned":self.calories_burned,
            "completed_at":self.compleded_at
        }
    @staticmethod
    def from_dict(data ):
        if data["type"]=="cardio":
            return Cardio(data["name"], data["duration"],data["calories_burned"],data["completed_at"])
        elif data["type"]=="strenght":
            return Strenght(data["name"], data["duration"],data["calories_burned"],data["completed_at"])
        raise ValueError("Unknown workout type")

#Cardio class type(requirement: inheritance, Cardio class inherits from Workout class)  
class Cardio(Workuot):
    #Requirement(Polymorphism, Cardio class overrides the perform method )
    def perform(self):
        return f"Completed cardio: {self.name}, duration: {self.duration} minutes, calories burned: {self.calories_burned}, completed at :{self.compleded_at}"
    
class Strenght(Workuot):
    def perform(self):
        return f"Completed strength training: {self.name}, duration: {self.duration} minutes, calories burned: {self.calories_burned}, completed at :{self.compleded_at}"

#Class for workout creating(requiremwnt: Design pattern )
class Workoutfactory:
    @staticmethod
    def create_workout(workout_type,name,duration):
        if workout_type=="cardio":
            return  Cardio(name,duration)
        elif workout_type=="strength":
            return  Strenght(name,duration) 
        raise ValueError("Unknown workout type")

#----------------------------------------------------------------MEAL----------------------------------------------------------------------------

#abstract base class for all Meal types    
class Meal(ABC):
    #requiremet(Encapsulation:private __calories atribute )
    def __init__(self, name, calories, logged_at=None):
        self.name=name
        self.__calories=calories
        self.logged_at = logged_at if logged_at else datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @abstractmethod
    def log(self):
        pass
    def get_calories(self):
        return self.__calories
    def to_dict(self):
        meal_type= "breakfast" if isinstance(self,Breakfast) else "lunch" if isinstance(self, Lunch) else "dinner"
        return {
            "type":meal_type,
            "name": self.name,
            "calories":self.get_calories(),
            "logged_at": self.logged_at
        }
    @staticmethod
    def from_dict(data):
        if data["type"]=="breakfast":
            return Breakfast(data["name"],data["calories"])
        elif data["type"] =="lunch":
            return Lunch(data["name"], data["calories"])
        elif data["type"] =="dinner":
            return Dinner(data["name"], data["calories"])
        raise ValueError("Unknown meal type")
    
class Breakfast(Meal):
    def log(self):
        return f"Logged breakfast: {self.name}, {self.get_calories()} calories"

class Lunch(Meal):
    def log(self):
        return f"Logged lunch: {self.name}, {self.get_calories()} calories"
class Dinner(Meal):
    def log(self):
        return f"Logged dinner: {self.name}, {self.get_calories()} calories"
    
class Mealfactory:
    @staticmethod
    def create_meal(meal_type,name,calories):
        if meal_type=="breakfast":
            return Breakfast(name,calories)
        elif meal_type=="lunch":
            return Lunch(name,calories)
        elif meal_type=="dinner":
            return Dinner(name,calories)
        raise ValueError("Unknown meal type")
#---------------------------------------------------------------------USER_DATA--------------------------------------------------------------------------   

#requirement:reading form and writting to file 
class UserDatabas:
    _instance=None
    filename="users.json"
    #requirement:(Design pattern singleton pattern for UserDatabase)
    def __new__(cls):
        if cls._instance is None:
            cls._instance=super().__new__(cls)
            try:
                with open(cls.filename, "r") as f:
                    cls._instance.data=json.load(f)
                print("Loaded users.json:", cls._instance.data)    
            except FileNotFoundError:
                cls._instance.data={}
            except json.decoder.JSONDecodeError:
                cls._instance.data={}
        return cls._instance
    def register_user(self, username, password, profile):
        if username in self.data:
            return False
        hashed_password=hashlib.sha256(password.encode()).hexdigest()
        self.data[username]={
            "password":hashed_password,
            "profile":profile,
            "workouts":[],
            "meals":[]
        }
        self.save()
        return True
    
    def user_login(self,username,password):
        if username not in self.data:
            return False
        stored_hash=self.data[username]["password"]
        hashed_passwoed=hashlib.sha256(password.encode()).hexdigest()
        return stored_hash==hashed_passwoed
    def get_users_data(self,username):
        return {
            "profile":self.data[username]["profile"],
            "workouts":self.data[username]["workouts"],
            "meals":self.data[username]["meals"]
        }
    def sawe_user_data(self, username, user_data):
        self.data[username]["profile"]=user_data["profile"]
        self.data[username]["workouts"]=user_data["workouts"]
        self.data[username]["meals"]=user_data["meals"]
    
    def save(self):
        with open(self.filename,"w") as f:
            json.dump(self.data,f,indent=4)
#---------------------------------------------------------------------Database_for_summaries------------------------------------------------
class SummaryDatabase:
    _instance = None
    filename = "summaries.json"

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            try:
                with open(cls.filename, "r") as f:
                    cls._instance.data = json.load(f)
            except FileNotFoundError:
                cls._instance.data = {}
        return cls._instance

    def add_summary(self, username, date, summary):
        if username not in self.data:
            self.data[username] = {}
        self.data[username][date] = summary
        self.save()

    def get_summaries(self, username):
        return self.data.get(username, {})

    def save(self):
        with open(self.filename, "w") as f:
            json.dump(self.data, f, indent=4)
#Class to represent a user and manage their data 
class User:
    def __init__(self, username, data):
        self.username=username
        self.profile=data["profile"]
        self.workouts=[Workuot.from_dict(w) for w in data ["workouts"]]
        self.meals=[Meal.from_dict(m) for m in data["meals"]]

    def add_workots(self,workout):
        self.workouts.append(workout)
    
    def add_meals(self, meal):
        self.meals.append(meal)

    def get_workouts(self,):
        return self.workouts
    
    def to_dict(self):
        return {
            "profile":self.profile,
            "workouts":[w.to_dict() for w in self.workouts],
            "meals":[m.to_dict() for m in self.meals]
        }
    def calculate_daily_summary(self, date):
        daily_workouts = [w for w in self.workouts if w.compleded_at.startswith(date)]
        daily_meals = [m for m in self.meals if hasattr(m, 'logged_at') and m.logged_at.startswith(date)]
        
        calories_burned = sum(w.calories_burned for w in daily_workouts)
        calories_consumed = sum(m.get_calories() for m in daily_meals)
        net_calories = calories_consumed - calories_burned

        return {
            "calories_burned": calories_burned,
            "calories_consumed": calories_consumed,
            "net_calories": net_calories
        }
    
#Function to disolay the main menu and get user choice 
def show_menu():
    print("\n1.Register")
    print("2.Login")
    print("3.Exit")
    choise=input("Choose an option: ")
    if choise in ["1","2","3"]:
        return["register","login","exit"][int(choise)-1]
    else:
        print("Invalid choise, choose one more time ")
        return show_menu()
def show_users_menu():
    print("\n1.Show past workouts")
    print("2.Add new workout")
    print("3.Add meal")
    print("4.Log out")
    choise=input("Choose an option:")
    if choise in ["1","2","3","4"]:
        return["view_workouts","add_workout","add_meal","logout"][int(choise)-1]
    else:
        print("Invalid choise, try one more time")
        return show_users_menu()
def registration_info():
    username=input("Enter username:")
    password=input("Enter password: ")
    name=input("Enter name: ")
    age=int(input("Enter age: "))
    weight=float(input("Enter weight: ")) 
    goal=input("Enter your fitness goal: ")
    profile_info={"name":name, "age":age, "weight":weight, "goal":goal}
    return username, password, profile_info
def login_info():
    username=input("Enter username:")
    password=input("Enter password: ")
    return username, password

def create_workout():
    wtype=input("Enter workout type (cardio/strength) : ")
    wname= input("Enter workout name: ")
    wduration=int(input("Enter duration in minutes: "))
    return Workoutfactory.create_workout(wtype, wname, wduration)

def create_meal():
    meal_type = input("Enter meal type (breakfast/lunch/dinner): ")
    name = input("Enter meal name: ")
    calories = int(input("Enter calories: "))
    return Mealfactory.create_meal(meal_type, name, calories)

def show_past_workouts(workouts):
    if not workouts:
        print("No past workouts")
    else:
        for i , workout in enumerate(workouts, 1):
            print(f"{i}.{workout.perform()}")

#Main function to run the program 
def mainfunc():
    user_db=UserDatabas()
    sumary_db=SummaryDatabase()
    while True:
        coise=show_menu()
        if coise =="register":
            username,password, profile = registration_info()
            if user_db.register_user(username, password, profile):
                print("Registered succesfully")
            else:
                print("Username alredey exist")
        elif coise =="login":
            username, password = login_info()
            if user_db.user_login(username, password):
                user_data=user_db.get_users_data(username)
                user=User(username, user_data)
                user_menu(user, user_db, sumary_db)
            else:
                print("Invalid user data ")
        elif coise== "exit":
            break
#function to run the user menu after login 
def user_menu(user, user_db,sumary_db):
       while True:
        choice = show_users_menu()
        if choice == "view_workouts":
            workouts = user.get_workouts()
            show_past_workouts(workouts)
        elif choice == "add_workout":
            workout = create_workout()
            user.add_workots(workout)
            user_db.sawe_user_data(user.username, user.to_dict())
            print("Workout added")
        elif choice == "add_meal":
            meal = create_meal()
            user.add_meals(meal)
            user_db.sawe_user_data(user.username, user.to_dict())
            print("Meal added")
        elif choice == "logout":
            # Save calorie summary for today before logging out
            today = datetime.now().strftime("%Y-%m-%d")
            summary = user.calculate_daily_summary(today)
            # Display calorie intake for the day
            print(f"Your calorie intake for today ({today}): {summary['calories_consumed']} calories")
            # Display full summary for more context
            print(f"Calories burned today: {summary['calories_burned']} calories")
            print(f"Net calories today: {summary['net_calories']} calories")
            # Save summary to summaries.json
            sumary_db.add_summary(user.username, today, summary)
            print("Calorie summary saved to summaries.json")
            break
# Unit tests for Meal classes
# requirement: (Unit Testing (tests for meal creation and behavior))
class TestWorkout(unittest.TestCase):
    def test_cardio_workout_creation(self):
        workout = Cardio("Running", 30)
        self.assertEqual(workout.name, "Running")
        self.assertEqual(workout.duration, 30)
        self.assertEqual(workout.calories_burned, 150)
        self.assertIn("Completed cardio", workout.perform())

    def test_strength_workout_creation(self):
        workout = Strenght("Lifting", 20)
        self.assertEqual(workout.name, "Lifting")
        self.assertEqual(workout.duration, 20)
        self.assertEqual(workout.calories_burned, 100)
        self.assertIn("Completed strength", workout.perform())

class TestMeal(unittest.TestCase):
    def test_breakfast_creation(self):
        meal = Breakfast("Oatmeal", 250)
        self.assertEqual(meal.name, "Oatmeal")
        self.assertEqual(meal.get_calories(), 250)
        self.assertIn("Logged breakfast", meal.log())

    def test_dinner_creation(self):
        meal = Dinner("Steak", 700)
        self.assertEqual(meal.name, "Steak")
        self.assertEqual(meal.get_calories(), 700)
        self.assertIn("Logged dinner", meal.log())

# Unit tests for User class
class TestUser(unittest.TestCase):
    def setUp(self):
        self.user_data = {
            "profile": {"name": "Alice", "age": 30, "weight": 65, "goal": "Tone up"},
            "workouts": [],
            "meals": []
        }
        self.user = User("alice", self.user_data)

    def test_add_workout(self):
        workout = Cardio("Cycling", 40)
        self.user.add_workots(workout)
        self.assertEqual(len(self.user.get_workouts()), 1)

    def test_add_meal_and_summary(self):
        meal = Lunch("Salad", 300)
        self.user.add_meals(meal)
        today = datetime.now().strftime("%Y-%m-%d")
        summary = self.user.calculate_daily_summary(today)
        self.assertGreaterEqual(summary["calories_consumed"], 300)
# Entry point to run the program or tests
if __name__ == "__main__":
    import sys
    if "test" in sys.argv:
        unittest.main(argv=[sys.argv[0]])
    else:
        mainfunc()