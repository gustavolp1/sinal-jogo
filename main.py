import flet as ft
import string
import random
import time

def main(page: ft.Page):
    page.title = "Sinal - Jogo"
    page.theme_mode = "light"
    page.bgcolor = "#f5f5f5"
    page.padding = 10
    page.vertical_alignment = ft.MainAxisAlignment.SPACE_BETWEEN
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    NUM_ROWS = 6
    WORD_LEN = 5
    LETTERS = list(string.ascii_uppercase)
    VERSION = "RELEASE 1.0.5"

    current_row = 0
    guesses = []
    grid = []
    keyboard_keys = {}
    target_word = ""
    game_over = False

    # === LOAD WORD LISTS ===
    try:
        with open("answer_words.txt", "r", encoding="utf-8") as f:
            answer_words = [w.strip().upper() for w in f.readlines() if len(w.strip()) == WORD_LEN]
        with open("accepted_words.txt", "r", encoding="utf-8") as f:
            accepted_words = [w.strip().upper() for w in f.readlines() if len(w.strip()) == WORD_LEN]
        if not answer_words:
            raise FileNotFoundError("Lista de respostas está vazia.")
    except FileNotFoundError:
        page.clean()
        page.add(ft.Text("Erro: arquivos de palavras não encontrados.", color="red"))
        return

    # === GAME LOGIC ===
    def pick_new_word():
        nonlocal target_word
        target_word = random.choice(answer_words)
        print("Target word:", target_word)

    def show_end_game_dialog(won: bool):
        msg = f"🎉 Você acertou! A palavra era {target_word}" if won else f"❌ Fim do jogo! A palavra era {target_word}."
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Fim do jogo", weight="bold"),
            content=ft.Text(msg),
            actions=[ft.TextButton("Fechar", on_click=lambda e: close_dialog(dlg))],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        if dlg not in page.overlay:
            page.overlay.append(dlg)
        page.dialog = dlg
        dlg.open = True
        page.update()

    def close_dialog(dlg):
        dlg.open = False
        page.update()

    def reset_game(e=None):
        nonlocal current_row, guesses, game_over
        current_row = 0
        game_over = False
        guesses[:] = [["" for _ in range(WORD_LEN)] for _ in range(NUM_ROWS)]
        pick_new_word()

        for row in range(NUM_ROWS):
            for col in range(WORD_LEN):
                grid[row][col].bgcolor = ft.Colors.GREY_200
                grid[row][col].content.src = "letters/blank.png"
                grid[row][col].border = ft.border.all(2, ft.Colors.GREY_400)
                grid[row][col].scale = 1.0
        for letter in LETTERS:
            keyboard_keys[letter].bgcolor = ft.Colors.WHITE
        page.update()

    def update_row(row_index):
        for i in range(WORD_LEN):
            letter = guesses[row_index][i]
            img = grid[row_index][i].content
            img.src = f"letters/{letter if letter else 'blank'}.png"
            grid[row_index][i].scale = 1.1 if letter else 1.0
            grid[row_index][i].border = ft.border.all(2, ft.Colors.BLACK if letter else ft.Colors.GREY_400)
        page.update()
        time.sleep(0.05)
        for i in range(WORD_LEN):
            grid[row_index][i].scale = 1.0
        page.update()

    def color_feedback(row_index, guess_word):
        nonlocal target_word
        target_chars = list(target_word)
        colors = [ft.Colors.GREY_400] * WORD_LEN
        for i in range(WORD_LEN):
            if guess_word[i] == target_chars[i]:
                colors[i] = ft.Colors.GREEN_400
                target_chars[i] = None
        for i in range(WORD_LEN):
            if colors[i] == ft.Colors.GREEN_400:
                continue
            if guess_word[i] in target_chars:
                colors[i] = ft.Colors.AMBER_300
                target_chars[target_chars.index(guess_word[i])] = None
        for i in range(WORD_LEN):
            grid[row_index][i].bgcolor = colors[i]
            grid[row_index][i].border = None
            update_keyboard_color(guess_word[i], colors[i])
        page.update()

    def update_keyboard_color(letter, new_color):
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

    def flash_invalid_row():
        for _ in range(2):
            for i in range(WORD_LEN):
                grid[current_row][i].bgcolor = ft.Colors.RED_300
                grid[current_row][i].scale = 1.05
            page.update()
            time.sleep(0.1)
            for i in range(WORD_LEN):
                grid[current_row][i].bgcolor = ft.Colors.GREY_200
                grid[current_row][i].scale = 1.0
            page.update()
            time.sleep(0.1)

    def submit_guess(e=None):
        nonlocal current_row, game_over
        if game_over:
            return
        guess_word = "".join(guesses[current_row])
        if len(guess_word) < WORD_LEN or (guess_word not in accepted_words and guess_word not in answer_words):
            flash_invalid_row()
            return
        color_feedback(current_row, guess_word)
        if guess_word == target_word:
            game_over = True
            time.sleep(0.4)
            show_end_game_dialog(True)
            return
        current_row += 1
        if current_row >= NUM_ROWS:
            game_over = True
            time.sleep(0.4)
            show_end_game_dialog(False)

    def on_keyboard(e: ft.KeyboardEvent):
        nonlocal current_row, game_over
        if game_over or current_row >= NUM_ROWS:
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
            return
        update_row(current_row)

    def click_keyboard_letter(letter):
        nonlocal current_row
        if game_over or current_row >= NUM_ROWS:
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

    # === INFO POPUP: defined once ===
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

    # Robust open_info: ensure overlay contains dialog AND assign to page.dialog
    def open_info(e=None):
        if info_dialog not in page.overlay:
            page.overlay.append(info_dialog)
        # assign to page.dialog (standard approach)
        page.dialog = info_dialog
        info_dialog.open = True
        page.update()

    # === MAIN LAYOUT ===
    logo = ft.Image(src="sinal_logo.png", width=180, height=80, fit=ft.ImageFit.CONTAIN)

    grid_area = ft.Column(
        [ft.Row([ft.Container(
            width=55,
            height=55,
            bgcolor=ft.Colors.GREY_200,
            border=ft.border.all(2, ft.Colors.GREY_400),
            border_radius=8,
            alignment=ft.alignment.center,
            content=ft.Image(src="letters/blank.png", width=38, height=38, fit=ft.ImageFit.CONTAIN),
            animate_scale=ft.Animation(120, "easeOut")
        ) for _ in range(WORD_LEN)], alignment="center", spacing=4) for _ in range(NUM_ROWS)],
        spacing=5,
        alignment="center"
    )

    grid[:] = [[col for col in row.controls] for row in grid_area.controls]

    keyboard_layout = []
    for row_letters in ["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM"]:
        row_controls = []
        for letter in row_letters:
            img = ft.Image(src=f"letters/{letter}.png", width=25, height=25, fit=ft.ImageFit.CONTAIN)
            btn = ft.Container(
                content=img,
                width=36,
                height=45,
                bgcolor=ft.Colors.WHITE,
                border=ft.border.all(2, ft.Colors.GREY_400),
                border_radius=6,
                alignment=ft.alignment.center,
                on_click=lambda e, l=letter: click_keyboard_letter(l),
                ink=True
            )
            keyboard_keys[letter] = btn
            row_controls.append(btn)
        keyboard_layout.append(ft.Row(row_controls, alignment="center", spacing=3))

    bottom_keys = ft.Row(
        [
            ft.Container(
                content=ft.Text("ENTER", size=11, weight="bold"),
                width=55, height=45,
                bgcolor=ft.Colors.GREY_300,
                border=ft.border.all(2, ft.Colors.GREY_400),
                border_radius=6,
                alignment=ft.alignment.center,
                on_click=lambda e: click_keyboard_letter("ENTER"), ink=True
            ),
            ft.Container(
                content=ft.Text("⌫", size=16),
                width=40, height=45,
                bgcolor=ft.Colors.GREY_300,
                border=ft.border.all(2, ft.Colors.GREY_400),
                border_radius=6,
                alignment=ft.alignment.center,
                on_click=lambda e: click_keyboard_letter("⌫"), ink=True
            )
        ],
        alignment="center",
        spacing=3
    )

    version_label = ft.Container(
        content=ft.Text(VERSION, size=10, color=ft.Colors.GREY_600),
        alignment=ft.alignment.bottom_right,
        padding=ft.padding.only(right=6, bottom=4)
    )

    page.add(
        ft.Stack(
            [
                ft.Column(
                    [
                        ft.Row([logo, ft.IconButton(icon=ft.Icons.INFO_OUTLINE, tooltip="Como jogar", on_click=open_info)],
                               alignment="spaceBetween"),
                        grid_area,
                        ft.ElevatedButton("🔄 Novo jogo", on_click=reset_game),
                        *keyboard_layout,
                        bottom_keys
                    ],
                    horizontal_alignment="center",
                    spacing=6,
                    expand=True,
                    alignment="spaceBetween"
                ),
                version_label
            ]
        )
    )

    page.on_keyboard_event = on_keyboard
    reset_game()
    page.update()

ft.app(target=main, assets_dir="assets")
