# FPreloader (now with Attribute monitor)

An extension that will make your life as an extension developer this much easier > ----- < 

FPreloader will HARD reload all your other extensions. It's like that one ring that rules the other rings, or something on that note.
For developers and other strange people.

for Python > 3.4

How it works:
```
cd PATH_TO_text-generation-webui/extensions
```
then clone this repo
```
git clone https://github.com/FartyPants/FPreloader
```

Start ooba and in Interface enable FPReloader

![image](https://github.com/FartyPants/FPreloader/assets/23346289/2389911c-15e2-475f-89e5-3f36f7008610)

Apply and restart interface, now you should see tab FPReloader

![image](https://github.com/FartyPants/FPreloader/assets/23346289/8c1f30b1-1654-4982-b6b3-fc6b88e55221)

Anytime you press the big red button, your extensions will be reloaded (AKA if you made changes to your script.py file, the changes should be reloaded) then Gradio will be restarted
... or you can do it in two steps: Reload Extensions, then Restart Gradio 
(depending on the size of the extension there needs to be a slight time for python to recompile your modified version, the red button assumes 2.5 sec is enough as default)

## Nested imports (or whatever they are called)

![image](https://github.com/FartyPants/FPreloader/assets/23346289/19425d48-a93d-4ff4-bd7a-fc6dfae2b775)

Use the Deep Reload for reloading all nested imports within the extensions (for example in superbooga chromadb or download_urls will reload as well before the script itself)

## Debug View Options
allows you to see attributes etc...

![image](https://github.com/FartyPants/FPreloader/assets/23346289/26882162-2a41-4274-97e1-e2ba22bc929d)

Attribute watch - type attribute of currently viewed module you want to see, instead of all. Comma delimited

![image](https://github.com/FartyPants/FPreloader/assets/23346289/1d8dcef0-fa1a-417d-b740-3c38905ffc88)

Dictionaries - you can type the exact dictionary key (you don't need to use ' or " for keys)

![image](https://github.com/FartyPants/FPreloader/assets/23346289/66a9a11e-b294-4a3f-a015-9a665cf9e337)

The monitor doesn't update by itself, when the value change you need to press refresh.

If nothing of this makes any sense then you are in the wrong repo.
