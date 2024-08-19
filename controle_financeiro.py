import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def criar_banco():
    conn = sqlite3.connect('controle_financeiro.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS transacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            descricao TEXT,
            valor REAL,
            tipo TEXT,
            data TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS orçamento (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            valor REAL
        )      
    ''')
    conn.commit()
    conn.close()

criar_banco()

def adicionar_transacao():
    descricao = entry_descricao.get()
    valor = entry_valor.get()
    tipo = combo_tipo.get()
    data = entry_data.get()

    if not descricao or not valor or not tipo or not data:
        messagebox.showwarning("Aviso", "Todos os campos devem ser preenchidos")
        return
    
    try:
        valor = float(valor)
    except ValueError:
        messagebox.showerror("Erro", "O valor deve ser um número")
        return
    
    conn = sqlite3.connect('controle_financeiro.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO transacoes (descricao, valor, tipo, data)
        VALUES (?, ?, ?, ?)
    ''', (descricao, valor, tipo, data))
    conn.commit()
    conn.close()

    entry_descricao.delete(0, tk.END)
    entry_valor.delete(0, tk.END)
    entry_data.delete(0, tk.END)

    messagebox.showinfo("Sucesso", "Transação adicionada com sucesso")
    atualizar_lista()

def remover_transacao():
    selecionado = lista_transacoes.selection()
    if not selecionado:
        messagebox.showwarning("Aviso", "Selecione uma transação para remover")
        return
    
    item_id = lista_transacoes.item(selecionado[0], 'values')[0]

    conn = sqlite3.connect('controle_financeiro.db')
    c = conn.cursor()
    c.execute('DELETE FROM transacoes WHERE id = ?', (item_id,))
    conn.commit()
    conn.close()

    atualizar_lista()
    atualizar_orcamento()

    messagebox.showinfo("Sucesso", "Transação removida com sucesso")

def atualizar_lista():
    for i in lista_transacoes.get_children():
        lista_transacoes.delete(i)

    conn = sqlite3.connect('controle_financeiro.db')
    c = conn.cursor()
    c.execute('SELECT * FROM transacoes')
    transacoes = c.fetchall()
    conn.close()

    for transacao in transacoes:
        lista_transacoes.insert('', 'end', values=transacao)

def gerar_relatorio():
    conn = sqlite3.connect('controle_financeiro.db')
    c = conn.cursor()
    c.execute('SELECT tipo, SUM(valor) FROM transacoes GROUP BY tipo')
    dados = c.fetchall()
    conn.close()

    tipos = [dado[0] for dado in dados]
    valores = [dado[1] for dado in dados]

    fig, ax = plt.subplots()
    ax.bar(tipos, valores, color=['blue', 'red'])
    ax.set_xlabel('Tipo')
    ax.set_ylabel('Valor')
    ax.set_title('Relatório Financeiro')

    canvas = FigureCanvasTkAgg(fig, master=frame_relatorio)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

def definir_orcamento():
    valor_orcamento = entry_orcamento.get()

    if not valor_orcamento:
        messagebox.showwarning("Aviso", "O campo de orçamento deve ser preenchido")
        return
    
    try:
        valor_orcamento = float(valor_orcamento)
    except ValueError:
        messagebox.showerror("Erro", "O valor do orçamento deve ser um número")
        return
    
    conn = sqlite3.connect('controle_financeiro.db')
    c = conn.cursor()
    c.execute('DELETE FROM orçamento')
    c.execute('INSERT INTO orçamento (valor) VALUES (?)', (valor_orcamento,))
    conn.commit()
    conn.close()

    entry_orcamento.delete(0, tk.END)

    messagebox.showinfo("Sucesso", "Orçamento definido com sucesso")
    atualizar_orcamento()

def atualizar_orcamento():
    conn = sqlite3.connect('controle_financeiro.db')
    c = conn. cursor()
    c.execute('SELECT SUM(valor) FROM transacoes WHERE tipo = "Despesa"')
    total_despesas = c.fetchone()[0] or 0
    c.execute('SELECT valor FROM orçamento')
    orcamento = c.fetchone()
    valor_orcamento = orcamento[0] if orcamento else 0
    conn.close()

    label_orcamento.config(text=f'Orçamento: R${valor_orcamento:.2f}')
    label_despesas.config(text=f'Despesas: R${total_despesas:.2f}')
    label_saldo.config(text=f'Saldo: R${valor_orcamento - total_despesas:.2f}')

# Configuração da Interface
root = tk.Tk()
root.title("Controle Financeiro")

# Adicionar Transação 
frame_adicionar = tk.Frame(root)
frame_adicionar.pack(padx=10, pady=10)

tk.Label(frame_adicionar, text="Descrição").grid(row=0, column=0, padx=5, pady=5)
entry_descricao = tk.Entry(frame_adicionar)
entry_descricao.grid(row=0, column=1, padx=5, pady=5)

tk.Label(frame_adicionar, text="Valor").grid(row=1, column=0, padx=5, pady=5)
entry_valor = tk.Entry(frame_adicionar)
entry_valor.grid(row=1, column=1, padx=5, pady=5)

tk.Label(frame_adicionar, text="Tipo").grid(row=2, column=0, padx=5, pady=5)
combo_tipo = ttk.Combobox(frame_adicionar, values=["Receita", "Despesa"])
combo_tipo.grid(row=2, column=1, padx=5, pady=5)

tk.Label(frame_adicionar, text="Data (YYYY-MM-DD)").grid(row=3, column=0, padx=5, pady=5)
entry_data = tk.Entry(frame_adicionar)
entry_data.grid(row=3, column=1, padx=5, pady=5)

tk.Button(frame_adicionar, text="Adicionar Transação", command=adicionar_transacao).grid(row=4, column=0, columnspan=2, pady=10)

# Remover Transação
tk.Button(frame_adicionar, text="Remover Transação", command=remover_transacao).grid(row=5, column=0, columnspan=2, pady=10)

# Lista de Transações
frame_lista = tk.Frame(root)
frame_lista.pack(padx=10, pady=10)

colunas = ("id", "descricao", "valor", "tipo", "data")
lista_transacoes = ttk.Treeview(frame_lista, columns=colunas, show="headings")

for coluna in colunas:
    lista_transacoes.heading(coluna, text=coluna.capitalize())
    lista_transacoes.column(coluna, width=100)

lista_transacoes.pack()

atualizar_lista()

# Relatório Financeiro
frame_relatorio = tk.Frame(root)
frame_relatorio.pack(padx=10, pady=10)

tk.Button(frame_relatorio, text="Gerar Relatório", command=gerar_relatorio).pack()

# Orçamento
frame_orcamento = tk.Frame(root)
frame_orcamento.pack(padx=10, pady=10)

tk.Label(frame_orcamento, text="Definir Orçamento").grid(row=0, column=0, padx=5, pady=5)
entry_orcamento = tk.Entry(frame_orcamento)
entry_orcamento.grid(row=0, column=1, padx=5, pady=5)

tk.Button(frame_orcamento, text="Definir Orçamento", command=definir_orcamento).grid(row=1, column=0, columnspan=2, padx=10)

# Exibição do Orçamento
label_orcamento = tk.Label(frame_orcamento, text="Orçamento: R$0.00")
label_orcamento.grid(row=2, column=0, columnspan=2, pady=5)

label_despesas = tk.Label(frame_orcamento, text="Despesas: R$0.00")
label_despesas.grid(row=3, column=0, columnspan=2, pady=5)

label_saldo = tk.Label(frame_orcamento, text="Saldo: R$0.00")
label_saldo.grid(row=4, column=0, columnspan=2, padx=5)

atualizar_orcamento()

root.mainloop()