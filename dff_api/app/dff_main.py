import os

from dff.messengers.telegram import PollingTelegramInterface
from dff.pipeline import Pipeline
from dff.utils.testing.common import is_interactive_mode

from dff_script import script, start_label, fallback_label
from healthchecker import Readiness
from config import API_URL, HELPER_EP


def main():
    interface = PollingTelegramInterface(token=os.getenv("TG_BOT_TOKEN"))
    
    pipeline = Pipeline.from_script(
        script=script,
        start_label=start_label,
        fallback_label=fallback_label,
        messenger_interface=interface    
    )

    pipeline.run()


if __name__ == "__main__" and is_interactive_mode():
    Readiness(
        urls=[f"http://{API_URL}:{os.getenv('NEURAL_API_PORT')}/{HELPER_EP}"],
    ).run()

    main()
