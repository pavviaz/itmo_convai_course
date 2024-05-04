import os
import asyncio

from dff.messengers.telegram import PollingTelegramInterface
from dff.pipeline import Pipeline
from dff.utils.testing.common import is_interactive_mode, check_happy_path
from dff.stats import (
    OtelInstrumentor,
    set_logger_destination,
    set_tracer_destination,
)
from dff.pipeline import (
    Pipeline,
    ACTOR,
    Service,
    ServiceGroup,
    GlobalExtraHandlerType,
)
from dff.stats import OTLPLogExporter, OTLPSpanExporter
from dff.stats import default_extractors

from dff_script import script, start_label, fallback_label, happy_path
from healthchecker import Readiness
from config import API_URL, HELPER_EP


set_logger_destination(OTLPLogExporter("grpc://otelcol:4317", insecure=True))
set_tracer_destination(OTLPSpanExporter("grpc://otelcol:4317", insecure=True))
dff_instrumentor = OtelInstrumentor()
dff_instrumentor.instrument()


@dff_instrumentor
async def get_service_state(ctx, _, info):
    data = {
        "execution_state": info.component.execution_state,
    }
    return data


async def heavy_service(ctx):
    _ = ctx
    await asyncio.sleep(0.02)


def main():
    interface = PollingTelegramInterface(token=os.getenv("TG_BOT_TOKEN"))

    pipeline = Pipeline.from_dict(
        {
            "script": script,
            "start_label": start_label,
            "fallback_label": fallback_label,
            "messenger_interface": interface,
            "components": [
                ServiceGroup(
                    before_handler=[default_extractors.get_timing_before],
                    after_handler=[
                        get_service_state,
                        default_extractors.get_timing_after,
                    ],
                    components=[
                        {"handler": heavy_service},
                        {"handler": heavy_service},
                    ],
                ),
                Service(
                    handler=ACTOR,
                    before_handler=[
                        default_extractors.get_timing_before,
                    ],
                    after_handler=[
                        get_service_state,
                        default_extractors.get_current_label,
                        default_extractors.get_timing_after,
                    ],
                ),
            ],
        }
    )
    pipeline.add_global_handler(
        GlobalExtraHandlerType.BEFORE_ALL, default_extractors.get_timing_before
    )
    pipeline.add_global_handler(
        GlobalExtraHandlerType.AFTER_ALL, default_extractors.get_timing_after
    )
    pipeline.add_global_handler(GlobalExtraHandlerType.AFTER_ALL, get_service_state)

    return pipeline


if __name__ == "__main__" and is_interactive_mode():
    print("Waiting for API to startup...", flush=True)
    Readiness(
        urls=[f"http://{API_URL}:{os.getenv('NEURAL_API_PORT')}/{HELPER_EP}"],
    ).run()

    print("Bot startup", flush=True)
    p = main()

    # check_happy_path(p, happy_path)
    print("Happy path!", flush=True)

    p.run()
