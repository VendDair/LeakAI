import customtkinter as tk
from PIL import Image
import json
import os
from functools import partial
from src.api import get_data, get_models, generate, gpt_request, image_to_image, upscale, get_set_base64
from glob import glob

class App(tk.CTk):
    def __init__(self):
        super().__init__()

        self.model = "absolute-reality-v1-8-1"
        self.steps = 25
        self.guidance = 7.5
        self.strength = 0.2

        self.title("LeakAI")
        tk.set_appearance_mode("dark")
        self.resizable(False, False)
        self.geometry("1024x512")

        self.Y_OFFSET = 55

        # create container for image at the right half of the window
        # idk why I need to use label to set the image >_<
        self.image_container = tk.CTkFrame(self, 512, 512, 0, 0)
        self.image_container.place(y=0, x=512)
        self.image = tk.CTkImage(Image.open(get_data("last_image_used")), size=(512, 512))
        self.label = tk.CTkLabel(self.image_container, image=self.image, text="")
        self.label.place(anchor=tk.CENTER, relx=0.5, rely=0.5)
        
        # creating the tabview with elements:
        #    Prompt to Image
        #    Image to Image
        #    Upscale
        #    History
        self.tabview = tk.CTkTabview(self, 512, 512, command=self.tab_handler, fg_color="#242424")
        self.tabview.place(x=0, y=0)
        self.PROMPT_TO_IMAGE = "Prompt to Image"
        self.IMAGE_TO_IMAGE = "Image to Image"
        self.UPSCALE = "Upscale"
        self.HISTORY = "History"
        self.tabview.add(self.PROMPT_TO_IMAGE)
        self.tabview.add(self.IMAGE_TO_IMAGE)
        self.tabview.add(self.UPSCALE)
        self.tabview.add(self.HISTORY)

        # Prompt input
        self.prompt_input = tk.CTkEntry(self, fg_color=None)
        self.prompt_input.place(x=256, rely=0.54, anchor=tk.CENTER)
        self.prompt_input_text = tk.CTkLabel(self, text="Prompt:")
        self.prompt_input_text.place(relx=0.15, rely=.54, anchor=tk.CENTER)
        
        # Negative prompt input
        self.negative_prompt_input = tk.CTkEntry(self, fg_color=None)
        self.negative_prompt_input.place(x=256, rely=.625, anchor=tk.CENTER)
        self.negative_prompt_input_text = tk.CTkLabel(self, text="Negative prompt:")
        self.negative_prompt_input_text.place(relx=.125, rely=.625, anchor=tk.CENTER)

        # Steps slider
        self.steps_slider = tk.CTkSlider(self, from_=1, to=100, number_of_steps=40, command=self.steps_slider_handler)
        self.steps_slider.set(self.steps)
        self.steps_slider_text = tk.CTkLabel(self, text="Steps:")
        self.steps_slider.place(x=256, rely=.2, anchor=tk.CENTER)
        self.steps_slider_text.place(x=256, rely=.15, anchor=tk.CENTER)

        # Guidance slider
        self.guidance_slider = tk.CTkSlider(self, from_=1, to=20, number_of_steps=40, command=self.guidance_slider_handler)
        self.guidance_slider.set(self.guidance)
        self.guidance_slider_text = tk.CTkLabel(self, text="Guidance:")
        self.guidance_slider.place(x=256, rely=.3, anchor=tk.CENTER)
        self.guidance_slider_text.place(x=256, rely=.25, anchor=tk.CENTER)

        # Strength slider to Image to Image tab
        self.strength_slider = tk.CTkSlider(self.tabview.tab(self.IMAGE_TO_IMAGE), from_=0.1, to=1, number_of_steps=40, command=self.strength_slider_handler)
        self.strength_slider.set(0.5)
        self.strength_slider_text = tk.CTkLabel(self.tabview.tab(self.IMAGE_TO_IMAGE), text="Strength:")
        self.strength_slider.place(relx=.5, rely=.375, anchor=tk.CENTER)
        self.strength_slider_text.place(relx=.5, rely=.32, anchor=tk.CENTER)

        # Option menu with all models availible
        self.models_option_menu = tk.CTkOptionMenu(self, values=get_models(), command=self.models_option_menu_handler)
        self.models_option_menu.place(x=20, y=50)

        # Check box for AI help
        self.ai_checkbox = tk.CTkCheckBox(self, width=10, text="Use AI")
        self.ai_checkbox.place(relx=0.375, rely=.54, anchor=tk.CENTER)

        # Upscale button for Upscale tab
        self.upscale_button = tk.CTkButton(self.tabview.tab(self.UPSCALE), text="Upscale", command=self.upscale_button_handler)
        self.upscale_button.pack()
    
        # History frame for History tab
        self.history_scrollable_frame = tk.CTkScrollableFrame(self.tabview.tab(self.HISTORY), width=450, height=450)
        self.history_scrollable_frame.pack()
        
        # Generate button
        self.generate_button = tk.CTkButton(self, text="Generate", command=self.generate_callback)
        self.generate_button.place(x=256, rely=.71, anchor=tk.CENTER)

    def place(self):
        self.ai_checkbox.place(relx=0.375, rely=.54, anchor=tk.CENTER)
        self.guidance_slider.place(x=256, rely=.3, anchor=tk.CENTER)
        self.models_option_menu.place(x=20, y=50)
        self.guidance_slider_text.place(x=256, rely=.25, anchor=tk.CENTER)
        self.steps_slider.place(x=256, rely=.2, anchor=tk.CENTER)
        self.steps_slider_text.place(x=256, rely=.15, anchor=tk.CENTER)
        self.negative_prompt_input_text.place(relx=.125, rely=.625, anchor=tk.CENTER)
        self.negative_prompt_input.place(x=256, rely=.625, anchor=tk.CENTER)
        self.prompt_input.place(x=256, rely=0.54, anchor=tk.CENTER)
        self.generate_button.place(x=256, rely=.71 ,anchor=tk.CENTER)
        self.prompt_input_text.place(relx=0.15, rely=.54, anchor=tk.CENTER)
    def forget(self):
        self.ai_checkbox.place_forget()
        self.models_option_menu.place_forget()
        self.steps_slider.place_forget()
        self.steps_slider_text.place_forget()
        self.negative_prompt_input_text.place_forget()
        self.negative_prompt_input.place_forget()
        self.prompt_input.place_forget()
        self.prompt_input_text.place_forget()
        self.generate_button.place_forget()
        self.guidance_slider.place_forget()
        self.guidance_slider_text.place_forget()
    
    def upscale_button_handler(self):
        upscale()

    def strength_slider_handler(self, _):
        self.strength = self.strength_slider.get()

    def guidance_slider_handler(self):
        self.guidance = self.guidance_slider.get()

    def steps_slider_handler(self):
        self.steps = self.steps_slider.get()
    
    def models_option_menu_handler(self, _):
        self.model = self.models_option_menu.get()

    def generate_callback(self):
        prompt = self.prompt_input.get()
        if self.ai_checkbox.get() == 1:
            prompt = gpt_request(prompt)
        print(prompt)
        image = ""
        if self.tabview.get() == self.PROMPT_TO_IMAGE: image = generate(prompt, self.model, self.steps, self.guidance, self.negative_prompt_input.get())
        elif self.tabview.get() == self.IMAGE_TO_IMAGE: image = image_to_image(prompt, self.model, self.steps, self.guidance, self.strength, self.negative_prompt_input.get())
        else: return

        self.image.configure(light_image=Image.open(image))

    def use_img(self, file_path: str):
        self.image.configure(light_image=Image.open(file_path))
        get_set_base64(file_path)

    def preview_img(self, file_path: str):
        self.image.configure(light_image=Image.open(file_path))
    
    def delete_img(self, file_path: str, frame: tk.CTkFrame):
        os.remove(file_path)
        frame.destroy()
        frame.pack_forget()

        self.files = glob(os.path.join("src/images", "*.jpg"))
        self.files = reversed(self.files)
        file_path = next(iter(self.files), None)

        get_set_base64(file_path)
        self.image.configure(light_image=Image.open(file_path))

    def history(self):
        self.files = glob(os.path.join("src/images", "*.jpg"))
        self.files = reversed(self.files)

        for file in self.files:
            image_raw = Image.open(file)
            image = tk.CTkImage(image_raw, size=(150, 150))

            frame = tk.CTkFrame(self.history_scrollable_frame, width=400, height=256)

            size = f"{image_raw.size[0]}x{image_raw.size[0]}"
            size_label = tk.CTkLabel(frame, text=size)
            size_label.pack(side=tk.TOP, padx=10)

            lb = tk.CTkLabel(frame, image=image, text="")
            lb.pack(side=tk.LEFT, padx=10)
            tk.CTkButton(frame, text="Use", width=100, command=partial(self.use_img, file)).pack(side=tk.RIGHT, fill="x")
            tk.CTkButton(frame, text="Preview", width=100, command=partial(self.preview_img, file)).pack(side=tk.RIGHT,
                                                                                                        fill="x")
            tk.CTkButton(frame, text="Delete", width=50, command=partial(self.delete_img, file, frame)).pack(
                side=tk.RIGHT,
                fill="x")
            frame.pack(pady=20)


    def tab_handler(self):
        if self.tabview.get() != self.HISTORY:
            self.image.configure(light_image=Image.open(get_data("last_image_used")))
            for widget in self.history_scrollable_frame.winfo_children():
                widget.destroy()

        if self.tabview.get() == self.HISTORY:
            self.forget()
            self.history()
        elif self.tabview.get() == self.UPSCALE:
            self.forget()
        else:
            self.place()

if __name__ == "__main__":
    app = App()
    app.mainloop()



