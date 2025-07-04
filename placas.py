import customtkinter as ctk
import tkinter as tk
import json
import os
import re
import cv2
import pytesseract
import numpy as np
import threading

# Configurações iniciais
ctk.set_appearance_mode('dark')
try:
    ctk.set_default_color_theme("tema.json")
except Exception as e:
    print(f"Erro ao carregar o tema: {e}")

app = ctk.CTk()
app.title("Login e Cadastro de Placas")
app.attributes('-fullscreen', True)
app.geometry('410x600')

pagina_saldo = ctk.CTkFrame(app)
scroll_frame_conversor = ctk.CTkScrollableFrame(app)

ARQUIVO_USUARIOS = "usuarios.json"
usuario_logado = None
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)

# --- Funções OCR ---
def preProcessForContours(frame):
    imgGray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    imgBlur = cv2.GaussianBlur(imgGray, (5,5), 1)
    imgCanny = cv2.Canny(imgBlur, 100, 200)
    kernel = np.ones((5,5),np.uint8)
    imgDilate = cv2.dilate(imgCanny, kernel, iterations=1)
    imgThresh = cv2.erode(imgDilate, kernel, iterations=1)
    return imgThresh

def preprocessForOCR(image_roi):
    cinza = cv2.cvtColor(image_roi, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    cinza = clahe.apply(cinza)
    _, binarizada = cv2.threshold(cinza, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
    processada = cv2.morphologyEx(binarizada, cv2.MORPH_CLOSE, kernel)
    return processada

def identificar_tipo_placa_texto(placa):
    placa = placa.upper()
    padrao_mercosul = r'^[A-Z]{3}\d[A-Z]\d{2}$'
    padrao_cinza = r'^[A-Z]{3}\d{4}$'
    if re.match(padrao_mercosul, placa):
        return "Mercosul"
    elif re.match(padrao_cinza, placa):
        return "Cinza"
    return "Invalida"

def iniciar_ocr():
    global camera
    placa_detectada = False
    text = ""

    while True:
        ret, frame = camera.read()
        if not ret:
            print("Erro ao ler frame")
            break

        frame = cv2.resize(frame, (640, 480))
        imgContours = preProcessForContours(frame)
        contours, _ = cv2.findContours(imgContours, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if 2000 < area < 20000:
                x, y, w, h = cv2.boundingRect(cnt)
                aspect_ratio = float(w) / h
                if 2.0 < aspect_ratio < 4.0:
                    margin = 5
                    roi = frame[max(0, y - margin):min(frame.shape[0], y + h + margin),
                                max(0, x - margin):min(frame.shape[1], x + w + margin)]
                    if roi.size > 0:
                        processed_roi = preprocessForOCR(roi)
                        config = r'--oem 3 --psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
                        text = pytesseract.image_to_string(processed_roi, lang="eng", config=config)
                        text = ''.join(c for c in text.strip().replace("\n", "").replace(" ", "") if c.isalnum()).upper()
                        if 7 <= len(text) <= 8 and all(c.isalnum() for c in text):
                            placa_detectada = True
                            break

        cv2.imshow('OCR Live', frame)
        cv2.imshow('Contours', imgContours)

        if placa_detectada:
            tipo = identificar_tipo_placa_texto(text)
            placa_cadastro.delete(0, tk.END)
            placa_cadastro.insert(0, text)
            ocr_label.configure(text=f"Placa Detectada: {text} - Tipo: {tipo}", text_color="green")
            break

        if cv2.waitKey(1) & 0xFF == 27:
            break

    cv2.destroyAllWindows()

def ao_fechar():
    camera.release()
    cv2.destroyAllWindows()
    app.destroy()

def carregar_usuarios():
    if not os.path.exists(ARQUIVO_USUARIOS):
        with open(ARQUIVO_USUARIOS, "w") as f:
            json.dump({}, f)
    with open(ARQUIVO_USUARIOS, "r") as f:
        return json.load(f)

def salvar_usuarios(usuarios):
    with open(ARQUIVO_USUARIOS, "w") as f:
        json.dump(usuarios, f, indent=4)

def verificar_login(usuario, senha):
    usuarios = carregar_usuarios()
    return usuario in usuarios and usuarios[usuario]["senha"] == senha

def cadastrar_usuario(usuario, senha):
    usuarios = carregar_usuarios()
    if usuario in usuarios:
        return False
    usuarios[usuario] = {"senha": senha}
    salvar_usuarios(usuarios)
    return True

def apenas_leitura(entry_value):
    return entry_value.isalpha() or entry_value == ""

def validar_placa_input(texto):
    return re.fullmatch(r'[A-Za-z0-9]*', texto) is not None

def validar_login():
    global usuario_logado
    usuario = campo_nome.get()
    senha = campo_password.get()
    if verificar_login(usuario, senha):
        usuario_logado = usuario
        for widget in [campo_user, campo_nome, campo_senha, campo_password, botoao_login, botao_cadastro, mostrar_senha, frame_login]:
            widget.pack_forget()
        pagina_saldo.pack(pady=20)
        scroll_frame_conversor.pack(fill="both", expand=True)
    else:
        verdade.configure(text='Login negado!', text_color="red")

def cadastrar():
    usuario = campo_nome.get()
    senha = campo_password.get()
    if cadastrar_usuario(usuario, senha):
        verdade.configure(text='Cadastro feito!', text_color='green')
    else:
        verdade.configure(text="O usuário já existe!", text_color='orange')

def alternar_senha():
    campo_password.configure(show="" if mostrar_var.get() == 1 else "*")

def registro_placa():
    global usuario_logado
    placa = placa_cadastro.get().upper()
    usuarios = carregar_usuarios()
    if placa in usuarios[usuario_logado].get("placas", []):
        return False
    usuarios[usuario_logado].setdefault("placas", []).append(placa)
    salvar_usuarios(usuarios)
    return True

def identificar_tipo_placa():
    placa = placa_cadastro.get().upper()
    padrao_mercosul = r'^[A-Z]{3}\d[A-Z]\d{2}$'
    padrao_cinza = r'^[A-Z]{3}\d{4}$'

    if mercosul_var.get() == 1 and placa_cinza_var.get() == 1:
        resultado_placa.configure(text="Selecione apenas um tipo de placa", text_color="orange")
    elif mercosul_var.get() == 1:
        if re.fullmatch(padrao_mercosul, placa):
            resultado_placa.configure(text=f"Placa válida (Mercosul)", text_color="green")
        else:
            resultado_placa.configure(text=f"Placa inválida (Mercosul)", text_color="red")
    elif placa_cinza_var.get() == 1:
        if re.fullmatch(padrao_cinza, placa):
            resultado_placa.configure(text=f"Placa válida (Cinza)", text_color="green")
        else:
            resultado_placa.configure(text=f"Placa inválida (Cinza)", text_color="red")
    else:
        resultado_placa.configure(text="Selecione o tipo de placa", text_color="blue")

app.bind("<Escape>", lambda event: app.attributes("-fullscreen", False))
vcmd_nome = app.register(apenas_leitura)
vcmd_placa = app.register(validar_placa_input)

frame_login = ctk.CTkFrame(app)
frame_login.pack(expand=True)

ctk.CTkLabel(frame_login, text='Bem vindo!', text_color='blue', font=ctk.CTkFont(size=24, weight='bold')).pack(pady=20)

campo_user = ctk.CTkLabel(app, text='Usuário:')
campo_user.pack(pady=5)

campo_nome = ctk.CTkEntry(app, placeholder_text="Digite seu usuário", validate="key", validatecommand=(vcmd_nome, "%P"))
campo_nome.pack(pady=5)

campo_senha = ctk.CTkLabel(app, text="Senha:")
campo_senha.pack(pady=10)

campo_password = ctk.CTkEntry(app, placeholder_text="Digite sua senha", show="*")
campo_password.pack(pady=5)

mostrar_var = tk.IntVar()
mostrar_senha = ctk.CTkCheckBox(app, text="Mostrar Senha", variable=mostrar_var, command=alternar_senha)
mostrar_senha.pack(pady=10)

botoao_login = ctk.CTkButton(app, text='Login', command=validar_login)
botoao_login.pack(pady=10)

botao_cadastro = ctk.CTkButton(app, text='Cadastrar', command=cadastrar)
botao_cadastro.pack(pady=5)

verdade = ctk.CTkLabel(app, text='')
verdade.pack(pady=10)

ctk.CTkLabel(pagina_saldo, text="Cadastre sua placa").pack(pady=20)

titulo = ctk.CTkLabel(scroll_frame_conversor, text="Cadastro e Validação de Placas", font=ctk.CTkFont(size=18, weight='bold'))
titulo.pack(padx=10, pady=10)

ctk.CTkLabel(scroll_frame_conversor, text="Digite a placa do carro:").pack(pady=5)

placa_cadastro = ctk.CTkEntry(scroll_frame_conversor, placeholder_text="ABC1D23 ou ABC1234", validate="key", validatecommand=(vcmd_placa, "%P"), width=250)
placa_cadastro.pack(pady=5)

mercosul_var = tk.IntVar()
placa_cinza_var = tk.IntVar()

def on_mercosul_check():
    if mercosul_var.get() == 1:
        placa_cinza_var.set(0)
        resultado_placa.configure(text="")

def on_cinza_check():
    if placa_cinza_var.get() == 1:
        mercosul_var.set(0)
        resultado_placa.configure(text="")

ctk.CTkCheckBox(scroll_frame_conversor, text="Padrão Mercosul (LLLNLNN)", variable=mercosul_var, command=on_mercosul_check).pack(pady=5)
ctk.CTkCheckBox(scroll_frame_conversor, text="Padrão Antigo (LLLNNNN)", variable=placa_cinza_var, command=on_cinza_check).pack(pady=5)

botao_validar_placa = ctk.CTkButton(scroll_frame_conversor, text='Validar Placa', command=identificar_tipo_placa)
botao_validar_placa.pack(pady=10)

resultado_placa = ctk.CTkLabel(scroll_frame_conversor, text='')
resultado_placa.pack(pady=10)

ocr_label = ctk.CTkLabel(scroll_frame_conversor, text="")
ocr_label.pack(pady=5)

botao_registrar_placa = ctk.CTkButton(scroll_frame_conversor, text="Registrar Placa", command=registro_placa)
botao_registrar_placa.pack(pady=5)

botao_ocr = ctk.CTkButton(scroll_frame_conversor, text="Detectar Placa com OCR", command=lambda: threading.Thread(target=iniciar_ocr).start())
botao_ocr.pack(pady=5)

app.protocol("WM_DELETE_WINDOW", ao_fechar)
app.mainloop()
