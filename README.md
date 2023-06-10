# FPreloader

An extension to HARD reload all your other extensions. For developers and such.

for Python > 3.4

This is a shallow process and if your extension has some nested imports, those may not be reloaded. But it will reload your script.py
(I can later add a deeper reload if needed)

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

Anytime you press the big red button, your extensions will be reloaded (AKA if you made changes, you will see the changes) then Gradio will be restarted
... or you can do it in steps: Reload Extensions, then Restart Gradio (
depending on the size of the extension there needs to be a slight time for python to recompile your modified version, the red button assumes 2.5 sec is enough)

To do (feel free to pull request):
- specify your own additional import that needs to be reloaded
- reload all modules (potentially bad idea)

