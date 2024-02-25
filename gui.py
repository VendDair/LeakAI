import customtkinter as tk
from PIL import Image
import json

class App(tk.CTk):
    def __init__(self):
        super().__init__()

        self.title("LeakAI")
        tk.set_appearance_mode("dark")
        self.resizable(False, False)
        self.geometry("1024x512")

        self.Y_OFFSET = 55

        # create container for image at the right half of the window
        # idk why I need to use label to set the image >_<
        self.image_container = tk.CTkFrame(self, 512, 512, 0, 0)
        self.image_container.place(y=0, x=512)
        self.image = tk.CTkImage(Image.open(self.get_data("last_image_used")), size=(512, 512))
        self.label = tk.CTkLabel(self.image_container, image=self.image, text="")
        self.label.place(anchor=tk.CENTER, relx=0.5, rely=0.5)
        
        # creating the tabview with elements:
        #    Prompt to Image
        #    Image to Image
        #    Upscale
        self.tabview = tk.CTkTabview(self, 512, 512)
        self.tabview.place(x=0, y=0)
        self.PROMPT_TO_IMAGE = "Prompt to Image"
        self.IMAGE_TO_IMAGE = "Image to Image"
        self.tabview.add(self.PROMPT_TO_IMAGE)
        self.tabview.add(self.IMAGE_TO_IMAGE)

        # Prompt input for Prompt to Image tab
        self.prompt_input = tk.CTkEntry(self, height=25, fg_color=None)
        self.prompt_input.place(y=self.Y_OFFSET + 256, x=256, anchor=tk.CENTER)


    def get_data(self, key: str):
        # Reads the json from src/data.json and returns the value by key provided
        try:
            with open("src/data.json", "r") as file:
                data = json.load(file)
                return data.get(key)
        except FileNotFoundError:
            print("Error: JSON file not found.")
            return None
        except json.JSONDecodeError:
            print("Error: Unable to decode JSON file.")
            return None


if __name__ == "__main__":
    app = App()
    app.mainloop()



