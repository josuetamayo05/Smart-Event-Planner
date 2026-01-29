from auth_manager import AuthManager

am=AuthManager("users.json")
am.add_user("javier","123456")
print("Created user")