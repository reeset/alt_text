import os
import boto3 # type: ignore
import json
import dotenv # type: ignore
from PIL import Image # type: ignore
import base64
import sys
import random

full_file_list = []

def list_files_scandir(path='.', str_exclude='pdf'):
    with os.scandir(path) as entries:
        for entry in entries:
            if entry.is_file():
                if entry.path.lower().endswith(str_exclude) == False:
                    full_file_list.insert(-1, entry.path)
            elif entry.is_dir():
                list_files_scandir(entry.path)


def print_to_stderr(*a):
 
    # Here a is the array holding the objects
    # passed as the argument of the function
    print(*a, file=sys.stderr)


def get_model_id(l_model_id):
    match l_model_id:
        case "default":
            return "anthropic.claude-3-5-sonnet-20240620-v1:0"

        case "sonnet3.51":
            return "anthropic.claude-3-5-sonnet-20240620-v1:0"
        
        case "sonnet3.52":
            return "anthropic.claude-3-5-sonnet-20241022-v2:0"
        
        case "sonnet3.571":
            return "anthropic.claude-3-7-sonnet-20250219-v1:0"
        case "novapro":
            return "amazon.nova-pro-v1:0"

        case _:
            return "anthropic.claude-3-5-sonnet-20240620-v1:0"


#define variables for user defined options

# save the processing output
# option: -s [filepath]
save_file_name = ""
model_id = get_model_id("default")
prompt_file_name = "prompt.txt"
b_random = False
# model selection
# Values
# default: claude sonnet v3.5
# sonnet3.51
# sonnet3.52
# sonnet3.571
# novapro
# option: -llm [optional - value]

#folder to process
# option: -d [folder path]

#prompt file
# option: -p [optional: file path to prompt]

#Random
# option: -r [optional]


if len(sys.argv) > 0:
    n = len(sys.argv)
    for i in range(1, n):
        match sys.argv[i]:
            case "-s":
                #save file
                save_file_name = sys.argv[i+1]
                i+=1

            case "-llm":
                model = sys.argv[i+1]
                model_id = get_model_id(model)
                i+=1

            case "-d":
                folder_name = sys.argv[i+1]
                i+=1

            case "-p":
                prompt_file_name = sys.argv[i+1]
                i+=1

            case "-r":
                b_random = True

#setup the save file
#save_file_name = "C:\\Users\\reese.2179.AD\\Desktop\\python-files\\output.txt"


if os.path.exists(save_file_name):
    os.remove(save_file_name)
    
f = open(save_file_name, 'w')

dotenv.load_dotenv(".env", override=True)
# set our credentials from the environment values loaded form the .env file
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.environ.get('AWS_REGION')

# instantiate a bedrock client using boto3 (AWS' official Python SDK)
bedrock_runtime_client = boto3.client(
    'bedrock-runtime',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

# Specify the directory path you want to start from

list_files_scandir(folder_name)

random_full_file_list = full_file_list
if b_random == True:
    random_full_file_list = random.sample(full_file_list, 500)




image_count = 1
for x in random_full_file_list: 
    print('Processing image ' + str(image_count))
    image_count += 1
    # will assume all files are images
    print("processing file name" + x)
    filename = x
    image_path =  filename
    tmp_image =  filename + 'tmp_file.png'
    
    image_size = os.path.getsize(image_path)

    #print(image_size)
    if image_size < 4000000:
        tmp_image = image_path
    else:    
        base_width = 800
        img = Image.open(image_path)
        wpercent = (base_width / float(img.size[0]))
        hsize = int((float(img.size[1]) * float(wpercent)))
        img = img.resize((base_width, hsize), Image.Resampling.LANCZOS)
        img.save(tmp_image)

    #print(tmp_image)
    with open(tmp_image, 'rb') as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode()

    if tmp_image != image_path:
        # delete temp file
        os.remove(tmp_image)


    with open(prompt_file_name, 'r') as prompt_file:
        prompt_string = prompt_file.read()
    

    prompt = prompt_string
    #"text": json.dumps(prompt)

    

    payload = {
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": encoded_image
                        }
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ],
        "max_tokens": 10000,
        "anthropic_version": "bedrock-2023-05-31"
    }


    # we're ready to invoke the model!
    response = bedrock_runtime_client.invoke_model(
        modelId=model_id,
        contentType="application/json",
        body=json.dumps(payload)
    )

    # now we need to read the response. It comes back as a stream of bytes 
    # so if we want to display the response in one go we need to read the full stream first
    # then convert it to a string as json and load it as a dictionary 
    # so we can access the field containing the content without all the metadata noise
    output_binary = response["body"].read()
    output_json = json.loads(output_binary)
    output = output_json["content"][0]["text"]

    # save the output
    
    try:
        alt_text = json.loads(output)
        f.write(filename + "\t" + alt_text['image']['alt'] + "\t" + alt_text['image']['desc'] + "\t" + alt_text['image']['subjects'] + "\n")  # python will convert \n to os.linesep
    except:
        f.write(filename + "\t" + "error thrown by amazon api" + "\n")


print("Script has completed")