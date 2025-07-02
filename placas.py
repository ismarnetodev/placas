import customtkinter as ctk
import tkinter as tk
import json
import os
import re

# Configura o modo de aparência para escuro
ctk.set_appearance_mode('dark')

# Inicializa a aplicação CustomTkinter
app = ctk.CTk()
app.title("Login e Cadastro de Placas")
# Define a janela em tela cheia
app.attributes('-fullscreen', True)
# Define o tamanho inicial da janela (será ignorado em tela cheia, mas útil para testes)
app.geometry('410x400')

# Cria frames para diferentes seções da aplicação
pagina_saldo = ctk.CTkFrame(app) # Este frame não está sendo usado no fluxo atual, mas pode ser para futuras expansões
scroll_frame_conversor = ctk.CTkScrollableFrame(app) # Frame para a seção de cadastro de placas

# Define o nome do arquivo para armazenar os dados dos usuários
ARQUIVO_USUARIOS = "usuarios.json"

# Variável global para armazenar o usuário logado
usuario_logado = None

# Função para carregar usuários do arquivo JSON
def carregar_usuarios():
    # Verifica se o arquivo de usuários existe
    if not os.path.exists(ARQUIVO_USUARIOS):
        # Se não existir, cria um arquivo vazio com um objeto JSON vazio
        with open(ARQUIVO_USUARIOS, "w") as f:
            json.dump({}, f)
    # Abre o arquivo e carrega os dados dos usuários
    with open(ARQUIVO_USUARIOS, "r") as f:
        return json.load(f)

# Função para salvar usuários no arquivo JSON
def salvar_usuarios(usuarios):
    # Abre o arquivo e salva os dados dos usuários com indentação para melhor leitura
    with open(ARQUIVO_USUARIOS, "w") as f:
        json.dump(usuarios, f, indent=4)

# Função para verificar as credenciais de login
def verificar_login(usuario, senha):
    usuarios = carregar_usuarios()
    # Retorna True se o usuário existe e a senha corresponde
    return usuario in usuarios and usuarios[usuario]["senha"] == senha

# Função para cadastrar um novo usuário
def cadastrar_usuario(usuario, senha):
    usuarios = carregar_usuarios()
    # Verifica se o usuário já existe
    if usuario in usuarios:
        return False # Usuário já existe
    # Adiciona o novo usuário com a senha
    usuarios[usuario] = {"senha": senha}
    salvar_usuarios(usuarios) # Salva os usuários atualizados
    return True # Cadastro realizado com sucesso

# Função de validação para permitir apenas letras no campo de nome de usuário
def apenas_leitura(entry_value):
    return entry_value.isalpha() or entry_value == ""

# Função para validar o login e alternar para a tela de cadastro de placas
def validar_login():
    global usuario_logado
    usuario = campo_nome.get()
    senha = campo_password.get()

    if verificar_login(usuario, senha):
        usuario_logado = usuario # Define o usuário logado
        # Esconde os widgets da tela de login
        for widget in [campo_user, campo_nome, campo_senha, campo_password, botoao_login, botao_cadastro, mostrar_senha, frame_login]:
            widget.pack_forget()
        # Exibe os frames da aplicação após o login
        pagina_saldo.pack(pady=20) # Pode ser usado para exibir informações do usuário
        scroll_frame_conversor.pack(fill="both", expand=True)
    else:
        verdade.configure(text='Login negado!', text_color="red") # Mensagem de erro de login

# Função para realizar o cadastro de um novo usuário
def cadastrar():
    usuario = campo_nome.get()
    senha = campo_password.get()

    if cadastrar_usuario(usuario, senha):
        verdade.configure(text='Cadastro feito!', text_color='green') # Mensagem de sucesso no cadastro
    else:
        verdade.configure(text="O usuário já existe!", text_color='orange') # Mensagem de erro no cadastro

# Função para alternar a visibilidade da senha
def alternar_senha():
    if mostrar_var.get() == 1:
        campo_password.configure(show="") # Mostra a senha
    else:
        campo_password.configure(show="*") # Esconde a senha com asteriscos

# Função para sair da tela cheia ao pressionar Esc
def sair_tela_cheia(event=None):
    app.attributes('-fullscreen', False)

# Função de validação para permitir apenas caracteres alfanuméricos na placa
def validar_placa_input(texto):
    # Permite apenas letras maiúsculas, minúsculas e números
    return re.fullmatch(r'[A-Za-z0-9]*', texto) is not None

# Função para armazenar as placas no arquivo json
def verificar_placa(): 

    if not os.path.exists(ARQUIVO_USUARIOS):
        with open(ARQUIVO_USUARIOS, 'w') as f:
            json.dump({}, f)

    with open(ARQUIVO_USUARIOS, "r") as f:
        return json.load(f)
# Registra as placas no json
def registro_placa():
    global usuario_logado
    placa = placa_cadastro.get().upper()
    usuarios = carregar_usuarios()

    if placa in usuarios[usuario_logado].get("placas", []):
        return False 

    usuarios[usuario_logado].setdefault("placas", []).append(placa)
    salvar_usuarios(usuarios)
    return True

# Função para identificar o tipo de placa (Mercosul ou Cinza)
def identificar_tipo_placa():
    placa = placa_cadastro.get().upper() # Pega o texto do campo da placa e converte para maiúsculas
    
    # Padrão Mercosul: 3 letras, 1 número, 1 letra, 2 números (ex: ABC1D23)
    padrao_mercosul = r'^[A-Z]{3}\d[A-Z]\d{2}$'
    # Padrão Placa Cinza (antigo): 3 letras, 4 números (ex: ABC1234)
    padrao_cinza = r'^[A-Z]{3}\d{4}$'

    if mercosul_var.get() == 1 and placa_cinza_var.get() == 1:
        resultado_placa.configure(text="Selecione apenas um tipo de placa (Mercosul ou Cinza).", text_color="orange")
    elif mercosul_var.get() == 1:
        if re.fullmatch(padrao_mercosul, placa):
            resultado_placa.configure(text=f"Placa '{placa}' é VÁLIDA para o padrão Mercosul.", text_color="green")
        else:
            resultado_placa.configure(text=f"Placa '{placa}' é INVÁLIDA para o padrão Mercosul.", text_color="red")
    elif placa_cinza_var.get() == 1:
        if re.fullmatch(padrao_cinza, placa):
            resultado_placa.configure(text=f"Placa '{placa}' é VÁLIDA para o padrão Placa Cinza.", text_color="green")
        else:
            resultado_placa.configure(text=f"Placa '{placa}' é INVÁLIDA para o padrão Placa Cinza.", text_color="red")
    else:
        resultado_placa.configure(text="Selecione o tipo de placa (Mercosul ou Cinza).", text_color="blue")

# Associa a tecla Esc à função para sair da tela cheia
app.bind("<Escape>", sair_tela_cheia)

# Registra as funções de validação para os campos de entrada
vcmd_nome = app.register(apenas_leitura)
vcmd_placa = app.register(validar_placa_input)

# Cria o frame de login
frame_login = ctk.CTkFrame(app)
frame_login.pack(expand=True)

# Widgets da tela de login
ctk.CTkLabel(frame_login, text='Bem vindo!', text_color='blue', font=ctk.CTkFont(size=24, weight='bold')).pack(pady=20)

campo_user = ctk.CTkLabel(app, text='Usuário:')
campo_user.pack(pady=5)

campo_nome = ctk.CTkEntry(app, placeholder_text="Digite seu usuário", validate="key", validatecommand=(vcmd_nome, "%P"))
campo_nome.pack(pady=5)

campo_senha = ctk.CTkLabel(app, text="Senha:")
campo_senha.pack(pady=10)

campo_password = ctk.CTkEntry(app, placeholder_text="Digite sua senha", show="*")
campo_password.pack(pady=5)

mostrar_var= tk.IntVar()
mostrar_senha= ctk.CTkCheckBox(app, text="Mostrar Senha", variable=mostrar_var, command=alternar_senha)
mostrar_senha.pack(padx=10, pady=10)

botoao_login = ctk.CTkButton(app, text='Login', command=validar_login)
botoao_login.pack(pady=10)

botao_cadastro = ctk.CTkButton(app, text='Cadastrar', command=cadastrar)
botao_cadastro.pack(pady=5)

verdade = ctk.CTkLabel(app, text='')
verdade.pack(pady=10)

# Widgets da tela de cadastro de placas (visível após o login)
label_saldo = ctk.CTkLabel(pagina_saldo, text="")
label_saldo.pack(pady=20)

titulo= ctk.CTkLabel(scroll_frame_conversor, text="Cadastro e Validação de Placas", font=ctk.CTkFont(size=18, weight='bold'))
titulo.pack(padx=10, pady=10)

ctk.CTkLabel(scroll_frame_conversor, text="Escreva a placa do carro desejado:", font=ctk.CTkFont(size=15)).pack(pady=5)

placa_cadastro = ctk.CTkEntry(
    scroll_frame_conversor,
    placeholder_text="Ex: ABC1D23 ou ABC1234",
    validate="key",
    validatecommand=(vcmd_placa, "%P"),
    width=250
)
placa_cadastro.pack(pady=5)

# Variáveis para os Checkboxes
mercosul_var = tk.IntVar()
placa_cinza_var = tk.IntVar()

# Funções para garantir que apenas um checkbox seja selecionado
def on_mercosul_check():
    if mercosul_var.get() == 1:
        placa_cinza_var.set(0) # Desmarca o outro checkbox
        resultado_placa.configure(text="") # Limpa a mensagem de erro
    
def on_cinza_check():
    if placa_cinza_var.get() == 1:
        mercosul_var.set(0) # Desmarca o outro checkbox
        resultado_placa.configure(text="") # Limpa a mensagem de erro

mercosul = ctk.CTkCheckBox(scroll_frame_conversor, text="Padrão Mercosul (LLLNLNN)", variable=mercosul_var, command=on_mercosul_check)
mercosul.pack(pady=5)

placa_cinza = ctk.CTkCheckBox(scroll_frame_conversor, text="Padrão Antigo (LLLNNNN)", variable=placa_cinza_var, command=on_cinza_check)
placa_cinza.pack(pady=5)

# Botão para validar a placa
botao_validar_placa = ctk.CTkButton(scroll_frame_conversor, text='Validar Placa', command=identificar_tipo_placa)
botao_validar_placa.pack(pady=10)

# Label para exibir o resultado da validação da placa
resultado_placa = ctk.CTkLabel(scroll_frame_conversor, text='')
resultado_placa.pack(pady=10)

botao_registrar_placa = ctk.CTkButton(scroll_frame_conversor, text="Registrar Placa", command=registro_placa)
botao_registrar_placa.pack(pady=5)

# Inicia o loop principal da aplicação
app.mainloop()