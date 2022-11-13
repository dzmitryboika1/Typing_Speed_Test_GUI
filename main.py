import json
import random
import tkinter as tk
from tkinter.constants import DISABLED, END, NORMAL, WORD
from tkinter.messagebox import showinfo
from oxford3000 import word_bank


class TypingSpeedTest(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Typing Speed Test")
        self.resizable(False, False)
        self.config(padx=20, pady=20)
        self.logo_img = None
        self.logo_canvas = None

        self.timer = None
        self.timer_text = None
        self.last_result_text = None
        self.best_result_text = None
        self.timer_canvas = None
        self.short_session = 0.3
        self.normal_session = 2
        self.long_session = 3
        self.reset_btn = None
        self.start_btn = None

        self.radio_btn_options = None
        self.radio_short = None
        self.radio_normal = None
        self.radio_long = None

        self.user_input = None
        self.source_words = None
        self.scrollbar = None
        self.current_words_str = None

        self.right_words_counter = 0

        self.create_widgets()

    def create_widgets(self):
        # logo
        self.logo_canvas = tk.Canvas(self, width=300, height=116)
        self.logo_img = tk.PhotoImage(file="logo.png")
        self.logo_canvas.create_image(150, 67, image=self.logo_img)
        self.logo_canvas.grid(column=0, row=2, columnspan=3)

        # timer
        self.timer_canvas = tk.Canvas(self, width=100, height=60)
        self.timer_text = self.timer_canvas.create_text(50, 30, text="00:00", fill="gray", font=("Courier", 25, "bold"))
        self.timer_canvas.grid(column=1, row=3)

        # scores
        self.last_result_text = tk.Label()
        self.best_result_text = tk.Label()
        self.update_results_text_labels()
        self.last_result_text.grid(column=2, row=0)
        self.best_result_text.grid(column=2, row=1)

        # duration of session (radio buttons)
        self.radio_btn_options = tk.StringVar(self)
        self.radio_btn_options.set('short')
        self.radio_short = tk.Radiobutton(self, text='Short (1 min)', variable=self.radio_btn_options, value='short')
        self.radio_short.grid(row=4, column=0)
        self.radio_normal = tk.Radiobutton(self, text='Normal (5 min)', variable=self.radio_btn_options, value='normal')
        self.radio_normal.grid(row=4, column=1)
        self.radio_long = tk.Radiobutton(self, text='Long (10 min)', variable=self.radio_btn_options, value='long')
        self.radio_long.grid(row=4, column=2)

        # text widget with source words
        self.source_words = tk.Text(self, width=35, height=8, fg='grey', font=('Arial', 16, 'bold'), wrap=WORD,
                                    state=DISABLED)
        self.source_words.tag_configure("center", justify='center')
        self.source_words.tag_configure("black_text", foreground="black")
        self.source_words.tag_configure("red_text", foreground="red")
        self.source_words.grid(column=0, row=5, columnspan=3, pady=10)

        self.scrollbar = tk.Scrollbar(self, orient='vertical', command=self.source_words.yview)
        self.scrollbar.grid(column=3, row=5, sticky='ns')
        self.source_words['yscrollcommand'] = self.scrollbar.set

        # user's input Entry
        check = (self.register(self.is_valid), '%P', '%i', '%d')
        self.user_input = tk.Entry(self, width=35, font=("Arial", 16, 'bold'), validate='key', validatecommand=check,
                                   state=DISABLED)
        self.user_input.grid(column=0, row=6, columnspan=3, pady=10)

        # buttons
        self.start_btn = tk.Button(self, text="Start", width=16, command=self.start_timer)
        self.start_btn.grid(column=1, row=7)

        self.reset_btn = tk.Button(self, text="Reset", width=16, command=self.reset_timer)
        self.reset_btn.grid(column=2, row=7)

    def get_random_words(self):
        self.current_words_str = ' '.join(random.choices(word_bank, k=300)) + ' '
        self.source_words.insert(1.0, self.current_words_str)
        self.source_words.config(state=DISABLED)

    def show_current_score_msg(self):
        result = 0
        if self.radio_btn_options.get() == 'short':
            result = self.right_words_counter
        elif self.radio_btn_options.get() == 'normal':
            result = int(self.right_words_counter / self.normal_session)
        elif self.radio_btn_options.get() == 'long':
            result = int(self.right_words_counter / self.long_session)

        showinfo(title='Result', message=f"Your result:\n{result} WPM")

    def update_results_text_labels(self):
        try:
            with open("scores.json", mode="r") as data_file:
                data = json.load(data_file)
                last_score = data['score']['last_score']
                best_score = data['score']['best_score']
                self.last_result_text.config(text=f"Last result: {last_score}")
                self.best_result_text.config(text=f"Best result: {best_score}")
        except FileNotFoundError:
            self.last_result_text.config(text=f"Last result: {0}")
            self.best_result_text.config(text=f"Best result: {0}")

    def save_result(self):
        best_result = 0
        try:
            with open("scores.json") as data_file:
                data = json.load(data_file)
                best_result = data["score"]["best_score"]
        except FileNotFoundError:
            with open("scores.json", mode="w") as data_file:
                new_data = {"score": {"last_score": self.right_words_counter, "best_score": self.right_words_counter}}
                json.dump(new_data, data_file)
        else:
            with open("scores.json", mode="w") as data_file:
                if self.right_words_counter > best_result:
                    best_result = self.right_words_counter
                new_data = {"score": {"last_score": self.right_words_counter, "best_score": best_result}}
                json.dump(new_data, data_file)
        finally:
            self.update_results_text_labels()

    # ---------------------------- WORDS VALIDATION ------------------------------- #
    def change_color(self, letter, index, color):
        self.source_words.config(state=NORMAL)
        self.source_words.delete(f"1.{index}", f"1.{str(int(index) + 1)}")
        self.source_words.insert(f"1.{index}", letter, color)

    def is_valid(self, new_value, value_index, is_delete):
        temp_letter = self.source_words.get(f"1.{str(value_index)}", f"1.{str(int(value_index) + 1)}")
        if is_delete == '1' and new_value[int(value_index)] == self.current_words_str[int(value_index)]:
            if new_value[int(value_index)] == " ":
                self.right_words_counter += 1

            self.change_color(temp_letter, value_index, "black_text")

        elif is_delete == '1' and new_value[int(value_index)] != self.current_words_str[int(value_index)]:
            self.change_color(temp_letter, value_index, "red_text")

        return True

    # ---------------------------- START TIMER ------------------------------- #
    def start_timer(self):
        self.user_input.config(state=NORMAL)
        self.user_input.focus_set()
        self.source_words.config(state=NORMAL)
        self.get_random_words()
        self.start_btn.config(state=DISABLED)
        if self.radio_btn_options.get() == "short":
            self.count_down(self.short_session * 60)
        elif self.radio_btn_options.get() == "normal":
            self.count_down(self.normal_session * 60)
        elif self.radio_btn_options.get() == "long":
            self.count_down(self.long_session * 60)

    # ---------------------------- TIMER RESET ------------------------------- #
    def reset_timer(self):
        self.after_cancel(self.timer)
        self.timer_canvas.itemconfig(self.timer_text, text="00:00")
        self.start_btn.config(state=NORMAL)
        self.source_words.config(state=NORMAL)
        self.source_words.delete(1.0, END)
        self.current_words_str = None
        self.right_words_counter = 0
        self.user_input.delete(0, END)
        self.user_input.config(state=DISABLED)
        self.source_words.config(state=DISABLED)

    # ---------------------------- COUNTDOWN MECHANISM ------------------------------- #
    def count_down(self, count):
        count_min = count // 60
        count_sec = count % 60
        if count_sec < 10:
            count_sec = f"0{count_sec}"
        self.timer_canvas.itemconfig(self.timer_text, text=f"{count_min}:{count_sec}")
        if count > 0:
            self.timer = self.after(1000, self.count_down, count - 1)
        else:
            self.show_current_score_msg()
            self.save_result()
            self.reset_timer()


if __name__ == "__main__":
    app = TypingSpeedTest()
    app.mainloop()
