import telegram, os, dotenv, json

dotenv_file = dotenv.find_dotenv()
dotenv.load_dotenv(dotenv_file)

mybot = telegram.bot(token=os.environ['SECRET_TOKEN'])

__commands: dict = [ #all the commands of the bot in JSON format
    {
        "commands": [
            {
                "command": "start",
                "description": "Start the bot",
            },
            {
                "command": "explain",
                "description": "Describes the bot",
            }
        ],
        "scope": {
            "type": "default"
        },
        "language_code": ""
    }
]
for comm in __commands:
    print(mybot.setCommands(comm).text)

text = mybot.getCommands("default").text

commands = json.loads(text)

print(commands['result'])