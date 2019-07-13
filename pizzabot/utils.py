import datetime
import random
import re
import traceback


def bot_log_interactive(message):
    print("BOT: ", message)


def get_user_log_interactive():
    log = input("USER: ")
    return log


def get_intent(wit_respond):
    try:
        entities = wit_respond["entities"]
        intent = entities["intent"]
        if type(intent) is list:
            intent = intent[0]
        return intent["value"], intent["confidence"]
    except:
        return None, 0


def get_time(wit_respond):
    try:
        responds = []
        entities = wit_respond["entities"]
        if 'datetime' in entities:
            time_value = entities["datetime"]["values"][0]["value"]
            # out: 2019-07-12T16:02:51.000+07:00
            time_value = re.sub(r"\.\d+\+.+", "", time_value)
            time_value = datetime.datetime.strptime(time_value, "%Y-%m-%dT%H:%M:%S")
            time = time_value.time()
            date = time_value.date()

            if date == datetime.datetime.now().date():
                responds.append(time.strftime("%H:%M"))
            if date - datetime.timedelta(days=1) == datetime.datetime.now():
                responds.append(time.strftime("%H:%M") + " ngày mai")
            responds.append("{} ngày {}".format(time.strftime("%H:%M"), date.strftime("%d/%m")))
        elif 'duration' in entities:
            duration_second = entities["duration"][0]["normalized"]["value"]
            time_value = (datetime.datetime.now() + datetime.timedelta(seconds=duration_second)).time()
            responds.append(time_value.strftime("%H:%M"))
            responds.append(time_value.strftime("%H:%M") + " hôm nay")
            responds.append(time_value.strftime("%H:%M") + " ngày hôm nay")
            responds.append(
                time_value.strftime("%H:%M") + " ngày {}".format(datetime.datetime.now().date().strftime("%d/%m")))
            if duration_second < 3600:
                responds.append("{} phút nữa".format(duration_second // 60))
                responds.append("{} phút sau".format(duration_second // 60))
            else:
                if duration_second % 3600 == 0:
                    responds.append("{} tiếng nữa".format(duration_second // 3600))
                    responds.append("{} tiếng sau".format(duration_second // 3600))
                    responds.append("{} giờ nữa".format(duration_second // 3600))
                    responds.append("{} giờ sau".format(duration_second // 3600))
                else:
                    responds.append("{}:{} nữa".format(duration_second // 3600, duration_second % 3600 // 60))
        return random.choice(responds)
    except:
        traceback.print_exc()
        return None


def get_random_item(messages):
    if messages is None or len(messages) == 0:
        return None
    return random.choice(messages)


