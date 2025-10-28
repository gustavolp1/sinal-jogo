import flet as ft
import string
import random

def main(page: ft.Page):
    page.title = "Sinal - Jogo"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = "light"
    page.window_width = 450
    page.window_height = 700
    page.bgcolor = "#f5f5f5"

    # Constants
    NUM_ROWS = 6
    WORD_LEN = 5
    LETTERS = list(string.ascii_uppercase)

    # === GAME STATE ===
    current_row = 0
    guesses = []
    grid = []
    keyboard_keys = {}
    target_word = ""

    # === LOAD WORD LISTS ===
    with open("answer_words.txt", "r", encoding="utf-8") as f:
        answer_words = [w.strip().upper() for w in f.readlines() if len(w.strip()) == WORD_LEN]

    with open("accepted_words.txt", "r", encoding="utf-8") as f:
        accepted_words = [w.strip().upper() for w in f.readlines() if len(w.strip()) == WORD_LEN]

    # === FUNCTIONS ===

    def pick_new_word():
        nonlocal target_word
        target_word = random.choice(answer_words)
        #target_word = "SINAL"
        print("Target word:", target_word)

    def reset_game(e=None):
        nonlocal current_row, guesses
        current_row = 0
        guesses = [["" for _ in range(WORD_LEN)] for _ in range(NUM_ROWS)]
        pick_new_word()

        # Reset grid visuals
        for row in range(NUM_ROWS):
            for col in range(WORD_LEN):
                grid[row][col].bgcolor = ft.Colors.GREY_200
                img = grid[row][col].content
                img.src = "letters/blank.png"

        # Reset keyboard visuals
        for letter in LETTERS:
            keyboard_keys[letter].bgcolor = ft.Colors.WHITE

        page.update()

    def update_row(row_index):
        for i in range(WORD_LEN):
            letter = guesses[row_index][i]
            img = grid[row_index][i].content
            img.src = f"letters/{letter if letter else 'blank'}.png"
        page.update()

    def color_feedback(row_index, guess_word):
        nonlocal target_word
        target_chars = list(target_word)
        colors = [ft.Colors.GREY_400] * WORD_LEN

        # Pass 1: Mark greens
        for i in range(WORD_LEN):
            if guess_word[i] == target_chars[i]:
                colors[i] = ft.Colors.GREEN_400
                target_chars[i] = None

        # Pass 2: Mark yellows
        for i in range(WORD_LEN):
            if colors[i] == ft.Colors.GREEN_400:
                continue
            if guess_word[i] in target_chars:
                colors[i] = ft.Colors.AMBER_300
                target_chars[target_chars.index(guess_word[i])] = None

        # Apply colors to grid and keyboard
        for i in range(WORD_LEN):
            grid[row_index][i].bgcolor = colors[i]
            letter = guess_word[i]
            update_keyboard_color(letter, colors[i])

        page.update()

    def update_keyboard_color(letter, new_color):
        """Updates the keyboard key color but keeps the 'highest' status (green > yellow > gray > white)."""
        key = keyboard_keys[letter]
        current = key.bgcolor
        priority = {
            ft.Colors.WHITE: 0,
            ft.Colors.GREY_400: 1,
            ft.Colors.AMBER_300: 2,
            ft.Colors.GREEN_400: 3,
        }
        if priority[new_color] > priority.get(current, 0):
            key.bgcolor = new_color

    def submit_guess(e=None):
        nonlocal current_row
        guess_word = "".join(guesses[current_row])
        if len(guess_word) < WORD_LEN:
            page.snack_bar = ft.SnackBar(ft.Text("Palavra incompleta!"))
            page.snack_bar.open = True
            page.update()
            return

        if guess_word not in accepted_words and guess_word not in answer_words:
            page.snack_bar = ft.SnackBar(ft.Text("Palavra inválida!"))
            page.snack_bar.open = True
            page.update()
            return

        color_feedback(current_row, guess_word)

        if guess_word == target_word:
            page.snack_bar = ft.SnackBar(ft.Text("🎉 Você acertou!"))
            page.snack_bar.open = True
            page.update()
            return

        current_row += 1
        if current_row >= NUM_ROWS:
            page.snack_bar = ft.SnackBar(ft.Text(f"Fim do jogo! A palavra era {target_word}."))
            page.snack_bar.open = True
            page.update()

    def on_keyboard(e: ft.KeyboardEvent):
        nonlocal current_row
        if current_row >= NUM_ROWS:
            return

        key = e.key.upper()

        if key in string.ascii_uppercase:
            for i in range(WORD_LEN):
                if guesses[current_row][i] == "":
                    guesses[current_row][i] = key
                    break
        elif key == "BACKSPACE":
            for i in range(WORD_LEN - 1, -1, -1):
                if guesses[current_row][i] != "":
                    guesses[current_row][i] = ""
                    break
        elif key == "ENTER":
            submit_guess()

        update_row(current_row)

    def click_keyboard_letter(letter):
        """Called when on-screen keyboard key is clicked."""
        nonlocal current_row
        if current_row >= NUM_ROWS:
            return
        if letter == "ENTER":
            submit_guess()
            return
        elif letter == "⌫":
            for i in range(WORD_LEN - 1, -1, -1):
                if guesses[current_row][i] != "":
                    guesses[current_row][i] = ""
                    break
            update_row(current_row)
            return
        else:
            for i in range(WORD_LEN):
                if guesses[current_row][i] == "":
                    guesses[current_row][i] = letter
                    break
            update_row(current_row)

    # === INFO POPUP ===

    def open_info(e):
        print("Info button clicked!")
        if info_dialog not in page.overlay:
            page.overlay.append(info_dialog)
        info_dialog.open = True
        page.update()

    def close_info(e):
        info_dialog.open = False
        page.update()

    info_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Como jogar", weight="bold", size=18),
        content=ft.Column(
            [
                ft.Text("O objetivo do jogo é adivinhar a palavra de 5 sinais em até 6 tentativas."),
                ft.Text("Cada tentativa deve ser uma palavra válida em Português, digitada com sinais de Libras."),
                ft.Text("Após cada tentativa, as cores dos quadrados mudarão para mostrar o quão perto você está da resposta:"),
                ft.Row([ft.Image(src="example_green.png", width=210, height=45), ft.Text("Um sinal na posição correta e um que existe na palavra, mas na posição incorreta.")]),
                ft.Row([ft.Image(src="example_yellow.png", width=210, height=45), ft.Text("Três sinais que existem na palavra, todos nas posições incorretas.")]),
                ft.Row([ft.Image(src="example_gray.png", width=210, height=45), ft.Text("Nenhum dos sinais aparece na palavra.")]),
                ft.Container(height=10),
                ft.Text("Use o teclado na tela (ou o do seu computador) para inserir os sinais correspondentes às letras."),
                ft.Text("Boa sorte! 🤟"),
            ],
            tight=True,
            scroll=ft.ScrollMode.AUTO,
        ),
        actions=[ft.TextButton("Fechar", on_click=close_info)],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    # === INFO BUTTON ON TOP RIGHT ===
    info_button = ft.IconButton(
        icon=ft.Icons.INFO_OUTLINE,
        tooltip="Como jogar",
        on_click=open_info,
    )

    # Add info button aligned top-right
    page.add(
        ft.Row(
            [ft.Container(expand=True), info_button],
            alignment="end",
            vertical_alignment="start",
        )
    )

    # === UI CONSTRUCTION ===

    # Logo
    page.add(
        ft.Image(
            src="sinal_logo.png",
            width=200,
            height=100,
            fit=ft.ImageFit.CONTAIN,
        )
    )

    # Build letter grid
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
        page.add(ft.Row(row_controls, alignment="center", spacing=5))

    # Buttons for submit & reset
    buttons_row = ft.Row(
        [
            ft.ElevatedButton("🔄 Novo jogo", on_click=reset_game)
        ],
        alignment="center",
        spacing=10,
    )
    page.add(buttons_row)

    # Build on-screen keyboard layout (3 rows)
    layout = ["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM"]
    keyboard_rows = []
    for row_letters in layout:
        row_controls = []
        for letter in row_letters:
            img = ft.Image(src=f"letters/{letter}.png", width=30, height=30, fit=ft.ImageFit.CONTAIN)
            btn = ft.Container(
                content=img,
                width=40,
                height=50,
                bgcolor=ft.Colors.WHITE,
                border=ft.border.all(2, ft.Colors.GREY_400),  # outline added
                border_radius=6,
                alignment=ft.alignment.center,
                on_click=lambda e, l=letter: click_keyboard_letter(l),
            )
            keyboard_keys[letter] = btn
            row_controls.append(btn)
        keyboard_rows.append(ft.Row(row_controls, alignment="center", spacing=4))

    # Bottom control keys row (ENTER and Backspace only)
    special_keys = [
        ft.Container(
            content=ft.Text("ENTER", size=12),
            width=60,
            height=50,
            bgcolor=ft.Colors.GREY_300,
            border=ft.border.all(2, ft.Colors.GREY_400),  # outline added
            border_radius=6,
            alignment=ft.alignment.center,
            on_click=lambda e: click_keyboard_letter("ENTER"),
        ),
        ft.Container(
            content=ft.Text("⌫", size=18),
            width=40,
            height=50,
            bgcolor=ft.Colors.GREY_300,
            border=ft.border.all(2, ft.Colors.GREY_400),  # outline added
            border_radius=6,
            alignment=ft.alignment.center,
            on_click=lambda e: click_keyboard_letter("⌫"),
        ),
    ]
    keyboard_rows.append(ft.Row(special_keys, alignment="center", spacing=4))

    # Add keyboard to page
    for row in keyboard_rows:
        page.add(row)

    # Enable physical keyboard too
    page.on_keyboard_event = on_keyboard

    # Start a new game
    pick_new_word()
    reset_game()

    page.update()


ft.app(target=main, assets_dir="assets")
