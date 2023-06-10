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

from sys import version_info
if version_info[0] < 3:
    pass # Python 2 has built in reload
elif version_info[0] == 3 and version_info[1] < 4:
    from imp import reload # Python 3.0 - 3.3 
else:
    from importlib import reload # Python 3.4+


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
      print(f"Reloading module: {full_name}")
      reload(sys.modules[full_name])


def reload_extens():

    result = ''

    for i, name in enumerate(shared.args.extensions):
        if name in extensions_module.available_extensions:
            if name != 'api':
                extension = f"extensions.{name}.script"

                if extension != "extensions.FPreloader.script":
                    reload(extension)
                    result+=name+','

    shared.need_restart = True
    return result        



def ui():


    print (f"Python {version_info}")

    with gr.Accordion("FartyPants Extensions Reloader", open=True):
        
        with gr.Row():
            extensions_box = gr.Textbox(label='Loaded Extensions',value = process_extens())
            gr_fetch = gr.Button('[Refresh]', elem_classes="small-button")  
        with gr.Row():
            gr_reload = gr.Button(value='Reload All Extensions', variant='stop') 
        gr_fetch.click(process_extens, None,extensions_box)
        gr_reload.click(reload_extens, None,extensions_box).then(
                lambda: None, None, None, _js='() => {document.body.innerHTML=\'<h1 style="font-family:monospace;margin-top:20%;color:red;text-align:center;">Reloading Extensions...</h1>\'; setTimeout(function(){location.reload()},2500); return []}')

  
