import json

with open('./mysite/secret_var.json', 'r') as file:
	secret_var = json.load(file)

def send_e(bot, e, line = ''):
	if bot is not None:
		bot.send_message(secret_var["telegram_id"], line + str(e))


