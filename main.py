import datetime
import json
import ollama
from ollama import Client
from ollama import ChatResponse
import os 
import re 
import sys 
from pydantic import BaseModel
from dataclasses import dataclass
from tqdm import tqdm
 

# Replace with your actual Ollama API key and endpoint
API_KEY = 'your_ollama_api_key'
ENDPOINT = "http://192.168.0.141:11434"

def create_chat():
    #

    # Create a new chat instance
    client = Client( host=ENDPOINT,  headers={'x-some-header': 'some-value'}  )
    models = client.list().models
    for model in models:
        print(model.model)
        #if  "phi4:" in str(model.model):
        #if  "Coder-14" in str(model.model):
        if  "writer" in str(model.model):
            
            model_name = str( model.model)
            break  
    return client , model_name
 

@dataclass
class SubtitleItem:
    index: int
    time_start: str
    time_end: str
    lines: list[str]

class SubtitleJs(BaseModel):
  index: int
  lines: list[str]
 
class Subtitles(BaseModel):
    items: list[SubtitleJs] 
 

 



def translate_subtitle( client, model_name ,  fragment):
    system_prompt = """
    Translate the following subtitle fragment from English to Brazilian Portuguese (pt-BR) while preserving the original meaning, tone, and context. Ensure the translation is idiomatic and suitable for subtitles, considering timing constraints and cultural nuances.

    Instructions:
    Context Awareness : Understand the overall context of the dialogue or scene to maintain coherence.
    Idiomatic Expressions : Translate any slang, idioms, or informal language accurately into equivalent Brazilian Portuguese expressions.
    Timing and Pacing : Ensure the translated text fits within the original timing constraints (start and end times).
    Consistency : Maintain consistency in character voices, styles, and terminology used throughout the subtitles. Use UTF8
    Ordering: Keep order and count for all entries, dont jump or skip any entry.
    Formating : Ensure the translated text is formatted correctly and follows the same structure as the original subtitle. keep number of lines and line length similar to the original.
    Write ONLY the translated subtitle text. Do not include notes , observations  or others comments.
    Dont write ANY Note/Info/Observation at end or begin of text, this text will be write to system,and anything out of format will be considered as wrong answer.
    Original Subtitle Fragment:
    """
 
    response = client.chat(  model=model_name, 
                          format=Subtitles.model_json_schema(),
        messages=[
    {
        'role': 'user',
        'content':  system_prompt
    },

    {
        'role': 'user',
        'content':  fragment
    },
    {
        'role': 'assistant',
        'content': ' Tranlated Subtitle Fragment:'
    }
    ],
    #deterministic options 
    
    ) 

    r = response.message.content 
    #clean empty lines from begin and end
    while r[0] == "\n":
        r = r[1:]
    while r[-1] == "\n":
        r = r[:-1]
    return r 


def removeEndNotes( trasnalted_text):
    #remove the end notes
    #at end of tra
    pass
     
def maybe_fix_encoding(utf8_string, possible_codec="cp1252"):
        """Attempts to fix mangled text caused by interpreting UTF8 as cp1252
        (or other codec: https://docs.python.org/3/library/codecs.html)"""
        try:
            return utf8_string.encode(possible_codec).decode('utf8')
        except UnicodeError:
            return utf8_string

def process_input_subtitle(text) -> list[SubtitleItem]  :
    #get the text  
 
    text = maybe_fix_encoding(text)
    

    #split the text by lines
    lines = text.split("\n")
    items = []
    item = None
 
    current_item = None 

    for line in lines:
        if line.strip() == "":
            continue

        #timestamp regex
        patten = r"(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})"
        if re.match(patten, line):
            time1 = re.findall(patten, line)[0][0]
            time2 = re.findall(patten, line)[0][1]     
            current_item.time_start = time1
            current_item.time_end = time2
            continue
             
 
        if line.isdigit(): 
            if (current_item != None ) :
                items.append(current_item)
            current_item = SubtitleItem(index=int(line), time_start="", time_end="", lines=[])
        else:  
            current_item.lines.append(line)
 
    if current_item != None:
        items.append(current_item)

    print(current_item.lines)
    return items             


def convert_to_text(item: SubtitleItem) -> str:
    s = str(item.index) + "\n"
    s += item.time_start + " --> " + item.time_end + "\n"
    for iline in item.lines:
        s += iline + "\n"
    return s

def convert_to_dict(item: Subtitles) -> dict:
    items = [] 
    for item in item.items:
        items.append( {  "index": item.index,  "lines": item.lines})
    return {"items": items}

def convert_to_js(sitems: list[SubtitleItem] , timestamp = True ) -> str:
    #create Subtitles object
    data = Subtitles(items=[SubtitleJs(index=item.index,   lines=item.lines) for item in sitems])
    dict_object = convert_to_dict(data)
    if timestamp == False:
        dict_object.pop('time_start', None)
        dict_object.pop('time_end', None)
    r =   json.dumps(dict_object, indent=4)  
    return r 


def convert_to_Subtitle_items( data_str :str  )  -> list[SubtitleItem]: 
    data =  json.loads(data_str)
    items = [] 
    for item in data["items"]:
        items.append(SubtitleItem(index=item["index"], time_start=item["time_start"], time_end=item["time_end"], lines=item["lines"]))
    return items

 


def is_equivalente( subtitle_items, translated_fragment_items):
    if len(subtitle_items) != len(translated_fragment_items  ):
        print("The translated fragment has a different number of items than the original fragment")
        print( str(subtitle_items))
        print( str(translated_fragment_items))
        return False
    for i in range(len(subtitle_items)):
        if int(subtitle_items[i].index) != int(translated_fragment_items[i].index):
            print("diferent index: ", subtitle_items[i].index, translated_fragment_items[i].index)
            return False
    return True 
 


def save_subtitle( outfilename ,  items):
    #write as an str valid file 
    with open(outfilename, "w" , encoding='utf8') as f:
        for item in items:
            f.write(convert_to_text(item))       
            f.write("\n")   #an empty line between items
        f.write("\n\n")    # in original file contains 2 extra end lines

# Example subtitle fragment
subtitle_fragment = """
341
00:15:14,998 --> 00:15:17,417
But be careful
with that shit, yeah?
342
00:15:17,542 --> 00:15:19,044
Careful. Ah.
343
00:15:19,169 --> 00:15:21,504
(song continues
with rapping in Russian)
344
00:15:22,964 --> 00:15:24,382
And that's for you.

"""

 


if __name__ == "__main__":
    if len(sys.argv) < 2:
       print("Usage: python main.py <path to subtitle file>")
       sys.exit(1)  
    
    subtitle_file = sys.argv[1]
    if not os.path.exists(subtitle_file):
        print("File does not exist")
        sys.exit(1)

    full_text = open(  subtitle_file , "r" , encoding='utf8').read()
    subtitle_items =   process_input_subtitle(full_text)
    #subtitle_items = subtitle_items[ 1177 : 1177 + 20 ]
 

    save_subtitle("out.str" ,     subtitle_items)

    chat , modelname  = create_chat( )
 
 
    timestamp = re.sub(r'[-: ]', '_', str(datetime.datetime.now()))
    file_out = f"tr_{timestamp}.str"

    sucess_executions = 0 
    failure_executions = 0 

    batch_size = 10
    #process 5/5 itens per  invoke 
    p_tqdm = tqdm(range(0, len(subtitle_items), batch_size))
    for i in p_tqdm:
        #print(f"processing {i} to {i+5} of {len(subtitle_items)}")
        group_items = subtitle_items[i:i+batch_size]        
        fragment_str =  "\n".join(  [ convert_to_text(item) for item in group_items]) 

        isTranslate = False
        while isTranslate== False :
            p_tqdm.set_description(f" {sucess_executions}  /  {failure_executions}")
            fragment_str_js = convert_to_js( group_items, timestamp = False  )
            translated_fragment_txt_js = translate_subtitle(chat, modelname, fragment_str_js)
           

            isTranslate = True 

            #convert to str format
            translated_fragment_items =  [ SubtitleItem(index=item["index"], time_start="", time_end="", lines=item["lines"]) for item in json.loads(translated_fragment_txt_js)["items"]]
            #verifiry if the data has same itens from original
            if not(is_equivalente( group_items, translated_fragment_items)):            
                #print("The translated fragment has a different number of items than the original fragment")               
                isTranslate = False
                failure_executions+=1            
                continue 

            sucess_executions+=1
 
            #transfer time stamps to translated fragment
            for i in range(len(group_items)):
                translated_fragment_items[i].time_start = group_items[i].time_start
                translated_fragment_items[i].time_end = group_items[i].time_end

            translated_fragment_str = "\n".join(  [ convert_to_text(item) for item in translated_fragment_items])
            if translated_fragment_str[-1] != "\n\n":
                translated_fragment_str += "\n"    

            
            with open(file_out , "a",   encoding='utf8') as f:
                f.write(translated_fragment_str )

  