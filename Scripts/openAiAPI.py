#NOTE: Works and tested for OpenAI LLM API only.

from datetime import datetime
import sys
from openai import OpenAI
import json
import base64
import argparse
from pydantic import BaseModel


# ~~~~~~~~~~~~~~~~~ Functions ~~~~~~~~~~~~~~~~~~~~~ Functions ~~~~~~~~~~~~~~~~~~~~~~~ Functions ~~~~~~~~~~~~~~~~~

# authenticate before using the API
def authenticate(authPath):
    try:
        with open(authPath, 'r') as file:
            apiKey = file.read().strip()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        exit(1)
    client = OpenAI(api_key=apiKey)
    return client


# -------------- batch processing functions-------------
#upload a jsonl file to be processed as batch
def uploadBatchFile(filePath:str):
    batch_input_file = client.files.create(
        file=open("batchinput.jsonl", "rb"),
        purpose="batch"
        )
    return batch_input_file


# create a batch object for LLM to process, requires the output of uploadBatchFileFunction
def createBatchFile(uploadBatch: str, description: str = "Default Description"):
    batch_object = client.batches.create(
        input_file_id=uploadBatch.id,
        endpoint="/v1/chat/completions",
        completion_window="24h",
        metadata={"description": description}
    )
    return batch_object


#returns a list of all batch processes, default limit is 20
def listBatches(limit = 20):
    res = client.batches.list(limit=limit)
    return res


# returns the status of the batch requested
def checkBatchProcess(batchID):
    return client.batches.retrieve(batchID)
# -------------- END batch processing functions END-------------


# ------------- Training/FineTuning Functions -------------------
# upload training dataset file path (JSONL format) for training 
def uploadTrainingFile(filePath:str):
    client_training_input = client.files.create(
        file=open(filePath, "rb"),
        purpose="fine-tune"
    )
    return client_training_input


# used to fine tune the model. requires the output of uploadTrainingFile
# default is 4o mini
def createFineTuneModel(uploadTrain:str, model="gpt-4o-mini"):
    fine_tuned_model = client.fine_tuning.jobs.create(
        training_file=uploadTrain.id, 
        model=model
    )
    return fine_tuned_model


# return a list of finteuning/training jobs
def listFineTunes(limit = 10):
    return client.fine_tuning.jobs.list(limit=limit)


# check the progress status of fine tuning. requires ID from listFineTunes
def checkFineTuningProcess(finetuneID):
    return client.fine_tuning.jobs.retrieve(finetuneID)
# ------------- END Training/FineTuning Functions END -------------------


# images stored locally requires to be encoded into base64 before being analysed.
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        res = base64.b64encode(image_file.read()).decode('utf-8')
    return res


#requires encoded image (encoded_image output)
def analyseImage(filePath, model="gpt-4o-mini"):
    
    class AnalysisRespose(BaseModel):
        description:str
        reasoning: str
        action: str
    image_path = encode_image(filePath)

    response = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a road safety visual assistant installed in a car. Your task is to analyze images of road scenes and provide recommendations for safe driving. "
                    "The user will provide you with an image or images to analyze."
                    "For each image or sub-image, use the template format to explain the following in least words:\n\n"
                    "1. Description: Describe what the car is currently doing. Then, describe the objects in the scene in few words, if any, focus on safety hazards, \
                        road signs, traffic lights, road lines/marks, pedestrians, obstacles. \n"
                    "2. Recommended Action: In few words, give suggestion as to what action should be taken by the driver. \
                        Also include if driver can change lane, overtake or turn left/right.\n"
                    "3. Reason: Explain in few words the reason for recommended action.\n\n"
                )
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Analyze the following image."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_path}"
                        }
                    }
                ]
            }
        ],
        response_format = AnalysisRespose,
    )
    return response


# store the output of LLM to json format
def save_to_json(res):
    try:
        output = res.to_dict()
        current_date = datetime.now().date()
        path = f"../Output/{current_date}.json"
        
        with open (path, 'w') as file:
            json.dump(output,file,indent=4)
        print(f"Program ran successfully. Check {path} for output")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        exit(1)
        
        
# ~~~~~~~~~~ EndFunctions ~~~~~~~~~~~~~~~~ EndFunctions ~~~~~~~~~~~~~~~~~~ EndFunctions ~~~~~~~~~~~~~~~~~


# ~~~~~~~~~~ CommandLine ~~~~~~~~~~~~~~~~ CommandLine ~~~~~~~~~~~~~~~~~~ CommandLine ~~~~~~~~~~~~~~~~~
parser = argparse.ArgumentParser(description="Functions of gpt")
parser.add_argument(
    '-pb', '--process-batch', 
    type=str, 
    metavar='<FILE_PATH>',
    help='upload a batch file path to be processed (batch process takes 24 hrs)'
)

parser.add_argument(
    '-lb', '--list-batches', 
    action='store_true', 
    help='list all batch processes'
)

parser.add_argument(
    '-cb', '--check-batch', 
    type=str,
    metavar='<BATCH_ID>',
    help='check the status of a specific batch ID. use -lb to list all batches'
)

# NOTE: THis section may be a little complicated if a fine tuned model requires furhter fine tuning,
# this will require the id of the fine tuned model?
parser.add_argument(
    '-ft', '--fine-tune', 
    type=str, 
    nargs=2,  # Specifies that this option requires exactly two arguments
    metavar=('<DATASET_PATH>', '[MODEL_NAME]'),  # Optional: specify argument names
    help='Upload a fine-tune dataset path and specify a model to be processed (Default model: 4o-mini)'
)

parser.add_argument(
    '-lft', '--list-fine-tune', 
    action='store_true', 
    help='list all fine-tune processes'
)

parser.add_argument(
    '-cft', '--check-fine-tune', 
    type=str, 
    metavar='<FINE_TUNE_ID>',

    help='check the status of a specific fine-tune ID. use -lft to list all fine tuning'
)

parser.add_argument(
    '-ai', '--analyse-image', 
    type=str, 
    metavar='<IMAGE_PATH>',
    help='analyse the image from the specified path'
)
# ~~~~~~~~~~ CommandLine ~~~~~~~~~~~~~~~~ CommandLine ~~~~~~~~~~~~~~~~~~ CommandLine ~~~~~~~~~~~~~~~~~



# ~~~~~~~~~~~~~~ main ~~~~~~~~~~~~ main ~~~~~~~~~~~~~ main ~~~~~~~~~~~~

# check flags, unknown stores the unknown flags entered by the user in CLI
args, unknown = parser.parse_known_args()
if unknown:
    print(f"Unknown arguments provided: {unknown}")
    print("For more info try running: python3 script.py --help")
    sys.exit(1)
    
    
# client = authenticate("../Private/LanceKeys/APIKey.txt")
client = authenticate("../Private/ClientKeys/chatgpt-api.txt")

if args.analyse_image:
    result = analyseImage(args.analyse_image)
    
    # print (result)
    save_to_json(result)








