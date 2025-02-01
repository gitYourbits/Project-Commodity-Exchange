# Project-Commodity-Exchange

Intro - This is a project to lend and borrow essential items from neighbours, friends and hostel mates. It has integrated chat rooms, developed using Websocket and Django Channels, for users to communicate with each other and have nagotiations on their deals. It also allows you to process payments as soon as you confirm a deal. For that it leverages RazorPay payment gateway API.

Project set-up instructions:
1. Clone this repository in your local machine.
2. Open a terminal and navigate to root folder, the folder containing "manage.py" file, using cd command.
3. Create a python Virtual Environment and activate it: python -m venv env_name >> source env_name/Scripts/activate (this command works in linux based terminals (like git bash), but root environment must be windows. For Windows powershel, simply use: env_name/Scripts/activate or if your root environment is Linux, use: source env_name/bin/activate. If still doesn't work, learn about python virtual env on internet).
4. Once venv is activated, run: pip install -r requirements.txt, all required modules and dependencies will get installed.
5. Finally run: "python manage.py runserver" in the root directory and access your project on localhost url provided in terminal by the Django ASGI development server.
6. If facing any issues, contact me on: aditya.mail.personal@gmail.com, I will help you resolve.

