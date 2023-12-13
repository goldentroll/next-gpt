from pydantic import BaseModel

class NextGptInput(BaseModel):
    prompt_input: str
    image_path: str = None
    audio_path: str = None
    video_path: str = None
    chatbot: str = None
    top_p: float = 10.0
    temperature: str =0.1
    history: str = None
    modality_cache: str = None
    guidance_scale_for_img: float = 7.5
    num_inference_steps_for_img: int = 50
    guidance_scale_for_vid:float = 7.5
    num_inference_steps_for_vid: int = 50
    num_frames: int =24
    guidance_scale_for_aud: float = 7.5
    num_inference_steps_for_aud: int = 50 
    audio_length_in_s: int = 9