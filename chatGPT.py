import tkinter as tk
from tkinter import messagebox
import requests
import json
import threading

global messages_list
messages_list = []

def generate_response2(prompt):
    global messages_list
    try:
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer your-token-here'
        }
        data = {
            "model": "gpt-4",
            "messages": [
                {"role": "system", "content": "you are very helpful and kind assistant, ready to help and your user any time"},
            ] + messages_list
        }
        
        response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, data=json.dumps(data))
        print(response.content)
        if response.status_code == 200:
            response_data = json.loads(response.content.decode('utf-8'))
            message = response_data['choices'][0]['message']['content'].strip()
        else:
            message = "Error generating response"
            
    except Exception as e:
        print("Error generating response:", e)
        message = "Error generating response"
    return message

def show_waiting_indicator():
    chat_log.tag_configure('ai_waiting', foreground='#6e7573', font=("Verdana", 12))
    chat_log.config(state=tk.NORMAL)
    chat_log.insert(tk.END, "\nChatbot: Thinking...", 'ai_waiting')
    chat_log.mark_set("waiting_indicator", tk.END + "-2 lines")
    chat_log.config(state=tk.DISABLED)
    chat_log.yview(tk.END)

def send_message(event=None):
    message = user_input.get("1.0", tk.END).strip()
    
    global messages_list
   
    if message:
        # Disable the send button
        send_button.config(state=tk.DISABLED)
        clear_button.config(state=tk.DISABLED)
        copy_button.config(state=tk.DISABLED)
    
        chat_log.tag_configure('user_text', foreground='#027fc2', font=("Verdana", 12))
        chat_log.config(state=tk.NORMAL)        
        chat_log.insert(tk.END, "\nYou: " + message + "\n", 'user_text')
        user_input.delete("1.0", tk.END)
        chat_log.config(state=tk.DISABLED)
        chat_log.yview(tk.END)
        prompt = f"You said: {message}\nChatbot:"
        messages_list.append({"role": "user", "content": message})

        # Show the waiting indicator
        show_waiting_indicator()

        # Start a new thread to generate the bot's response in the background
        thread = threading.Thread(target=generate_response, args=(prompt,))
        thread.start()

def generate_response(prompt):
    bot_message = generate_response2(prompt)
    
    global messages_list
    messages_list.append({"role": "assistant", "content": bot_message})
    
    chat_log.tag_configure('ai_text', foreground='#1C7A5E', font=("Verdana", 12))
    chat_log.config(state=tk.NORMAL)
    chat_log.delete("waiting_indicator", "waiting_indicator + 21 chars")    
    chat_log.insert(tk.END, "\nChatbot: " + bot_message + "\n", 'ai_text')
    chat_log.config(state=tk.DISABLED)
    chat_log.yview(tk.END)
    user_input.delete("1.0", tk.END)
    
    # Re-enable the send button
    send_button.config(state=tk.NORMAL)
    clear_button.config(state=tk.NORMAL)
    copy_button.config(state=tk.NORMAL)
    
def clear_input():
    chat_log.config(state=tk.NORMAL)
    chat_log.delete("1.0", tk.END)
    chat_log.config(state=tk.DISABLED)
    
def copy_ai_message(root):
    try:
        last_ai_response = None
        index = "1.0"
        
        while True:
            next_ai_range = chat_log.tag_nextrange("ai_text", index)
            
            if len(next_ai_range) < 2:
                break
                
            next_ai_start, next_ai_end = next_ai_range
            ai_message = chat_log.get(next_ai_start, next_ai_end)
            if ai_message.strip():
                last_ai_response = ai_message.strip().replace("Chatbot: ", "", 1)
            
            index = next_ai_end

        if last_ai_response:
            root.clipboard_clear()
            root.clipboard_append(last_ai_response)
            messagebox.showinfo("Copied", "AI response copied to clipboard.")
        else:
            messagebox.showerror("Error 2", "No AI response found to copy.")
            
    except Exception as e:
        print("Error copying AI message:", e)
        messagebox.showerror("Error 3", "There was an error while copying the AI response.")

    
def on_enter(event, button):
    # Changes mouse pointer when hover over enabled button
    if button['state'] != 'disabled':
        event.widget.config(cursor="hand2")
    else:
        event.widget.config(cursor="")

def on_leave(event):
    # Changes mouse pointer back to original when leaving the button
    event.widget.config(cursor="")

def run_chat():
    root = tk.Tk()
    root.title("Chatbot")

    root.resizable(width=True, height=True)

    frame = tk.Frame(root)
    frame.pack(fill=tk.BOTH, expand=True)  
    

    global chat_log
    chat_log = tk.Text(frame, bd=0, bg="white", height="8", width="50", font="Arial")
    chat_log.config(state=tk.DISABLED)

    scrollbar = tk.Scrollbar(frame, command=chat_log.yview)
    chat_log['yscrollcommand'] = scrollbar.set

    global user_input
    user_input = tk.Text(frame, bd=0, bg="white", width="5", height="2", font=("Arial", 12))
    user_input.bind("<Return>", send_message)

    global send_button
    send_button = tk.Button(frame, font=("Verdana",12,'bold'), text="Send", width="14", height=2,
                            bd=0, bg="#32de97", activebackground="#3c9d9b", fg='#ffffff',
                            command=send_message)
                            
    send_button.bind("<Enter>", lambda event: on_enter(event, send_button))
    send_button.bind("<Leave>", on_leave)
                            
    global clear_button
    clear_button = tk.Button(frame, font=("Verdana",12,'bold'), text="Clear", width="5", height=2,
                            bd=0, bg="#f05454", activebackground="#d54343", fg='#ffffff',
                            command=clear_input)
                            
    clear_button.bind("<Enter>", lambda event: on_enter(event, clear_button))
    clear_button.bind("<Leave>", on_leave)
    
    # Add the copy_button
    global copy_button
    copy_button = tk.Button(frame, font=("Verdana",12,'bold'), text="Copy", width="5", height=2,
                            bd=0, bg="#f9a828", activebackground="#db8e15", fg='#ffffff',
                            command=lambda: copy_ai_message(root))
                            
    copy_button.bind("<Enter>", lambda event: on_enter(event, copy_button))
    copy_button.bind("<Leave>", on_leave)

    chat_log.grid(row=0, column=0, columnspan=4, sticky='news')
    scrollbar.grid(row=0, column=4, sticky='ns')    
    user_input.grid(row=1, column=0, sticky='ew')    
    clear_button.grid(row=1, column=1, sticky='ew')    
    copy_button.grid(row=1, column=2, sticky='ew')
    send_button.grid(row=1, column=3, sticky='ew')

    frame.columnconfigure(0, weight=90)
    frame.columnconfigure(1, weight=3)
    frame.columnconfigure(2, weight=3)
    frame.columnconfigure(3, weight=4)
    frame.rowconfigure(0, weight=1)
    frame.rowconfigure(1, weight=0)    

    root.lift()
    root.attributes('-topmost',True)
    root.after_idle(root.attributes,'-topmost',False)    

    root.mainloop()

run_chat()