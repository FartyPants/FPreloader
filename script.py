from pathlib import Path
import gradio as gr
import modules.shared as shared
from pathlib import Path
import modules.extensions as extensions_module
import sys
import importlib
import time
import inspect
from modules import utils
import os
import json
from sys import version_info

file_nameJSON = "FPreloader.json"

params = {
    "display_name": "FPreloader",
    "is_tab": True,
    "timeout": 2.5,
    "LORAsubs": False,
    "LORATime": False,
    "MODELTime": False

}

original_get_available_loras = utils.get_available_loras
original_get_available_models = utils.get_available_models
loaded_extens = []

attribute_watch = []

Lora_sortedByTime=False
Lora_witSubs=False

# currently displayed extension in the data view
current_extension = ''

refresh_symbol = '\U0001f504'  # 🔄

class ToolButton(gr.Button, gr.components.FormComponent):
    """Small button with single emoji as text, fits inside gradio forms"""

    def __init__(self, **kwargs):
        super().__init__(variant="tool", **kwargs)

    def get_block_name(self):
        return "button"



def clean_path(base_path: str, path: str):
    """Strips unusual symbols and forcibly builds a path as relative to the intended directory."""
    # TODO: Probably could do with a security audit to guarantee there's no ways this can be bypassed to target an unwanted path.
    # Or swap it to a strict whitelist of [a-zA-Z_0-9]
    path = path.replace('\\', '/').replace('..', '_')
    if base_path is None:
        return path

    return f'{Path(base_path).absolute()}/{path}'

def process_extens():
    global loaded_extens

    loaded_extens.clear()

    result = ''
    for i, name in enumerate(shared.args.extensions):
        if name in extensions_module.available_extensions:
            
            #ext = f"extensions.{name}.script"
            loaded_extens.append(name)

            if name != 'api':
                print(f'Extension "{name}"...')
                result+=name+', '


    return result            

def reload(full_name):
    if full_name in sys.modules:
      print(f"Reloading module: \033[1;31;1m{full_name}\033[0;37;0m")
      importlib.reload(sys.modules[full_name])


def reload_extens():

    result ='Reloaded :'

    for i, name in enumerate(shared.args.extensions):
        if name in extensions_module.available_extensions:
            if name != 'api':
                extension = f"extensions.{name}.script"

                if extension != "extensions.FPreloader.script":
                    reload(extension)
                    result+='['+name+'] '

   
    return result

def process_allmodules():
    
    names = []
    for i, name in enumerate(shared.args.extensions):
        if name in extensions_module.available_extensions:
            if name != 'api':
                names.append(name+'.')

    result=''
    for mod in sys.modules:
        if any(name in mod for name in names):
            result+=mod+'\n'

    return result        

def reload_extensAll():
   
    names = []
    for i, name in enumerate(shared.args.extensions):
        if name in extensions_module.available_extensions:
            if name != 'api':
                names.append(name+'.')

    result=''
    extensions = []
    for mod in sys.modules:
        if any(name in mod for name in names):
            if mod != "extensions.FPreloader.script":
                extensions.append(mod)

    
    for extension in extensions:
        reload(extension)
        result+='['+name+'] '

    return result    



def wait_recomp():
    time.sleep(params['timeout'])
    shared.need_restart = True

def gradio_restart():
    shared.need_restart = True

def display_module(ext_module,module_name):

    global attribute_watch
    lines = ''
    if len(attribute_watch) > 0:
        lines = f"# Attributes in {module_name}\n"
        ext_module_items = dir(ext_module)
        for item in attribute_watch:
            itemstr = f"{item}"
            key_str = ''
            # Find the index positions of '[' and ']'
            start_index = itemstr.find('[')
            end_index = itemstr.find(']')

            if start_index != -1 and end_index != -1:
                # Square brackets found
                param = itemstr[:start_index]
                key_str = itemstr[start_index + 1 : end_index]
                key_str = key_str.strip()
                key_str = key_str.replace('\"','')
                key_str = key_str.replace('\'','')

                itemstr = param
            else:
                # Square brackets not found
                key_str = ""

            line = f"{itemstr}:\n"
            if itemstr in ext_module_items:
                if not callable(getattr(ext_module, itemstr)):
                    value = getattr(ext_module, itemstr)
                    # value is dictionaries
                    if isinstance(value, dict):
                        line =line+ "{\n"
                        for key,val in value.items():
                            valstr = f'{val}'
                            if isinstance(val, str):
                                valstr = valstr.replace('\n','\\n')
                                valstr = valstr.replace("'","\\'")
                                valstr = "'"+valstr+"'"

                            if key_str:
                                #display only the desired key
                                keynew = f"{key}"
                                if key_str==keynew:
                                    line =line+ f"..., \'{key}\': {valstr}\n"
                            else:    
                                line =line+ f"     \'{key}\': {valstr},\n" 
                        line =line+ "}\n"           
                    else:
                        valstr = f'{value}'
                        if isinstance(value, str):
                            valstr = valstr.replace('\n','\\n')
                            valstr = valstr.replace("'","\\'")
                            valstr = "'"+valstr+"'"
    
                        line = f"{itemstr}: {valstr}\n\n"
                    lines = lines+line
            else:
                line = f"{itemstr}: --none--\n\n"
                lines = lines+line

        return lines

    lines = lines +'#----Attributes:----\n'
    ext_module_items = dir(ext_module)
    for item in ext_module_items:
        if not callable(getattr(ext_module, item)) and not item.startswith('__') and not item=='gradio':
            value = getattr(ext_module, item)
            type_str = f"{type(value).__name__}"
            value_str = f"{value}"
            if type_str=='str':
                value_str = "'"+value_str+"'"
            if type_str:
                type_str = "("+type_str+") "

            line = f"{item}: {type_str}{value_str}\n"
            #line = f"{item}: {value}\n"
            lines = lines+line

    lines = lines+ '#----Functions:----\n'
    
    for item in ext_module_items:
        obj = getattr(ext_module, item)
        try:
            if inspect.isfunction(obj):
                signature = inspect.signature(obj)
                #parameters = list(signature.parameters.keys())
                #parameters_str = ', '.join(parameters)
                line = f"{item}{signature}\n"
                lines = lines+line
        except Exception as e:
            print(f"Error occurred while inspecting {item}: {str(e)}")
                

    lines = lines+ '#----Classes:----\n'
    for item in ext_module_items:
        obj = getattr(ext_module, item)
        if inspect.isclass(obj):
            line = f"{item}\n"
            lines = lines+line

    return lines        



def radio_change(selected_extension):
    extension = f"extensions.{selected_extension}.script"
    global current_extension
    textout = ''
    current_extension = ''
    if extension in sys.modules:
        current_extension = extension
        ext_module = sys.modules[extension]

        textout = display_module(ext_module,extension)
  

        #textout = f"{ext_module}"

    return textout

def custom_module(module,selected_extension):
    global current_extension
    textout = ''
    if module=='':
        textout = radio_change(selected_extension)
        return textout
    current_extension = ''
    if module in sys.modules:
        ext_module = sys.modules[module]
        current_extension = module
        textout = display_module(ext_module,module)
    else:
        textout = f"Module {module} does not exist."

    return textout

def attributewatch(attribs):
    global attribute_watch
    if attribs:
        attribute_watch = [item.strip() for item in attribs.split(',')]
    else:
        attribute_watch = []

    extension = current_extension    
    if extension in sys.modules:
        ext_module = sys.modules[extension]
        ext_module = sys.modules[extension]
        textout = display_module(ext_module,extension)
    else:
        textout = f"Module {extension} does not exist."        

    return textout

def get_available_lorasProper():
    return sorted([item.name for item in list(Path(shared.args.lora_dir).glob('*')) if not item.name.endswith(('.txt', '-np', '.pt', '.json'))], key=utils.natural_keys)

def list_subfolders2(directory, subdir):
    subfolders = []
    for entry in os.scandir(directory):
        if entry.is_dir() and entry.name != 'runs':
            newdir = f"{subdir}/{entry.name}"
            subfolders.append(newdir)

    return sorted(subfolders, key=utils.natural_keys)


def list_subfoldersROOT(directory):
    subfolders = []
    for entry in os.scandir(directory):
        if entry.is_dir():
            newdir = f"{directory}/{entry.name}"
            subfolders.append(entry.name)
            subfolders = subfolders+list_subfolders2(newdir,entry.name)

    
    return sorted(subfolders, key=utils.natural_keys)


def sorted_ls(path):
    mtime = lambda f: os.stat(os.path.join(path, f)).st_mtime
    return list(sorted(os.listdir(path), key=mtime))

def list_subfoldersByTime(directory,isSubfolders):

    if not directory.endswith('/'):
        directory += '/'
    subfolders = []
    path = directory
    name_list = os.listdir(path)
    full_list = [os.path.join(path,i) for i in name_list]
    time_sorted_list = sorted(full_list, key=os.path.getmtime,reverse=True)

    for entry in time_sorted_list:
        if os.path.isdir(entry):
            entry_str = f"{entry}"  # Convert entry to a string
            full_path = entry_str
            entry_str = entry_str.replace('\\','/')
            entry_str = entry_str.replace(f"{directory}", "")  # Remove directory part
            subfolders.append(entry_str)
            if isSubfolders:
                subfolders = subfolders+ list_subfolders2(full_path,entry_str)

    return subfolders


def get_available_loras_monkey():
    print("[FP] LORA Detour Activated")
    model_dir = shared.args.lora_dir  # Update with the appropriate directory path
    subfolders = []
    if Lora_sortedByTime:
        subfolders = list_subfoldersByTime(model_dir,Lora_witSubs)
    else:
        subfolders = list_subfoldersROOT(model_dir)        
 

    return subfolders

def get_available_models_monkey():
    print("[FP] MODELS Detour Activated")
    model_dir = shared.args.model_dir  # Update with the appropriate directory path
    subfolders = []
    subfolders = list_subfoldersByTime(model_dir, False)        
 
    return subfolders

def save_PRAMS():
    return
#    try:    
#        global params
#        with open(file_nameJSON, 'w') as json_file:
#            json.dump(params, json_file,indent=2)
#            #print(f"Saved: {file_nameJSON}")
#    except IOError as e:
#        print(f"An error occurred while saving the file: {e}") 

def update_monkey_detour_internal(bEnableSubs,bEnableTimeSort):
    global Lora_sortedByTime
    global Lora_witSubs
    Lora_witSubs = bEnableSubs
    Lora_sortedByTime = bEnableTimeSort

    if bEnableSubs or bEnableTimeSort:
        utils.get_available_loras = get_available_loras_monkey
        print(f"[FP] LoRA Subfolders: {Lora_witSubs}, Sorted by Time: {Lora_sortedByTime}")
    else:
        utils.get_available_loras = original_get_available_loras
        print("[FP] LoRA Detour Deactivated")
 

def update_monkey_detour(bEnableSubs,bEnableTimeSort):
    update_monkey_detour_internal(bEnableSubs,bEnableTimeSort)
    params.update({"LORAsubs": bEnableSubs})
    params.update({"LORATime": bEnableTimeSort})
    save_PRAMS()    

def update_monkey_detour_models_internal(bEnableMonkey):
    if bEnableMonkey:
        utils.get_available_models = get_available_models_monkey
        print(f"[FP] Models Sorted by Time")
    else:
        utils.get_available_models = original_get_available_models
        print("[FP] Models Detour Deactivated")

 
def update_monkey_detour_models(bEnableMonkey):
    update_monkey_detour_models_internal(bEnableMonkey)
    params.update({"MODELTime": bEnableMonkey})
    save_PRAMS()


def ui():

#   try:
#       with open(file_nameJSON, 'r') as json_file:
#           new_params = json.load(json_file)
#           for item in new_params:
#               params[item] = new_params[item]
#   except FileNotFoundError:
#       params.update({"MODELTime": False})
#
#   if params['MODELTime']:
#       update_monkey_detour_models_internal(params['MODELTime'])
# 
#   if params['LORAsubs'] or params['LORATime']:
#       update_monkey_detour_internal(params['LORAsubs'],params['LORATime'])


    modelview = f"{shared.model}"
    obj_class = type(shared.model)
    objclass_pr = f"{obj_class}"

    print (f"\033[1;31;1m\nFPreloader ready\033[0;37;0m - Python {version_info[0]}.{version_info[1]}.{version_info[2]}")

    with gr.Accordion("FartyPants Extensions Reloader", open=True):
        
        with gr.Row():
            extensions_box = gr.Textbox(label='Loaded Extensions',value = process_extens())
            gr_fetch = gr.Button('[Refresh]', elem_classes="small-button")  
        with gr.Row():
            gr_reload = gr.Button(value='Reload All Extensions + Restart Gradio', variant='stop') 
            with gr.Row():
                gr_reloadonly = gr.Button(value='Reload Extensions') 
                gr_restart = gr.Button(value='Restart Gradio') 
    with gr.Accordion("Deep Reload", open=False):
        with gr.Row():
            allmodules = gr.Textbox(label='Extensions + Nested Imports',value = 'Press [Refresh] to see the list')
            allmodules_fetch = gr.Button('[Refresh]', elem_classes="small-button")
        with gr.Row():
            gr_reloadAll = gr.Button(value='Reload All Extensions and Nested Imports + Restart Gradio', variant='stop') 
   
    with gr.Accordion("FartyPants Debugger", open=False):
        with gr.Row():
            with gr.Column(scale=1):
                gr_refresh = gr.Button(value='Refresh')  
                class_p = gr.Textbox(label='Class: shared.model', value=objclass_pr)
                preview = gr.Code(label='shared.model', lines=10, value=modelview,language="python")
            with gr.Column(scale=3):
                gr_refresh3 = gr.Button(value='Refresh')
                with gr.Row():
                    with gr.Column(scale=2):
                        gr_radio= gr.Radio(choices=loaded_extens, value='None',label='Extensions')
                        with gr.Row():
                            with gr.Column(scale=2):
                                gr_attrWatch =  gr.Textbox(label='Attribute Watch (comma delimited)', lines=1, value='',info="Ex: params, params['display_name'], __builtins__ etc...")
                            with gr.Column(scale=1 ):
                                gr_Refresh4 = gr.Button(value="Refresh")
                                gr_Clear =  gr.Button(value="Clear")
                    with gr.Column(scale=1):                        
                        with gr.Row():
                            with gr.Column():
                                gr_customMod =  gr.Textbox(label='Module View',info="Enter name of module, ex: modules.shared", lines=1, value='modules.LoRA')
                                with gr.Row():
                                    gr_custApp = gr.Button(value="View Module")
                                    gr_custApp2 = gr.Button(value="Back")
                
                preview3 = gr.Code(label='module', lines=4, value="# Data View\n",language="python")
    with gr.Accordion("FartyPants Monkey Bussines", open=False):
        with gr.Row():
            with gr.Column():
                monkey_detour = gr.Checkbox(value = params['LORAsubs'], label='List LoRA + Checkpoints', info='When enabled, the LoRA menu will also shows all nested checkpoints')
                monkey_TimeSort = gr.Checkbox(value = params['LORATime'], label='Sort LoRA by recently created', info='When enabled, the LoRA menu will be sorted by time with newest LoRA(s) first')
                monkey_TimeSortMod = gr.Checkbox(value = params['MODELTime'], label='Sort MODELS by recently added', info='When enabled, the MODELS menu will be sorted by time with newest models first')
                monkey_patch = gr.Checkbox(value = shared.args.monkey_patch, label='Apply/Remove --monkeypatch without restarting', info='You still need to reload model if it was previously loaded with GPTQ_for_LLaAMA (untested feature)')    
    with gr.Accordion("Settings", open=True):
        with gr.Row():
            with gr.Column():
                timeout = gr.Slider(0.0, 5.0, value=params['timeout'], step=0.5, label='Timeout (seconds)', info='Timeout between Reload and Restart Gradio (Waiting for recompile)')
            with gr.Column():
                gr.Markdown('v.06/18/2023')    
                gr.Markdown('https://github.com/FartyPants/FPreloader')    

    
    def sliderchange(slider):  # SelectData is a subclass of EventData
        params['timeout'] = slider
   
    timeout.change(sliderchange,timeout,None)

    allmodules_fetch.click(process_allmodules, None,allmodules)
    gr_reloadAll.click(reload_extensAll,None,allmodules).then(
                lambda: None, None, None, _js='() => {document.body.innerHTML=\'<h1 style="font-family:monospace;margin-top:20%;color:blue;text-align:center;">Waiting for recompile...</h1>\'}').then(
                wait_recomp,None,None).then(
                lambda: None, None, None, _js='() => {document.body.innerHTML=\'<h1 style="font-family:monospace;margin-top:20%;color:red;text-align:center;">Reloading Gradio...</h1>\'; setTimeout(function(){location.reload()},2500); return []}')

    gr_fetch.click(process_extens, None,extensions_box).then(lambda: gr.update(choices=loaded_extens), None, gr_radio)
    gr_reload.click(reload_extens, None,extensions_box).then(
                lambda: None, None, None, _js='() => {document.body.innerHTML=\'<h1 style="font-family:monospace;margin-top:20%;color:blue;text-align:center;">Waiting for recompile...</h1>\'}').then(
                wait_recomp,None,None).then(
                lambda: None, None, None, _js='() => {document.body.innerHTML=\'<h1 style="font-family:monospace;margin-top:20%;color:red;text-align:center;">Reloading Gradio...</h1>\'; setTimeout(function(){location.reload()},2500); return []}')
    gr_reloadonly.click(reload_extens, None,extensions_box)
    gr_restart.click(gradio_restart, None,extensions_box).then(
                lambda: None, None, None, _js='() => {document.body.innerHTML=\'<h1 style="font-family:monospace;margin-top:20%;color:red;text-align:center;">Reloading Gradio...</h1>\'; setTimeout(function(){location.reload()},2500); return []}')
  

    def do_refresh():
        obj_class = type(shared.model)
        print(obj_class)
        return  f"{shared.model}",f"{obj_class}"
    
    gr_refresh.click(do_refresh,None,[preview,class_p])

    gr_refresh3.click(radio_change,gr_radio,preview3)
    gr_Refresh4.click(attributewatch,gr_attrWatch,preview3)

    gr_radio.change(radio_change,gr_radio,preview3).then(lambda x : gr.update(label=x), gr_radio, preview3)
    gr_attrWatch.change(attributewatch,gr_attrWatch,preview3)
    
    gr_Clear.click(lambda : '', None,gr_attrWatch).then(attributewatch,gr_attrWatch,preview3)

    gr_custApp.click(custom_module,[gr_customMod,gr_radio],preview3).then(lambda x : gr.update(label=x), gr_customMod, preview3)
    gr_custApp2.click(radio_change,gr_radio,preview3).then(lambda x : gr.update(label=x), gr_radio, preview3)

    def reload_lora():
        return gr.Dropdown.update(choices=utils.get_available_loras())
    
    monkey_detour.change(update_monkey_detour,[monkey_detour,monkey_TimeSort],None).then(reload_lora,None,shared.gradio['lora_menu'])
    monkey_TimeSort.change(update_monkey_detour,[monkey_detour,monkey_TimeSort],None).then(reload_lora,None,shared.gradio['lora_menu'])
   
    def update_monkeypatch(x):
        shared.args.monkey_patch = x
        print(f"--monkeypath: {shared.args.monkey_patch}")
        
    monkey_patch.change(update_monkeypatch,monkey_patch,None)

    def reload_models():
        return gr.Dropdown.update(choices=utils.get_available_models())
 
    monkey_TimeSortMod.change(update_monkey_detour_models,monkey_TimeSortMod,None).then(reload_models,None,shared.gradio['model_menu'])
