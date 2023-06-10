from pathlib import Path
import gradio as gr
from modules import utils
import modules.shared as shared
from pathlib import Path
import modules.extensions as extensions_module
import torch
import math
import os
import sys
import importlib
import time

from sys import version_info

params = {
    "display_name": "FPreloader",
    "is_tab": True,
}

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

    result = ''
    for i, name in enumerate(shared.args.extensions):
        if name in extensions_module.available_extensions:
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

def wait_recomp():
    time.sleep(2.5)
    shared.need_restart = True

def gradio_restart():
    shared.need_restart = True

def ui():


    print (f"Python {version_info}")

    with gr.Accordion("FartyPants Extensions Reloader", open=True):
        
        with gr.Row():
            extensions_box = gr.Textbox(label='Loaded Extensions',value = process_extens())
            gr_fetch = gr.Button('[Refresh]', elem_classes="small-button")  
        with gr.Row():
            gr_reload = gr.Button(value='Reload All Extensions + Restart Gradio', variant='stop') 
            with gr.Row():
                gr_reloadonly = gr.Button(value='Reload Extensions') 
                gr_restart = gr.Button(value='Restart Gradio') 
        gr_fetch.click(process_extens, None,extensions_box)
        gr_reload.click(reload_extens, None,extensions_box).then(
                lambda: None, None, None, _js='() => {document.body.innerHTML=\'<h1 style="font-family:monospace;margin-top:20%;color:blue;text-align:center;">Waiting for recompile...</h1>\'}').then(
                wait_recomp,None,None).then(
                lambda: None, None, None, _js='() => {document.body.innerHTML=\'<h1 style="font-family:monospace;margin-top:20%;color:red;text-align:center;">Reloading Gradio...</h1>\'; setTimeout(function(){location.reload()},2500); return []}')
        gr_reloadonly.click(reload_extens, None,extensions_box)
        gr_restart.click(gradio_restart, None,extensions_box).then(
                lambda: None, None, None, _js='() => {document.body.innerHTML=\'<h1 style="font-family:monospace;margin-top:20%;color:red;text-align:center;">Reloading Gradio...</h1>\'; setTimeout(function(){location.reload()},2500); return []}')
  
