import flet as ft
import string

def main(page: ft.Page):
    page.title = "Sinal - Jogo"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = "light"
    page.window_width = 400
    page.window_height = 600

    # Constants
    NUM_ROWS = 6
    WORD_LEN = 5

    # Keep track of current input state
    current_row = 0
    guesses = [["" for _ in range(WORD_LEN)] for _ in range(NUM_ROWS)]

    # Build grid of containers (boxes)
    grid = []
    for row in range(NUM_ROWS):
        row_controls = []
        for col in range(WORD_LEN):
            letter_img = ft.Image(
                src="letters/blank.png",
                width=40,
                height=40,
                fit=ft.ImageFit.CONTAIN,
            )

            box = ft.Container(
                width=60,
                height=60,
                bgcolor=ft.Colors.GREY_200,
                border=ft.border.all(2, ft.Colors.GREY_400),
                border_radius=8,
                alignment=ft.alignment.center,
                content=letter_img,
            )

            row_controls.append(box)
        grid.append(row_controls)

    # Add all rows to the page
    for r in grid:
        page.add(ft.Row(r, alignment="center", spacing=5))

    # Helper to update a row visually
    def update_row(row_index):
        for i in range(WORD_LEN):
            letter = guesses[row_index][i]
            img = grid[row_index][i].content  # get the ft.Image
            if letter == "":
                img.src = f"letters/{letter}.png"
            else:
                img.src = f"letters/{letter}.png"
        page.update()

    # Handle guess submission
    def submit_guess():
        nonlocal current_row
        guess_word = "".join(guesses[current_row])
        if len(guess_word) < WORD_LEN:
            page.snack_bar = ft.SnackBar(ft.Text("Palavra incompleta!"))
            page.snack_bar.open = True
            page.update()
            return

        print("Guess submitted:", guess_word)
        # TODO: check guess logic here

        current_row += 1
        if current_row >= NUM_ROWS:
            page.snack_bar = ft.SnackBar(ft.Text("Fim do jogo!"))
            page.snack_bar.open = True
            page.update()

    # Handle keyboard input
    def on_keyboard(e: ft.KeyboardEvent):
        nonlocal current_row
        if current_row >= NUM_ROWS:
            return  # game over

        key = e.key.upper()

        if key in string.ascii_uppercase:
            # Add letter if space available
            for i in range(WORD_LEN):
                if guesses[current_row][i] == "":
                    guesses[current_row][i] = key
                    break
        elif key == "BACKSPACE":
            # Delete last filled letter
            for i in range(WORD_LEN - 1, -1, -1):
                if guesses[current_row][i] != "":
                    guesses[current_row][i] = ""
                    break
        elif key == "ENTER":
            submit_guess()

        update_row(current_row)

    # Add a submit button too
    page.add(ft.ElevatedButton("Enviar", on_click=lambda e: submit_guess()))

    # Enable keyboard listening
    page.on_keyboard_event = on_keyboard

    page.update()


ft.app(target=main, assets_dir="assets")
