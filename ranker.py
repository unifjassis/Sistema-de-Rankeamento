import tkinter as tk
from tkinter import messagebox
import random
import itertools
import math
import csv
import os
from datetime import datetime 

# Requisito R1: Seleção de jogos (entre 2 e 10 antes de iniciar o rankeamento)
class GameSelector:
    def __init__(self, root, container, games, callback):
        self.root = root
        self.container = container
        self.games = games
        self.callback = callback
        self.check_vars = {}

    def show(self):
        # Limpa widgets anteriores
        for w in self.container.winfo_children():
            w.destroy()

        tk.Label(self.container, text="Selecione de 2 a 10 jogos:", font=("Helvetica", 14, "bold")).pack(pady=10)

        # Cria área rolável
        scroll_canvas = tk.Canvas(self.container)
        scrollbar = tk.Scrollbar(self.container, orient=tk.VERTICAL, command=scroll_canvas.yview)
        scroll_canvas.configure(yscrollcommand=scrollbar.set)
        scroll_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        list_frame = tk.Frame(scroll_canvas)
        scroll_canvas.create_window((0, 0), window=list_frame, anchor='nw')

        def on_frame_config(event):
            scroll_canvas.configure(scrollregion=scroll_canvas.bbox("all"))
        list_frame.bind("<Configure>", on_frame_config)

        # Divide em duas colunas: primeiros 25 à esquerda, demais à direita
        left_games = self.games[:25]
        right_games = self.games[25:]

        left_frame = tk.Frame(list_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,10))
        right_frame = tk.Frame(list_frame)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10,0))

        # Cria checkboxes
        for game in left_games:
            var = tk.IntVar(value=0)
            cb = tk.Checkbutton(left_frame, text=game, variable=var, command=self.validate_selection)
            cb.pack(anchor=tk.W)
            self.check_vars[game] = var

        for game in right_games:
            var = tk.IntVar(value=0)
            cb = tk.Checkbutton(right_frame, text=game, variable=var, command=self.validate_selection)
            cb.pack(anchor=tk.W)
            self.check_vars[game] = var

        self.start_btn = tk.Button(self.container, text="Iniciar Rankeamento", state=tk.DISABLED, command=self.start)
        self.start_btn.pack(pady=20)

    def validate_selection(self):
        count = sum(v.get() for v in self.check_vars.values())
        if 2 <= count <= 10:
            self.start_btn.configure(state=tk.NORMAL)
        else:
            self.start_btn.configure(state=tk.DISABLED)

    def start(self):
        selected = [g for g, v in self.check_vars.items() if v.get()]
        self.callback(selected)

class RoundedButton(tk.Canvas):
    def __init__(self, parent, text, command, radius=25, **kwargs):
        super().__init__(parent, **kwargs, highlightthickness=0)
        self.command = command
        self.radius = radius
        self.fill_colors = {
            'normal': '#404040',
            'hover': '#505050',
            'active': '#303030'
        }
        
        self.bind("<Button-1>", self.on_click)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        
        self.width = 200
        self.height = 100
        
        self.rect = self.create_rounded_rect(0, 0, self.width, self.height, radius=radius, fill=self.fill_colors['normal'])
        self.text = self.create_text(self.width/2, self.height/2, text=text, fill='white', font=('Helvetica', 12))
        
        self.configure(width=self.width, height=self.height)

    def create_rounded_rect(self, x1, y1, x2, y2, radius=25, **kwargs):
        points = []
        points += [x1 + radius, y1,
                   x2 - radius, y1]
        points += [x2 - radius, y1,
                   x2, y1,
                   x2, y1 + radius]
        points += [x2, y1 + radius,
                   x2, y2 - radius]
        points += [x2, y2 - radius,
                   x2, y2,
                   x2 - radius, y2]
        points += [x2 - radius, y2,
                   x1 + radius, y2]
        points += [x1 + radius, y2,
                   x1, y2,
                   x1, y2 - radius]
        points += [x1, y2 - radius,
                   x1, y1 + radius]
        points += [x1, y1 + radius,
                   x1, y1,
                   x1 + radius, y1]
        
        return self.create_polygon(points, **kwargs, smooth=True)

    def on_click(self, event):
        self.itemconfig(self.rect, fill=self.fill_colors['active'])
        self.after(100, self.command)

    def on_enter(self, event):
        self.itemconfig(self.rect, fill=self.fill_colors['hover'])

    def on_leave(self, event):
        self.itemconfig(self.rect, fill=self.fill_colors['normal'])

class CircularButton(tk.Canvas):
    def __init__(self, parent, text, command, **kwargs):
        super().__init__(parent, **kwargs, highlightthickness=0)
        self.command = command
        self.fill_colors = {
            'normal': '#404040',
            'hover': '#505050',
            'active': '#303030'
        }
        
        self.diameter = 100
        self.radius = self.diameter // 2
        
        self.bind("<Button-1>", self.on_click)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        
        self.circle = self.create_oval(0, 0, self.diameter, self.diameter, fill=self.fill_colors['normal'], outline='')
        self.text = self.create_text(self.radius, self.radius, text=text, fill='white', font=('Helvetica', 12))
        
        self.configure(width=self.diameter, height=self.diameter)

    def on_click(self, event):
        self.itemconfig(self.circle, fill=self.fill_colors['active'])
        self.after(100, self.command)

    def on_enter(self, event):
        self.itemconfig(self.circle, fill=self.fill_colors['hover'])

    def on_leave(self, event):
        self.itemconfig(self.circle, fill=self.fill_colors['normal'])

class Ranker:
    def __init__(self, root, frame, items):
        self.root = root
        self.frame = frame
        self.items = items
        self.scores = {item: 0 for item in items}
        self.pairs = list(itertools.combinations(items, 2))
        random.shuffle(self.pairs)
        self.remaining_pairs = self.pairs.copy()
        self.history = []
        self.current_pair = None

    def start_ranking(self):
        self.next_pair()

    def next_pair(self):
        if self.remaining_pairs:
            self.current_pair = self.remaining_pairs.pop(0)
            self.show_pair(*self.current_pair)
        else:
            self.show_results()

    def show_pair(self, item1, item2):
        for widget in self.frame.winfo_children():
            widget.destroy()

        main_container = tk.Frame(self.frame)
        main_container.pack(expand=True, fill=tk.BOTH, pady=20)

        title_frame = tk.Frame(main_container)
        title_frame.pack(pady=10)
        tk.Label(title_frame, text="Qual você prefere?", font=("Helvetica", 14, "bold")).pack()

        buttons_frame = tk.Frame(main_container)
        buttons_frame.pack(expand=True, fill=tk.BOTH, pady=20)

        RoundedButton(
            buttons_frame,
            text=item1,
            command=lambda: self.handle_choice(-1)
        ).pack(side=tk.LEFT, expand=True, padx=10)

        CircularButton(
            buttons_frame,
            text="Empate",
            command=lambda: self.handle_choice(0)
        ).pack(side=tk.LEFT, padx=10)

        RoundedButton(
            buttons_frame,
            text=item2,
            command=lambda: self.handle_choice(1)
        ).pack(side=tk.LEFT, expand=True, padx=10)

        bottom_frame = tk.Frame(main_container)
        bottom_frame.pack(pady=20)

        self.back_button = tk.Button(
            bottom_frame,
            text="Voltar",
            width=12,
            font=("Helvetica", 10),
            relief=tk.FLAT,
            bg='#404040',
            fg='white',
            activebackground='#303030',
            command=self.handle_back,
            state=tk.NORMAL if self.history else tk.DISABLED
        )
        self.back_button.pack()

    def handle_choice(self, choice):
        item1, item2 = self.current_pair
        
        if choice == -1:
            self.scores[item1] += 1
        elif choice == 1:
            self.scores[item2] += 1

        self.history.append((item1, item2, choice))
        self.next_pair()

    def handle_back(self):
        if self.history:
            item1, item2, choice = self.history.pop()
            
            if choice == -1:
                self.scores[item1] -= 1
            elif choice == 1:
                self.scores[item2] -= 1
            
            self.remaining_pairs.insert(0, (item1, item2))
            self.next_pair()

    def save_results(self):
        try:
            ranked_items = sorted(self.scores.items(), key=lambda x: x[1], reverse=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            script_dir = os.path.dirname(os.path.abspath(__file__))
            save_dir = os.path.join(script_dir, "results")
            os.makedirs(save_dir, exist_ok=True)
            
            filename = f"ranking_{timestamp}.csv"
            full_path = os.path.join(save_dir, filename)
            
            with open(full_path, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(["Posição", "Jogo", "Pontuação"])
                for index, (item, score) in enumerate(ranked_items, start=1):
                    writer.writerow([index, item, score])
            
            messagebox.showinfo(
                "Resultados Salvos",
                f"Arquivo salvo com sucesso!\nLocal: {full_path}"
            )
        except Exception as e:
            messagebox.showerror(
                "Erro ao Salvar",
                f"Não foi possível salvar o arquivo:\n{str(e)}"
            )

    def show_results(self):
        for widget in self.frame.winfo_children():
            widget.destroy()

        result_frame = tk.Frame(self.frame)
        result_frame.pack(expand=True, fill=tk.BOTH)

        tk.Label(
            result_frame,
            text="Ranking Final",
            font=("Helvetica", 16, "bold")
        ).pack(pady=20)

        ranked_items = sorted(self.scores.items(), key=lambda x: x[1], reverse=True)
        
        results_container = tk.Frame(result_frame)
        results_container.pack(expand=True, fill=tk.BOTH)

        for index, (item, score) in enumerate(ranked_items, start=1):
            item_frame = tk.Frame(results_container)
            item_frame.pack(fill=tk.X, padx=50, pady=5)
            
            tk.Label(
                item_frame,
                text=f"{index}º",
                font=("Helvetica", 14),
                width=4,
                anchor=tk.W
            ).pack(side=tk.LEFT)
            
            tk.Label(
                item_frame,
                text=item,
                font=("Helvetica", 14)
            ).pack(side=tk.LEFT, padx=20)
            
            tk.Label(
                item_frame,
                text=f"★ {score}",
                font=("Helvetica", 12),
                fg="#666666"
            ).pack(side=tk.RIGHT)
        
        # Botão para salvar
        save_btn = tk.Button(
            result_frame,
            text="Salvar Resultado",
            width=16,
            font=("Helvetica", 12),
            relief=tk.FLAT,
            bg='#404040',
            fg='white',
            activebackground='#303030',
            command=self.save_results
        )
        save_btn.pack(pady=(20, 10))

        # Botão para voltar ao início
        restart_btn = tk.Button(
            result_frame,
            text="Voltar ao Início",
            width=16,
            font=("Helvetica", 12),
            relief=tk.FLAT,
            bg='#404040',
            fg='white',
            activebackground='#303030',
            command=lambda: selector.show()
        )
        restart_btn.pack(pady=(0, 20))

# Fluxo principal com Seleção de Jogos (Requisito R1)
if __name__ == '__main__':
    listed = [
        "Super Mario World",
        "Doom",
        "Super Metroid",
        "Final Fantasy VI",
        "Chrono Trigger",
        "Donkey Kong Country 2:\nDiddy's Kong Quest",
        "Super Mario 64",
        "Final Fantasy VII",
        "Castlevania:\nSymphony of the Night",
        "Resident Evil 2",
        "Metal Gear Solid",
        "The Legend of Zelda:\nOcarina of Time",
        "Final Fantasy IX",
        "Metroid Prime",
        "Grand Theft Auto:\nSan Andreas",
        "Halo 2",
        "Metal Gear Solid 3:\nSnake Eater",
        "Resident Evil 4",
        "Shadow of the Colossus",
        "Kingdom Hearts II",
        "God of War II",
        "Bioshock",
        "Halo 3",
        "Portal",
        "Super Mario Galaxy",
        "Uncharted 2:\nAmong Thieves",
        "Assassins Creed II",
        "God of War III",
        "Red Dead Redemption",
        "Dark Souls",
        "Portal 2",
        "Minecraft",
        "The Elder Scrolls V:\nSkyrim",
        "The Last of Us",
        "Grand Theft Auto V",
        "Bloodborne",
        "The Witcher 3:\nWild Hunt",
        "Undertale",
        "Dark Souls III",
        "Uncharted 4:\nA Thief's End",
        "The Legend of Zelda:\nBreath of the Wild",
        "Super Mario Odyssey",
        "Hollow Knight",
        "Persona 5",
        "God of War",
        "Red Dead Redemption 2",
        "Celeste",
        "Hades",
        "It Takes Two",
        "Elden Ring"
    ]

    root = tk.Tk()
    root.title("Game Ranker")
    root.geometry("800x600")
    root.minsize(700, 500)

    main_frame = tk.Frame(root)
    main_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)

    def init_ranker(selected_games):
        ranker = Ranker(root, main_frame, selected_games)
        ranker.start_ranking()

    selector = GameSelector(root, main_frame, listed, init_ranker)
    selector.show()

    root.mainloop()