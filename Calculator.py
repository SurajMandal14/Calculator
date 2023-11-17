import tkinter as tk


def calculate():
    num1 = float(entry_num1.get())
    num2 = float(entry_num2.get())
    operation = variable.get()

    if operation == "+":
        result = num1 + num2
    elif operation == "-":
        result = num1 - num2
    elif operation == "*":
        result = num1 * num2
    elif operation == "/":
        if num2 != 0:
            result = num1 / num2
        else:
            result = "Cannot divide by zero"
    else:
        result = "Invalid operation"

    label_result.config(text=f"Result: {result}")


root = tk.Tk()
root.title("Simple Calculator")

root.geometry("800x600")

frame = tk.Frame(root, bg="#f0f0f0", padx=40, pady=40)
frame.pack(expand=True)

label_num1 = tk.Label(frame, text="Enter first number:",
                      font=("Arial", 24), bg="#f0f0f0")
label_num1.grid(row=0, column=0, pady=10)

entry_num1 = tk.Entry(frame, font=("Arial", 24))
entry_num1.grid(row=0, column=1, pady=10)

label_num2 = tk.Label(frame, text="Enter second number:",
                      font=("Arial", 24), bg="#f0f0f0")
label_num2.grid(row=1, column=0, pady=10)

entry_num2 = tk.Entry(frame, font=("Arial", 24))
entry_num2.grid(row=1, column=1, pady=10)

label_operation = tk.Label(
    frame, text="Choose operation:", font=("Arial", 24), bg="#f0f0f0")
label_operation.grid(row=2, column=0, pady=10)

variable = tk.StringVar(root)
variable.set("+")  # Default operation is addition

operation_menu = tk.OptionMenu(frame, variable, "+", "-", "*", "/")
operation_menu.config(font=("Arial", 24))
operation_menu.grid(row=2, column=1, pady=10)

button_calculate = tk.Button(
    frame, text="Calculate", font=("Arial", 24), command=calculate)
button_calculate.grid(row=3, columnspan=2, pady=20)

label_result = tk.Label(frame, text="Result: ",
                        font=("Arial", 28), bg="#f0f0f0")
label_result.grid(row=4, columnspan=2, pady=10)

root.mainloop()
