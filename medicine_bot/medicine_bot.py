import json
import re
import traceback

from utils import *
from wit import Wit

####################### CONFIG #######################
WIT_ACCESS_TOKEN = "STO5Q473XLWWIXFU2DCKKFE5XDNTXWEY"


######################################################


class Node:
    def __init__(self, node):
        self.node_id = node["node_id"]
        self.description = node["description"]
        self.type = node["type"]
        self.case = node["case"]
        self.message = node["message"]
        self.next_node = node["next_node"]

    @staticmethod
    def is_user_node(node):
        return node.type == "user"

    @staticmethod
    def is_bot_node(node):
        return node.type == "bot"


class Story:
    def __init__(self, stories):
        self.story = []
        for x in stories:
            self.story.append(Node(x))

    def get_node(self, index):
        return self.story[index]


class MedicineBot:
    def __init__(self, bot_data='bot_data.json'):
        bot_data = json.load(open(bot_data, encoding='utf8'))
        self.paras = bot_data["paras"]
        self.regex_para = bot_data["regex_para"]
        self.start_node_id = bot_data["start_node"]

        self.story = Story(bot_data["stories"])
        self.wit = Wit(WIT_ACCESS_TOKEN)

    def get_wit_analysis(self, message, debug=False):
        wit_respond = self.wit.message(message)
        if debug:
            print(wit_respond)
        return wit_respond

    def interactive(self, person_name):
        self.paras["{para.person_name}"] = person_name
        wit_respond = None
        current_node_id = self.start_node_id
        while current_node_id != -1:
            try:
                node = self.story.get_node(current_node_id)
                if Node.is_bot_node(node):
                    message = get_random_item(node.message)
                    message = self.fill_para_message(message, wit_respond)
                    if message:
                        bot_log_interactive(message)
                        current_node_id = node.next_node
                    else:
                        raise RuntimeError("Can not get message for node_id " + str(current_node_id))
                if Node.is_user_node(node):
                    wit_respond = self.get_wit_analysis(get_user_log_interactive(), debug=True)
                    intent, confidence = get_intent(wit_respond)
                    if intent is None:
                        bot_log_interactive(self.fill_para_message(get_random_item(node.case["error"]), wit_respond))
                    else:
                        current_node_id = node.case[intent]["next_node"]
            except:
                traceback.print_exc()
        print("Done!")

    def fill_para_message(self, message, wit_respond):
        paras = re.findall(self.regex_para, message)
        try:
            for para in paras:
                if para in self.paras:
                    message = re.sub(para, self.paras[para], message)
                elif para == "{para.schedule_time}":
                    message = re.sub(para, get_time(wit_respond), message)
                else:
                    return ValueError("Unknown para: {}".format(para))
            return message
        except:
            return None


if __name__ == '__main__':
    bot = MedicineBot()
    bot.interactive(person_name='anh Hiếu')
