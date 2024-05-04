import os

from transformers import LlavaNextProcessor, LlavaNextForConditionalGeneration
import torch

from config import SBERT_MODEL, END_INST_TOKEN


class Worker:
    def __init__(self):
        self.processor = LlavaNextProcessor.from_pretrained(
            SBERT_MODEL, cache_dir=os.environ["TRANSFORMERS_CACHE"]
        )
        self.model = LlavaNextForConditionalGeneration.from_pretrained(
            SBERT_MODEL,
            torch_dtype=torch.float16,
            low_cpu_mem_usage=True,
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            cache_dir=os.environ["TRANSFORMERS_CACHE"],
        )

    def answer(self, data):
        inputs = self.processor(
            data.prompt,
            data.img,
            return_tensors="pt",
        ).to("cuda:0")

        output = self.model.generate(
            **inputs,
            max_new_tokens=data.max_new_tokens
        )

        o = self.processor.decode(
            output[0], skip_special_tokens=True, clean_up_tokenization_spaces=True
        )
        o = o[o.rfind(END_INST_TOKEN) + len(END_INST_TOKEN) :].strip()
        return {"answer": o}


if __name__ == "__main__":
    w = Worker()
