import json
import os

dir_path = os.path.dirname(os.path.realpath(__file__))

from pizzabot.utils import *


class PizzaBot:
    def __init__(self, bot_data=os.path.join(dir_path, './resources/bot_data.json')):
        bot_data = json.load(open(bot_data, encoding='utf8'))
        self.paras = bot_data["paras"]
        self.stories = bot_data["stories"]
        self.start_node_id = bot_data["start_node_id"]
        self.confirm_node_id = bot_data["confirm_node_id"]
        self.end_node_id = bot_data["end_node_id"]
        self.requires = bot_data["requires"]
        self.regex_para = bot_data["regex_para"]
        self.order_data = {}
        self.prev_require = None
        self.confirmed_count = 0
        self.welcomed = False
        self.ended = False

    def can_confirm(self):
        for key in self.requires:
            if re.match(self.regex_para, key):
                if key not in self.order_data:
                    return False
        return True

    def update_order_info(self, user_mess, overwrite=False):
        for key in self.requires["orders"]:
            for regex in self.requires[key]["match_regex"]:
                founds = re.findall(regex, user_mess, re.IGNORECASE)
                if len(founds) > 0:
                    if key not in self.order_data or overwrite:

                        if key == '{para.pizza_name}':
                            founds[0] = re.sub('\\bmột\\b', '1', founds[0])
                            founds[0] = re.sub('\\bhai\\b', '2', founds[0])
                            founds[0] = re.sub('\\bba\\b', '3', founds[0])
                            founds[0] = re.sub('\\bbốn\\b', '4', founds[0])
                            founds[0] = re.sub('\\bnăm\\b', '5', founds[0])
                            founds[0] = re.sub('\\bsáu\\b', '6', founds[0])
                            founds[0] = re.sub('\\bbảy\\b', '7', founds[0])
                            founds[0] = re.sub('\\btám\\b', '8', founds[0])
                            founds[0] = re.sub('\\bchín\\b', '9', founds[0])
                            if re.match("(\\d)", founds[0]):
                                founds[0] = re.sub("(\\d) (pizza)?", r"\1 pizza ",
                                                   founds[0])
                            elif "pizza" not in founds[0]:
                                founds[0] = "pizza " + founds[0]
                        self.order_data[key] = founds[0]
                        if re.match('({para.pizza_name}|{para.pizza_size}|{para.pizza_type})', key) and re.match(
                                "(\\d)", founds[0]):
                            self.order_data["{para.pizza_amount}"] = ""
                    break

    def confirm_action(self, user_confirm_mess=None):
        # First confirm
        if self.confirmed_count == 0:
            self.confirmed_count += 1
            return self.fill_message_para(get_random_item(self.stories[self.confirm_node_id]["message"]))

        # Check confirm is YES
        for regex in self.stories[self.confirm_node_id]["match_yes"]:
            if re.match(regex, user_confirm_mess, re.IGNORECASE):
                self.ended = True
                return self.fill_message_para(get_random_item(self.stories[self.end_node_id]["message"]))

        # Check confirm is NO
        for regex in self.stories[self.confirm_node_id]["match_no"]:
            if re.match(regex, user_confirm_mess, re.IGNORECASE):
                # self.start_over()
                # return self.fill_message_para(get_random_item(self.stories[self.start_node_id]["start_over_message"]))
                self.ended = True
                return self.fill_message_para(get_random_item(self.stories[self.end_node_id]["error_message"]))

        return self.fill_message_para(get_random_item(self.stories[self.end_node_id]["error_message"]))

    def start_over(self):
        self.order_data = {}
        self.prev_require = None
        self.confirmed_count = 0
        self.welcomed = True
        self.ended = False

    def mark_as_asked_again(self, node_id):
        self.stories[node_id]["asked"] = True

    def has_asked_again(self, node_id):
        return "asked" in self.stories[node_id]

    def interactive(self, user_message=None):
        if self.ended:
            return "_END_."
        if not self.welcomed:
            self.welcomed = True
            return self.fill_message_para(get_random_item(self.stories[self.start_node_id]["message"]))
        elif self.can_confirm():
            return self.confirm_action(user_message)
        else:
            self.update_order_info(user_message)
            if not self.can_confirm():
                if user_message is None:
                    raise ValueError("user_message can not is None!")
                for key in self.requires["orders"]:
                    if key not in self.order_data:
                        if key != self.prev_require:
                            mess = get_random_item(self.stories[self.requires[key]["node_id"]]["message"])
                            self.prev_require = key
                            return self.fill_message_para(mess)
                        else:
                            if self.has_asked_again(self.requires[key]["node_id"]):
                                self.ended = True
                                return self.fill_message_para(
                                    get_random_item(self.stories[self.end_node_id]["error_message"]))
                            else:
                                self.mark_as_asked_again(self.requires[key]["node_id"])
                                mess = get_random_item(self.stories[self.requires[key]["node_id"]]["error_message"])
                            return self.fill_message_para(mess)
            else:
                return self.confirm_action()

    def fill_message_para(self, message):
        paras = re.findall(self.regex_para, message)
        for para in paras:
            if para in self.paras:
                message = re.sub(para, self.paras.get(para), message)
            else:
                message = re.sub(para, self.order_data.get(para), message)
        message = re.sub('đế giày', 'đế dày', message)
        return re.sub("\\s+", " ", message).strip()


def interactive():
    bot = PizzaBot()
    bot_mess = bot.interactive()
    while bot_mess != "_END_.":
        print(bot_mess)
        message = input('> ')
        bot_mess = bot.interactive(user_message=message)


if __name__ == '__main__':
    interactive()
