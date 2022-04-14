from logging import exception
from flask import Flask, Response, request, jsonify
from flask_cors import CORS, cross_origin
import pymongo
import json
import sys

app = Flask(__name__)
CORS(app, support_credentials=True)


try:
    mongo = pymongo.MongoClient('mongodb+srv://mani:Mani1@xharktank.b8ym6.mongodb.net/xharktank?retryWrites=true&w=majority')
    db = mongo["xharktank"]
    collection = db["mycollection"]

except Exception as ex:
    print("---",ex)
    print("DB NOT FOUND")


def check_pitch_post(content):
    required_keys = ["entrepreneur", "pitchTitle", "pitchIdea", "askAmount", "equity"]
    required_keys.sort()
    keys = list(content.keys())
    keys.sort()

    ## Checking for correctness of all the keys
    if(required_keys == keys and content["entrepreneur"] != None and content["pitchTitle"] != None and content["pitchIdea"] != None and content["equity"]!= None and content["askAmount"] != None):
        len_ent = len(content["entrepreneur"])
        len_pitchTitle = len(content["pitchTitle"])
        len_pitchIdea = len(content["pitchIdea"])
        entrepreneur = content["entrepreneur"]
        pitchTitle = content["pitchTitle"]
        pitchIdea = content["pitchIdea"]
        equity = content["equity"]
        askAmount = content["askAmount"]
        ent_str = isinstance(entrepreneur, str)
        pitchIdea_str = isinstance(pitchIdea, str)
        pitchTitle_str = isinstance(pitchTitle, str)
        equity_float = isinstance(equity, str)
        askAmount_float = isinstance(askAmount, str)
        

        if(equity > 100 or len_ent == 0 or len_pitchTitle == 0 or len_pitchIdea == 0 or not ent_str or not pitchTitle_str or not pitchIdea_str or equity_float or askAmount_float):
            return False        
        else:
            return True
    
    else:
        False

def check_offer_post(content):
    required_keys = ["investor", "amount", "equity", "comment"]
    required_keys.sort()
    keys = list(content.keys())
    keys.sort()

    ## checking for correctness of all the keys 
    if(required_keys == keys and content["investor"]!= None and content["equity"]!=None and content["amount"]!= None and content["comment"]!= None):
        investor = content["investor"]
        equity = content["equity"]
        amount = content["amount"]
        comment = content["comment"]
        len_investor = len(investor)
        len_comment = len(comment)
        invetsor_str = isinstance(investor, str)
        comment_str = isinstance(comment, str)
        amount_float = isinstance(amount, str)
        equity_float = isinstance(equity, str)
        

        if(equity>100 or len_investor == 0 or len_comment == 0 or not invetsor_str or not comment_str or amount_float or equity_float):
            return False
        else:
            return True
    else:
        return False



@app.route("/pitches", methods = ["POST","GET"])
@cross_origin(supports_credentials=True)
def create_pitch():
    if request.method == "POST":
        #content = None
        try:
            content = request.json
        except Exception as ex:
            return Response(status = 400)
        
        ## Checking for correctness of request content
        if(check_pitch_post(content)):
            count_id =  collection.count_documents({})
            content["id"] = str(count_id + 1)
            content["_id"] = count_id + 1
            content["offers"] = []
            ## inserting the pitch into db
            dbresponse = collection.insert_one(content)
            return Response( response = json.dumps({"id" : str(dbresponse.inserted_id)}), status = 201, mimetype = "application/json")       
        else:
            return Response(status = 400)
    
    if request.method == "GET":
        list_of_all_pitches = []
        
        ## getting all the pitches, masking _id and sorting in decreasing order of id
        pitches = collection.find().sort("_id",-1)
        
        for each_pitch in pitches:
            del each_pitch["_id"]
            list_of_all_pitches.append(each_pitch)
        
        return Response(response = json.dumps(list_of_all_pitches), status = 200, mimetype = "application/json" )


@app.route("/pitches/<pitch_id>", methods = ["GET"])
@cross_origin(supports_credentials=True)
def get_pitch(pitch_id):
    
    ## Finding the given pitch_id and masking _id 
    response_pitch = collection.find({"id":pitch_id},{"_id":0})

    required_pitch = list(response_pitch)

    ## checking whether we got required_pitch with length of cursor
    if(len(required_pitch)>0):
        required_pitch = required_pitch[0]
        return Response(response = json.dumps(required_pitch), status = 200,  mimetype = "application/json")
    else:
        return Response(status = 404)


@app.route("/pitches/<pitch_id>/makeOffer", methods = ["POST"])
@cross_origin(supports_credentials=True)
def make_offer(pitch_id):

    #content = None

    try:
        content = request.json
    
    except Exception as ex:
        return Response(status = 400)

    ## Checking for correctness of content
    if(check_offer_post(content)):
        response_pitch = collection.find({"id":pitch_id})
        required_pitch = list(response_pitch)

        ## Checking whether we got a required_pitch with length of cursor
        if(len(required_pitch)>0):            
            required_pitch = required_pitch[0]
            
            ##incrementing offer_id
            offer_id = str( len(required_pitch["offers"]) + 1 )
            content["id"] = offer_id
            required_pitch["offers"].append(content)

            dbresponse = collection.update_one({"id":pitch_id},{"$push": {"offers" : content}})
            return Response(response = json.dumps({"id":pitch_id}), status = 201,  mimetype = "application/json")
        
        else:
            return Response(status = 404)

    else:
        return Response( status = 400 )
    



if __name__ == "__main__":
    app.run()

