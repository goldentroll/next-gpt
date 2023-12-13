import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from transformers import AutoModel, AutoTokenizer
from copy import deepcopy
import os
import ipdb
import gradio as gr
import mdtex2html
from model.anyToImageVideoAudio import NextGPTModel
import torch
import json
import tempfile
from PIL import Image
import scipy
from config import *
import imageio
import argparse
import re
from base_model import NextGptInput

# init the model
def predict(
        input,
        image_path=None,
        audio_path=None,
        video_path=None,
        thermal_path=None,
        max_tgt_len=200,
        top_p=10.0,
        temperature=0.1,
        history=None,
        modality_cache=None,
        filter_value=-float('Inf'), min_word_tokens=0,
        gen_scale_factor=10.0, max_num_imgs=1,
        stops_id=None,
        load_sd=True,
        generator=None,
        guidance_scale_for_img=7.5,
        num_inference_steps_for_img=50,
        guidance_scale_for_vid=7.5,
        num_inference_steps_for_vid=50,
        max_num_vids=1,
        height=320,
        width=576,
        num_frames=24,
        guidance_scale_for_aud=7.5,
        num_inference_steps_for_aud=50,
        max_num_auds=1,
        audio_length_in_s=9,
        ENCOUNTERS=1,
):
    if image_path is None and audio_path is None and video_path is None and thermal_path is None:
        # return [(input, "There is no input data provided! Please upload your data and start the conversation.")]
        print('no image, audio, video, and thermal are input')
    else:
        print(
            f'[!] image path: {image_path}\n[!] audio path: {audio_path}\n[!] video path: {video_path}\n[!] thermal path: {thermal_path}')

    # prepare the prompt
    prompt_text = ''
    if history != None:
        for idx, (q, a) in enumerate(history):
            if idx == 0:
                prompt_text += f'{q}\n### Assistant: {a}\n###'
            else:
                prompt_text += f' Human: {q}\n### Assistant: {a}\n###'
        prompt_text += f'### Human: {input}'
    else:
        prompt_text += f'### Human: {input}'

    print('prompt_text: ', prompt_text)

    response = model.generate({
        'prompt': prompt_text,
        'image_paths': [image_path] if image_path else [],
        'audio_paths': [audio_path] if audio_path else [],
        'video_paths': [video_path] if video_path else [],
        'thermal_paths': [thermal_path] if thermal_path else [],
        'top_p': top_p,
        'temperature': temperature,
        'max_tgt_len': max_tgt_len,
        'modality_embeds': modality_cache,
        'filter_value': filter_value, 'min_word_tokens': min_word_tokens,
        'gen_scale_factor': gen_scale_factor, 'max_num_imgs': max_num_imgs,
        'stops_id': stops_id,
        'load_sd': load_sd,
        'generator': generator,
        'guidance_scale_for_img': guidance_scale_for_img,
        'num_inference_steps_for_img': num_inference_steps_for_img,

        'guidance_scale_for_vid': guidance_scale_for_vid,
        'num_inference_steps_for_vid': num_inference_steps_for_vid,
        'max_num_vids': max_num_vids,
        'height': height,
        'width': width,
        'num_frames': num_frames,

        'guidance_scale_for_aud': guidance_scale_for_aud,
        'num_inference_steps_for_aud': num_inference_steps_for_aud,
        'max_num_auds': max_num_auds,
        'audio_length_in_s': audio_length_in_s,
        'ENCOUNTERS': ENCOUNTERS,

    })
    return response

g_cuda = torch.Generator(device='cuda').manual_seed(1337)
args = {'model': 'nextgpt',
            'nextgpt_ckpt_path': '../ckpt/delta_ckpt/nextgpt/7b_tiva_v0/',
            'max_length': 128,
            'stage': 3,
            'root_dir': '../',
            'mode': 'test',
            }
args.update(load_config(args))
model = NextGPTModel(**args)
delta_ckpt = torch.load(os.path.join(args['nextgpt_ckpt_path'], 'pytorch_model.pt'), map_location=torch.device('cuda'))
# print(delta_ckpt)
model.load_state_dict(delta_ckpt, strict=False)
model = model.eval().half().cuda()
# model = model.eval().cuda()
print(f'[!] init the 7b model over ...')

"""Override Chatbot.postprocess"""
max_tgt_length = 150
top_p = 1.0
temperature = 0.4
modality_cache = None

app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("next-gpt")
async def prediction(input: NextGptInput):
    result=predict(input=input.prompt_input,image_path=input.image_path,audio_path=input.audio_path, video_path=input.video_path,
                   top_p=input.top_p, temperature=input.temperature, history=input.history, modality_cache=input.modality_cache,
                   guidance_scale_for_img=input.guidance_scale_for_img, num_inference_steps_for_img=input.num_inference_steps_for_img,
                   guidance_scale_for_vid=input.guidance_scale_for_vid, num_inference_steps_for_vid=input.num_inference_steps_for_vid,
                   num_frames=input.num_frames, guidance_scale_for_aud=input.guidance_scale_for_aud, num_inference_steps_for_aud=input.num_inference_steps_for_aud,
                   audio_length_in_s=input.audio_length_in_s)
    return result

