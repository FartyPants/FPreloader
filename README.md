# FPreloader

An extension to reload all your other extensions. For developers and such.

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

![image](https://github.com/FartyPants/FPreloader/assets/23346289/133c7b9c-203d-4448-a542-7fa11408de4b)

Anytime you press the big red button, your extensions will be reloaded (AKA if you made changes, you will see the changes)

