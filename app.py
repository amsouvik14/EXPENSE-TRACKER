from flask import Flask, request, jsonify
from uuid import uuid1, uuid4
import os, json, pytz
from datetime import date, datetime
import pandas as pd

db = {} #Empty dictionary
db_filename = "db.json"

#CHECK WHEATHER DB.JSON EXISTS IN THE DICTIONARY OR NOT
if os.path.exists(db_filename):
    with open(db_filename, 'r') as f:
        db = json.load(f)
else:  #GENERATE ACCESS KEY AND SECRET KEY
    accesskey = str(uuid1())
    secretkey = str(uuid4())

    item_type = ["Food","Beverages","Stationary","CLothing","Electronic Accessories","Wearables"]
    db = {
        "accesskey": accesskey,
        "secretkey": secretkey,
        "item_type": item_type,
        "users": []
    }

with open(db_filename, "w+") as f:
    json.dump(db, f, indent=4)

app = Flask(__name__)

######################### USER SIGN UP ##############################
@app.route('/signup',methods=['POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        username = request.form['username']
        userDict = {
            "name": name,
            "email": email,
            "password": password,
            "username": username,
            "purchases": {}
        }

        email_list = []
        for element in db["users"]:
            email_list.append(element["email"])

        if len(db["users"]) == 0 or userDict["email"] not in email_list:
            db["users"].append(userDict)
            with open(db_filename, "r+") as f:
                f.seek(0)
                json.dump(db, f, indent=4)

            return "User added Successfully"
        else:
                return "User already exists"
        return "Error: Trying to access endpoint with wrong method"

############################# LOGIN #####################################
@app.route("/login", methods=["POST"])
def login():
    email = request.form["email"]
    password = request.form["password"]
    user_idx = None
    for user in db["users"]:
        if user["email"] == email and user["password"] == password:
            user_idx = db["users"].index(user)

            response = {
                "message": "logged in successfullly",
                "user_index": user_idx
            }
            return response
        else:
            continue
        return "Wong user!!!"

########################## ADD A PURCHASE ##############################
@app.route('/add_purchases', methods=['POST'])
def add_purchases():
    if request.method == 'POST':
        user_idx = int(request.form['user_idx'])
        item_type = request.form['item_type']
        item_name = request.form['item_name']
        item_price = request.form['item_price']

        curr_date = str(date.today())
        curr_time = str(datetime.now(pytz.timezone('Asia/Kolkata')))

        itemDict = {
            "Purchase Time": curr_time,
            "item_type": item_type,
            "item_name": item_name,
            "item_price": item_price
        }

        existingDates = list(db["users"][user_idx]["purchases"].keys())

        if len(db["users"][user_idx]["purchases"]) == 0 or curr_date not in existingDates:

            #if there are no purchases for the day
            db["users"][user_idx]["purchases"][curr_date] = []
            db["users"][user_idx]["purchases"][curr_date].append(itemDict)
            with open(db_filename, "r+") as f:
                f.seek(0)
                json.dump(db, f, indent=4)
            return"item added Successfully"

        else:
            db["users"][user_idx]["purchases"][curr_date].append(itemDict)
            with open(db_filename, "r+") as f:
                f.seek(0)
                json.dump(db, f, indent=4)
            return "item added Successfully"@app.route('/add_purchases', methods=['POST'])
def add_purchases():
    if request.method == 'POST':
        user_idx = int(request.form['user_idx'])
        item_type = request.form['item_type']
        item_name = request.form['item_name']
        item_price = request.form['item_price']

        curr_date = str(date.today())
        curr_time = str(datetime.now(pytz.timezone('Asia/Kolkata')))

        itemDict = {
            "Purchase Time": curr_time,
            "item_type": item_type,
            "item_name": item_name,
            "item_price": item_price
        }

        existingDates = list(db["users"][user_idx]["purchases"].keys())

        if len(db["users"][user_idx]["purchases"]) == 0 or curr_date not in existingDates:

            #if there are no purchases for the day
            db["users"][user_idx]["purchases"][curr_date] = []
            db["users"][user_idx]["purchases"][curr_date].append(itemDict)
            with open(db_filename, "r+") as f:
                f.seek(0)
                json.dump(db, f, indent=4)
            return "Item added Successfully"

        # else:
        #     db["users"][user_idx]["purchases"][curr_date].append(itemDict)
        #     with open(db_filename, "r+") as f:
        #         f.seek(0)
        #         json.dump(db, f, indent=4)
        #     return "item added Successfully"
               
############# GET ALL PURCHASES ################
@app.route("/get_all_purchases_for_today", methods = ["GET"])
def get_all_purchases_for_today():
    user_idx = int(request.args["user_index"])
    curr_date = str(date.today())

    list_of_purchases = int(db["users"][user_idx]["purchases"][curr_date])
    purchasedates = list(db["users"][user_idx][curr_date]["purchases"].keys())
    if(curr_date in purchasedates):
        return jsonify(purchases_for_today = list_of_purchases)
    else:
        return jsonify(message=" Date Not Found")
    # return jsonify(purchases_for_today=list_of_purchases

######################SATRT DATE AND END DATE#########################
@app.route("/get_purchases", methods = ["GET"])
def get_purchases():
    data = request.json
    user_index = data["user_index"]
    start_date = data["start_date"]
    end_date = data["end_date"]

    dates = pd.date_range(start_date, end_date)
    print(dates)

    dates_in_db = list(db["users"][user_index]["purchases"].keys())

    purchaseDict = {}
    for dt in dates_in_db:
        print(dt)
        if dt in dates:
            purchaseDict[dt] = db["users"][user_index]["purchases"][dt]
        else:
            continue
    return purchaseDict

######################## GET THE AVERAGE AMOUNT OF PURCHASES TILL NOW #############################
@app.route('/get_average_amount', methods=['POST'])
def get_average_amount():
    if request.method == 'POST':
        user_idx = int(request.form['user_index'])
        dates = list(db["users"][user_idx]["purchases"].keys())
        sum_total = 0
        count = 0
        for date in dates:
            for data in db["users"][user_idx]["purchases"][date]:
                sum_total += int(data["item_price"])
                count += 1
        average = sum_total / count
        return jsonify({'average': average})


# ######################## GET THE MOST PURCHASED ITEM ###########################
@app.route('/get_most_purchased_item', methods=['POST'])
def get_most_purchased_item():
    item_dict = {}
    if request.method == 'POST':
        user_idx = int(request.form["user_index"])
        dates = list(db["users"][user_idx]["purchases"].keys())
        for date in dates:
            for item in db["users"][user_idx]["purchases"][date]:
                if item["item_name"] not in item_dict:
                    item_dict[item["item_name"]] = 1
                else:
                    item_dict[item["item_name"]] += 1

        frequency = 0

        for key, value in item_dict.items():
            if value > frequency:
                frequency = value
                most_purchased = key
        return jsonify({"most_purchased": most_purchased})

    
if __name__== "__main__":
    app.run(host='0.0.0.0',port="5000",debug = True)

