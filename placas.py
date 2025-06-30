import customtkinter as ctk
import tkinter as tk
import json
import os

ctk.set_appearance_mode('dark')

app = ctk.CTk()
app.title("Login")
app.attributes('-fullscreen', True)
app.geometry('410x400')

pagina_saldo = ctk.CTkFrame(app)
scroll_frame_conversor = ctk.CTkScrollableFrame(app)

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

def cadastrar_usuario(usuario, senha):
    usuarios = carregar_usuarios()
    if usuario in usuarios:
        return False
    usuarios[usuario] = {"senha": senha}
    salvar_usuarios(usuarios)
    return True

def apenas_leitura(entry_value):
    return entry_value.isalpha() or entry_value == "" 

def validar_login():
    global usuario_logado
    usuario = campo_nome.get()
    senha = campo_password.get()
    

    if verificar_login(usuario, senha):
        usuario_logado = usuario
        verdade.configure(text="Seja bem vindo {}!".format(usuario))
       
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
        verdade.configure(text="O usuario já existe!", text_color='orange')


def alternar_senha():
    if mostrar_var.get() == 1:
        campo_password.configure(show="")
    else:
        campo_password.configure(show="*")    

def sair_tela_cheia(event=None):
    app.attributes('-fullscreen', False)

app.bind("<Escape>", sair_tela_cheia)
vcmd = app.register(apenas_leitura) 

frame_login = ctk.CTkFrame(app)
frame_login.pack(expand=True)

ctk.CTkLabel(frame_login, text='Bem vindo!', text_color='Blue', font=ctk.CTkFont(size=24, weight='bold')).pack(pady=20)
ctk.CTkLabel(scroll_frame_conversor, text="Selecione a moeda para converte-la!", font=ctk.CTkFont(size=15, weight='bold')).pack(pady=15)

campo_user = ctk.CTkLabel(app, text='Usuário:')
campo_user.pack(pady=5)

campo_nome = ctk.CTkEntry(app, placeholder_text="Digite seu usuário", validate="key", validatecommand=(vcmd, "%P"))
campo_nome.pack(pady=5)

campo_senha = ctk.CTkLabel(app, text="Senha:")
campo_senha.pack(pady=10)

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

label_saldo = ctk.CTkLabel(pagina_saldo, text="")
label_saldo.pack(pady=20)


titulo= ctk.CTkLabel(scroll_frame_conversor, text="Cadastro de placas")


titulo.pack(padx=10, pady=10)

app.mainloop()