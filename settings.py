#  MongoDb connection string, to be kept secret, replace new_user_name_for_python and new_user_password_for_python with database user login and password, white list your IP address to MongoDb
#  more on https://www.mongodb.com/docs/atlas/tutorial/connect-to-your-cluster/
#   usually something like this:  "mongodb+srv://new_user_name_for_python:new_user_password_for_python@better_copy_string_from_atlas.mongodb.net/"      
URI = "mongodb+srv://new_user_name_for_python:new_user_password_for_python@better_copy_string_from_atlas.mongodb.net/"
DATABASE = "yourdatabasename"  # change datebase name here
COLLECTION = "yourcollectionname" # change collection name here
# comma seperated keywords to search in added lines
KEYWORDS = "keyword1,Europe,technology"  # for example looking for keywords Europe or technology

