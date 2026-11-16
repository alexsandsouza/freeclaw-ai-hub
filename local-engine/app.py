"""FreeClaw Local Engine v0.4 - secure, review-first Tkinter desktop UI."""
import queue
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext, ttk

from engine import call_nvidia, load_specification, make_messages

TASK = ("Proponha o incremento POST /students em FastAPI e SQLite, validação e testes pytest, "
        "com rastreabilidade RF/AC/teste. Destaque pendências; não afirme testes executados.")

class FreeClawApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("FreeClaw Local Engine 0.4 - SPECTION")
        self.geometry("940x740")
        self.minsize(670,560)
        self.file = None
        self.response = ""
        self.events = queue.Queue()
        self.model = tk.StringVar(value="nvidia/nemotron-3.5-lightning-30b-a3b")
        self.key = tk.StringVar()
        self.status = tk.StringVar(value="Selecione um pacote Markdown. Chaves não são gravadas em disco.")
        self.build_ui()
        self.after(150,self.poll)
        self.protocol("WM_DELETE_WINDOW",self.close)

    def build_ui(self):
        page = ttk.Frame(self,padding=18)
        page.pack(fill="both",expand=True)
        ttk.Label(page,text="FreeClaw Local Engine 0.4",font=("Segoe UI",19,"bold")).pack(anchor="w")
        ttk.Label(page,text="SPECTION + NVIDIA · aplicação local · geração para revisão humana").pack(anchor="w",pady=(0,14))
        bar=ttk.Frame(page);bar.pack(fill="x")
        ttk.Button(bar,text="Escolher pacote .md",command=self.choose).pack(side="left")
        self.filename=ttk.Label(bar,text="Nenhum arquivo selecionado")
        self.filename.pack(side="left",padx=12)
        ttk.Label(page,text="ID do modelo NVIDIA (verifique no catálogo Build):").pack(anchor="w",pady=(10,0))
        ttk.Entry(page,textvariable=self.model).pack(fill="x")
        ttk.Label(page,text="Chave NVIDIA (oculta; apenas na memória):").pack(anchor="w",pady=(10,0))
        ttk.Entry(page,textvariable=self.key,show="*").pack(fill="x")
        ttk.Label(page,text="Objetivo da tarefa:").pack(anchor="w",pady=(10,0))
        self.task=scrolledtext.ScrolledText(page,height=4,font=("Consolas",10))
        self.task.insert("1.0",TASK);self.task.pack(fill="x")
        buttons=ttk.Frame(page);buttons.pack(fill="x",pady=12)
        ttk.Button(buttons,text="Pré-validar sem gastar tokens",command=self.preview).pack(side="left")
        self.send_button=ttk.Button(buttons,text="Enviar à NVIDIA (confirmar)",command=self.submit)
        self.send_button.pack(side="left",padx=9)
        ttk.Button(buttons,text="Salvar resposta .md",command=self.save).pack(side="left")
        ttk.Label(page,textvariable=self.status,wraplength=800).pack(anchor="w",pady=(0,9))
        self.output=scrolledtext.ScrolledText(page,font=("Consolas",10),wrap="word")
        self.output.pack(fill="both",expand=True)
        ttk.Label(page,text="Atenção: use apenas dados fictícios e sem segredos. A resposta não executa código e não altera o GitHub.").pack(anchor="w",pady=(8,0))

    def choose(self):
        selected=filedialog.askopenfilename(filetypes=[("Markdown e texto","*.md *.txt")])
        if selected:
            self.file=Path(selected)
            self.filename.configure(text=self.file.name)
            self.status.set("Revise o documento antes de enviar.")

    def messages(self):
        if self.file is None:
            raise ValueError("Selecione primeiro o pacote .md do AI Studio.")
        specs=load_specification(self.file)
        return make_messages(self.task.get("1.0","end-1c"),specs),len(specs)

    def preview(self):
        try:
            _,count=self.messages()
            self.status.set(f"Pré-validação OK: {count} caracteres. Nenhuma chamada à API.")
        except (OSError,ValueError,UnicodeError) as exc:
            messagebox.showerror("Validação",str(exc))

    def submit(self):
        try:
            messages,count=self.messages()
            key=self.key.get().strip()
            model=self.model.get().strip()
            if not key or not model:
                raise ValueError("Preencha chave e modelo.")
        except (OSError,ValueError,UnicodeError) as exc:
            messagebox.showerror("Validação",str(exc));return
        if not messagebox.askyesno("Confirmação",f"Enviar {count} caracteres à NVIDIA?\nRevise privacidade, credenciais e possíveis custos/cotas."):
            return
        self.send_button.configure(state="disabled")
        self.status.set("Solicitação enviada; aguardando resposta...")
        threading.Thread(target=self.worker,args=(key,model,messages),daemon=True).start()

    def worker(self,key,model,messages):
        try:
            self.events.put((True,call_nvidia(key,model,messages)))
        except Exception as exc:
            self.events.put((False,str(exc)))

    def poll(self):
        try:
            while True:
                ok,content=self.events.get_nowait()
                self.send_button.configure(state="normal")
                if ok:
                    self.response=content
                    self.output.delete("1.0","end")
                    self.output.insert("1.0",content)
                    self.status.set("Resposta recebida; revise e salve. Nenhum código foi executado.")
                else:
                    self.status.set(content)
                    messagebox.showerror("NVIDIA",content)
        except queue.Empty:
            pass
        self.after(150,self.poll)

    def save(self):
        if not self.response:
            messagebox.showinfo("Sem resposta","Gere uma resposta antes de salvar.");return
        filename=filedialog.asksaveasfilename(defaultextension=".md",filetypes=[("Markdown","*.md")],initialfile="proposta-spection.md")
        if filename:
            Path(filename).write_text(self.response,encoding="utf-8")
            self.status.set("Rascunho salvo localmente, aguardando revisão.")

    def close(self):
        self.key.set("")
        self.destroy()

if __name__=="__main__":
    FreeClawApp().mainloop()
