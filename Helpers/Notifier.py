import datetime
from win10toast import ToastNotifier
from configparser import ConfigParser


# ---------------------------------------------------------------------------
# Constants -----------------------------------------------------------------
# ---------------------------------------------------------------------------

showToast_OnGlobalStateChange = False
writeLog_OnGlobalStateChange = True

showToast_OnDeepSleepWakeUp = True
writeLog_OnDeepSleepWakeUp = True
iftttCall_OnDeepSleepWakeUp = False

showToast_OnDeepSleep = False
writeLog_OnDeepSleep = True
iftttCall_OnDeepSleep = False

# ---------------------------------------------------------------------------
# Initializers --------------------------------------------------------------
# ---------------------------------------------------------------------------
toast = ToastNotifier()

# ---------------------------------------------------------------------------
# Configuration -------------------------------------------------------------
# ---------------------------------------------------------------------------
config_network = ConfigParser()
config_network.read("config/config_network.ini")
ifttt_key = config_network.get("ifttt", "ifttt_key")
ifttt_event = config_network.get("ifttt", "ifttt_event")
print("Network Config Initialized @ Notifier")

# ---------------------------------------------------------------------------
# Functions -----------------------------------------------------------------
# ---------------------------------------------------------------------------


# --------------------------------------------------------------------------------------------------------


def notify_StartMoving(
    stopping_period, targetcam, file_globalstatechange, factSystemRequester
):
    title = "Moving_State " + targetcam
    message = "was stopped for " + str(stopping_period) + " min"
    message_withdate = (
        datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        + " - "
        + title
        + " - "
        + message
    )

    print(message_withdate)

    if showToast_OnGlobalStateChange:
        toast.show_toast(
            "Machine " + targetcam,
            "Machine status changed to running (was stopped for "
            + str(stopping_period)
            + "mins)",
            icon_path="python_icon.ico",
            duration=3,
        )

    if writeLog_OnGlobalStateChange:
        file_globalstatechange.write(message_withdate + "\n")
        file_globalstatechange.flush()


# --------------------------------------------------------------------------------------------------------


def notify_StopMoving(targetcam, file_globalstatechange, factSystemRequester):
    title = "Stopped_State " + targetcam
    message = ""
    message_withdate = (
        datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S") + " - " + title
    )

    print(message_withdate)

    if showToast_OnGlobalStateChange:
        toast.show_toast(title, message, icon_path="config/python_icon.ico", duration=3)

    if writeLog_OnGlobalStateChange:
        file_globalstatechange.write(message_withdate + "\n")
        file_globalstatechange.flush()


# --------------------------------------------------------------------------------------------------------


def notify_DeepSleepWakeup(
    stopping_period,
    targetcam,
    factSystemRequester,
    file_deepsleep,
):
    title = "Woke_Up: " + targetcam
    message = "Idle time: " + str(stopping_period) + " min"
    message_withdate = (
        datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        + " - "
        + title
        + " - "
        + message
    )

    print(message_withdate)

    if factSystemRequester:
        factSystemRequester.startMachine()

    if iftttCall_OnDeepSleepWakeUp and factSystemRequester:
        response = factSystemRequester.post(
            "https://maker.ifttt.com/trigger/" + ifttt_event + "/with/key/" + ifttt_key,
            params={
                "value1": title,
                "value2": message,
                "value3": "none",
            },
        )

        if response is None:
            print("request failed to trigger Woke_Up on IFTTT")
            file_deepsleep.write("request failed to trigger Woke_Up on IFTTT\n")
            file_deepsleep.flush()
        elif not (response.status_code == 200):
            print(response.text)
            file_deepsleep.write(str(response.text) + "\n")
            file_deepsleep.flush()

    if showToast_OnDeepSleepWakeUp:
        toast.show_toast(
            title,
            message,
            icon_path="config/python_icon.ico",
            duration=3,
        )

    if writeLog_OnDeepSleepWakeUp:
        file_deepsleep.write(message_withdate + "\n")
        file_deepsleep.flush()


# --------------------------------------------------------------------------------------------------------


def notify_DeepSleep(
    targetcam,
    globalmotion_deepsleep_mins,
    factSystemRequester,
    file_deepsleep,
):
    title = "Deep_Sleep: " + targetcam
    message = "stopped " + str(globalmotion_deepsleep_mins) + " mins ago"
    message_withdate = (
        datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        + " - "
        + title
        + " - "
        + message
    )
    print(message_withdate)

    if factSystemRequester:
        factSystemRequester.stopMachine()

    if iftttCall_OnDeepSleep and factSystemRequester:
        response = factSystemRequester.post(
            "https://maker.ifttt.com/trigger/" + ifttt_event + "/with/key/" + ifttt_key,
            params={
                "value1": title,
                "value2": message,
                "value3": "none",
            },
        )

        if response is None:
            print("request failed to trigger Deep_Sleep on IFTTT")
            file_deepsleep.write("request failed to trigger Deep_Sleep on IFTTT\n")
            file_deepsleep.flush()
        elif not (response.status_code == 200):
            print(response.text)
            file_deepsleep.write(str(response.text) + "\n")
            file_deepsleep.flush()

    if showToast_OnDeepSleep:
        toast.show_toast(
            title,
            message,
            icon_path="config/python_icon.ico",
            duration=3,
        )

    if writeLog_OnDeepSleep:
        file_deepsleep.write(message_withdate + "\n")
        file_deepsleep.flush()
