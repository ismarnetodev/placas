import customtkinter as ctk
import tkinter as tk
import json 
import os

ctk.set_appearance_mode('dark')

app = ctk.CTk()
app.geometry('410x400')
app.title("Sistema de controle de carros")
app.attributes('-fullscreen', True)

ARQUIVO_USUARIOS = "usuarios.json"

usuario_logado = None

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

def apenas_leitura(entry_value):
    return entry_value.isalpha() or entry_value == "" 

def validar_login():
    global usuario_logado
    usuario = campo_nome.get()
    senha = campo_password.get()
    

    if verificar_login(usuario, senha):
        usuario_logado = usuario
        verdade.configure(text="Seja bem vindo {}!".format(usuario))
               

    else:
        verdade.configure(text='Login negado!', text_color="red")

def cadastrar():
    usuario = campo_nome.get()
    senha = campo_password.get()

def alternar_senha():
    if mostrar_var.get() == 1:
        campo_password.configure(show="")
    else:
        campo_password.configure(show="*")    

def sair_tela_cheia(event=None):
    app.attributes('-fullscreen', False)


app.bind("<Escape>", sair_tela_cheia)

frame_login = ctk.CTkFrame(app)
frame_login.pack()

ctk.CTkLabel(frame_login, text='Bem vindo!', font=ctk.CTkFont(size=24, weight='bold')).pack(pady=20)

campo_user = ctk.CTkLabel(app, text='Usuario:')
campo_user.pack(pady=10)

campo_nome = ctk.CTkEntry(app, placeholder_text='Seu nome')
campo_nome.pack(pady=5)

campo_senha = ctk.CTkLabel(app, text='Senha:')
campo_senha.pack(pady=5)

campo_password = ctk.CTkEntry(app, placeholder_text="Digite sua senha", show="*")
campo_password.pack(pady=5)

mostrar_var= tk.IntVar()
mostrar_senha= ctk.CTkCheckBox(app, text="Mostrar Senha", variable=mostrar_var, command=alternar_senha)
mostrar_senha.pack(padx=10, pady=10)

botoao_login = ctk.CTkButton(app, text='login', command=validar_login)
botoao_login.pack(pady=10)

botao_cadastro = ctk.CTkButton(app, text='Cadastrar', command=cadastrar)
botao_cadastro.pack(pady=5)

verdade = ctk.CTkLabel(app, text='')
verdade.pack(pady=10)        

app.mainloop()