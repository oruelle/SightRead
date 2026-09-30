#!/usr/bin/env python3
"""
Music Reading Trainer
Un programme pour s'entraîner à la lecture de notes de musique.
Les notes se déplacent de droite à gauche sur une portée à une vitesse ajustable.
"""

import tkinter as tk
from tkinter import ttk
import random
import math

class MusicTrainer:
    """Application principale pour l'entraînement à la lecture de notes."""

    # Constantes pour la portée
    NUM_LINES = 5
    LINE_SPACING = 15  # Espacement entre les lignes de la portée
    STAFF_Y_OFFSET = 100  # Position Y du haut de la portée
    STAFF_HEIGHT = (NUM_LINES - 1) * LINE_SPACING

    # Constantes pour les notes
    NOTE_RADIUS = 8
    NOTE_SPEED_BASE = 2.0  # Vitesse de base (pixels par frame)

    # Noms des notes (de bas en haut)
    NOTE_NAMES = ['Mi0', 'Do', 'Ré', 'Mi', 'Fa', 'Sol', 'La', 'Si', 'Do2', 'Ré2', 'Mi2']
    # Positions des notes sur la portée (0 = ligne du bas, 4 = ligne du haut)
    # Les notes entre les lignes ont des positions demi-entières
    NOTE_POSITIONS = {
        'Mi0': -1,   # Mi grave - sous la portée
        'Do': 0,     # Sous la portée
        'Ré': 0.5,
        'Mi': 1,
        'Fa': 1.5,
        'Sol': 2,
        'La': 2.5,
        'Si': 3,
        'Do2': 3.5,  # Au-dessus de la portée
        'Ré2': 4.0,  # Ré sur-aigu
        'Mi2': 4.5,  # Mi sur-aigu - bien au-dessus de la portée
    }

    # Niveaux d'amplitude (nombre de notes différentes)
    AMPLITUDE_LEVELS = {
        1: ['Mi', 'Sol', 'La'],           # Niveau 1: 3 notes
        2: ['Do', 'Ré', 'Mi', 'Fa', 'Sol'],  # Niveau 2: 5 notes
        3: ['Do', 'Ré', 'Mi', 'Fa', 'Sol', 'La', 'Si', 'Do2'],  # Niveau 3: 8 notes
        4: ['Mi0', 'Do', 'Ré', 'Mi', 'Fa', 'Sol', 'La', 'Si', 'Do2', 'Ré2', 'Mi2'],  # Niveau 4: 11 notes
    }

    # Niveaux d'écart maximum entre notes successives
    INTERVAL_LEVELS = {
        1: 1,   # Niveau 1: écart max de 1 (seconde)
        2: 2,   # Niveau 2: écart max de 2 (terce)
        3: 3,   # Niveau 3: écart max de 3 (quarte)
    }

    def __init__(self, root):
        """Initialise l'application."""
        self.root = root
        self.root.title("Music Reading Trainer")
        self.root.geometry("800x600")

        # Variables de contrôle
        self.bpm = tk.IntVar(value=60)
        self.amplitude_level = tk.IntVar(value=2)
        self.interval_level = tk.IntVar(value=2)
        self.is_playing = tk.BooleanVar(value=True)

        # Liste des notes actives
        self.notes = []

        # Position de la ligne verticale (où les notes disparaissent)
        self.vertical_line_x = 200

        # Temps entre les frames (en ms)
        self.frame_delay = 16  # ~60 FPS

        # Crée l'interface
        self.create_widgets()
        self.create_staff()

        # Démarre l'animation
        self.last_note_time = 0
        self.last_note_spawn = 0
        self.animation_id = None
        self.start_animation()

        # Gère la fermeture de la fenêtre
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def create_widgets(self):
        """Crée tous les widgets de l'interface."""
        # Frame pour les contrôles
        control_frame = ttk.Frame(self.root)
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        # Contrôle BPM
        bpm_frame = ttk.LabelFrame(control_frame, text="Vitesse (BPM)")
        bpm_frame.pack(side=tk.LEFT, padx=5, pady=5)

        bpm_label = ttk.Label(bpm_frame, text="BPM:")
        bpm_label.grid(row=0, column=0, padx=5, pady=2)

        bpm_entry = ttk.Entry(bpm_frame, textvariable=self.bpm, width=5)
        bpm_entry.grid(row=0, column=1, padx=5, pady=2)

        bpm_minus = ttk.Button(bpm_frame, text="-", command=self.decrease_bpm)
        bpm_minus.grid(row=0, column=2, padx=2, pady=2)

        bpm_plus = ttk.Button(bpm_frame, text="+", command=self.increase_bpm)
        bpm_plus.grid(row=0, column=3, padx=2, pady=2)

        # Contrôle d'amplitude
        amplitude_frame = ttk.LabelFrame(control_frame, text="Amplitude")
        amplitude_frame.pack(side=tk.LEFT, padx=5, pady=5)

        amplitude_label = ttk.Label(amplitude_frame, text="Niveau:")
        amplitude_label.grid(row=0, column=0, padx=5, pady=2)

        amplitude_entry = ttk.Entry(amplitude_frame, textvariable=self.amplitude_level, width=3)
        amplitude_entry.grid(row=0, column=1, padx=5, pady=2)

        amplitude_minus = ttk.Button(amplitude_frame, text="-", command=self.decrease_amplitude)
        amplitude_minus.grid(row=0, column=2, padx=2, pady=2)

        amplitude_plus = ttk.Button(amplitude_frame, text="+", command=self.increase_amplitude)
        amplitude_plus.grid(row=0, column=3, padx=2, pady=2)

        # Contrôle d'écart
        interval_frame = ttk.LabelFrame(control_frame, text="Écart max")
        interval_frame.pack(side=tk.LEFT, padx=5, pady=5)

        interval_label = ttk.Label(interval_frame, text="Niveau:")
        interval_label.grid(row=0, column=0, padx=5, pady=2)

        interval_entry = ttk.Entry(interval_frame, textvariable=self.interval_level, width=3)
        interval_entry.grid(row=0, column=1, padx=5, pady=2)

        interval_minus = ttk.Button(interval_frame, text="-", command=self.decrease_interval)
        interval_minus.grid(row=0, column=2, padx=2, pady=2)

        interval_plus = ttk.Button(interval_frame, text="+", command=self.increase_interval)
        interval_plus.grid(row=0, column=3, padx=2, pady=2)

        # Boutons de contrôle
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(side=tk.LEFT, padx=5, pady=5)

        play_button = ttk.Button(button_frame, text="Pause", command=self.toggle_play)
        play_button.pack(side=tk.LEFT, padx=2)

        clear_button = ttk.Button(button_frame, text="Effacer", command=self.clear_notes)
        clear_button.pack(side=tk.LEFT, padx=2)

        # Canvas pour la portée et les notes
        self.canvas = tk.Canvas(self.root, bg='white')
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Bind les événements clavier
        self.root.bind('<space>', lambda e: self.toggle_play())
        self.root.bind('<Delete>', lambda e: self.clear_notes())
        self.root.bind('<Left>', lambda e: self.decrease_bpm())
        self.root.bind('<Right>', lambda e: self.increase_bpm())
        self.root.bind('<Up>', lambda e: self.increase_amplitude())
        self.root.bind('<Down>', lambda e: self.decrease_amplitude())

    def create_staff(self):
        """Dessine la portée sur le canvas."""
        width = self.canvas.winfo_width() if self.canvas.winfo_width() > 0 else 800
        height = self.canvas.winfo_height() if self.canvas.winfo_height() > 0 else 400

        # Efface tout
        self.canvas.delete("all")

        # Dessine les lignes de la portée
        for i in range(self.NUM_LINES):
            y = self.STAFF_Y_OFFSET + i * self.LINE_SPACING
            self.canvas.create_line(0, y, width, y, fill='black', width=1, tags='staff')

        # Dessine la ligne verticale (où les notes disparaissent)
        self.canvas.create_line(
            self.vertical_line_x, 0,
            self.vertical_line_x, height,
            fill='red', width=2, dash=(5, 5), tags='vertical_line'
        )

        # Redessine les notes existantes
        for note in self.notes:
            self.draw_note(note)

    def draw_note(self, note):
        """Dessine une note sur le canvas."""
        x, y, note_name = note

        # Calcule la position Y en fonction de la note
        note_pos = self.NOTE_POSITIONS.get(note_name, 2)
        actual_y = self.STAFF_Y_OFFSET + note_pos * self.LINE_SPACING

        # Dessine le cercle de la note
        note_id = self.canvas.create_oval(
            x - self.NOTE_RADIUS, actual_y - self.NOTE_RADIUS,
            x + self.NOTE_RADIUS, actual_y + self.NOTE_RADIUS,
            fill='black', outline='black', tags=f'note {note_name}'
        )

        return note_id

    def get_note_y_position(self, note_name):
        """Retourne la position Y d'une note sur la portée."""
        note_pos = self.NOTE_POSITIONS.get(note_name, 2)
        return self.STAFF_Y_OFFSET + note_pos * self.LINE_SPACING

    def spawn_note(self):
        """Fait apparaître une nouvelle note à droite de la dernière note."""
        if not self.is_playing.get():
            return

        # Sélectionne les notes disponibles en fonction du niveau d'amplitude
        available_notes = self.AMPLITUDE_LEVELS.get(self.amplitude_level.get(), ['Mi', 'Sol', 'La'])

        # Si c'est la première note ou si on ne respecte pas l'écart
        if not self.notes:
            note_name = random.choice(available_notes)
        else:
            # Récupère la dernière note
            last_note = self.notes[-1]
            last_note_name = last_note[2]
            last_note_pos = self.NOTE_POSITIONS.get(last_note_name, 2)

            max_interval = self.INTERVAL_LEVELS.get(self.interval_level.get(), 2)

            # Filtre les notes qui respectent l'écart maximum
            valid_notes = []
            for note in available_notes:
                note_pos = self.NOTE_POSITIONS.get(note, 2)
                interval = abs(note_pos - last_note_pos)
                if interval <= max_interval:
                    valid_notes.append(note)

            # Si aucune note valide, on prend toutes les notes
            if not valid_notes:
                valid_notes = available_notes

            note_name = random.choice(valid_notes)

        # Position initiale à NOTE_SPACING pixels à droite de la dernière note
        NOTE_SPACING = 100
        if self.notes:
            last_x = self.notes[-1][0]
            x = last_x + NOTE_SPACING
        else:
            x = 800 + self.NOTE_RADIUS * 2
        y = self.get_note_y_position(note_name)

        # Ajoute la note à la liste
        self.notes.append([x, y, note_name])

        # Dessine la note
        self.draw_note([x, y, note_name])

    def move_notes(self):
        """Déplace toutes les notes vers la gauche."""
        speed = self.calculate_speed()
        notes_to_remove = []

        for i, note in enumerate(self.notes):
            x, y, note_name = note
            new_x = x - speed

            # Si la note passe la ligne verticale, on la marque pour suppression
            if new_x < self.vertical_line_x - self.NOTE_RADIUS:
                notes_to_remove.append(i)
            else:
                # Met à jour la position
                self.notes[i] = [new_x, y, note_name]

        # Supprime les notes qui ont passé la ligne
        for i in sorted(notes_to_remove, reverse=True):
            self.notes.pop(i)

        # Redessine toutes les notes
        self.redraw_notes()

    def redraw_notes(self):
        """Redessine toutes les notes sur le canvas."""
        # Efface toutes les notes
        self.canvas.delete("note")

        # Dessine la portée et la ligne verticale
        width = self.canvas.winfo_width() if self.canvas.winfo_width() > 0 else 800
        height = self.canvas.winfo_height() if self.canvas.winfo_height() > 0 else 400

        for i in range(self.NUM_LINES):
            y = self.STAFF_Y_OFFSET + i * self.LINE_SPACING
            self.canvas.create_line(0, y, width, y, fill='black', width=1, tags='staff')

        self.canvas.create_line(
            self.vertical_line_x, 0,
            self.vertical_line_x, height,
            fill='red', width=2, dash=(5, 5), tags='vertical_line'
        )

        # Redessine les notes
        for note in self.notes:
            self.draw_note(note)

    def calculate_speed(self):
        """Calcule la vitesse de déplacement en fonction du BPM avec distance fixe entre notes."""
        # Distance fixe entre les notes (en pixels)
        NOTE_SPACING = 100

        # Temps entre l'apparition de deux notes (basé sur le BPM)
        # À 60 BPM, une note par seconde
        seconds_per_beat = 60.0 / self.bpm.get()

        # Vitesse en pixels par frame (16ms)
        speed_per_second = NOTE_SPACING / seconds_per_beat
        speed_per_frame = speed_per_second * (self.frame_delay / 1000.0)

        return speed_per_frame

    def update(self):
        """Met à jour l'animation (appelée à chaque frame)."""
        # Spawn une nouvelle note directement
        self.spawn_note()

        # Déplace les notes
        self.move_notes()

        # Planifie la prochaine frame
        self.animation_id = self.root.after(self.frame_delay, self.update)

    def start_animation(self):
        """Démarre l'animation."""
        if self.animation_id is None:
            self.last_note_spawn = 0
            self.update()

    def stop_animation(self):
        """Arrête l'animation."""
        if self.animation_id is not None:
            self.root.after_cancel(self.animation_id)
            self.animation_id = None

    def toggle_play(self):
        """Bascule entre lecture et pause."""
        if self.is_playing.get():
            self.is_playing.set(False)
            self.stop_animation()
        else:
            self.is_playing.set(True)
            self.start_animation()

    def clear_notes(self):
        """Efface toutes les notes."""
        self.notes = []
        self.redraw_notes()

    def increase_bpm(self):
        """Augmente le BPM."""
        self.bpm.set(min(self.bpm.get() + 10, 300))

    def decrease_bpm(self):
        """Diminue le BPM."""
        self.bpm.set(max(self.bpm.get() - 10, 20))

    def increase_amplitude(self):
        """Augmente le niveau d'amplitude."""
        self.amplitude_level.set(min(self.amplitude_level.get() + 1, 4))

    def decrease_amplitude(self):
        """Diminue le niveau d'amplitude."""
        self.amplitude_level.set(max(self.amplitude_level.get() - 1, 1))

    def increase_interval(self):
        """Augmente le niveau d'écart."""
        self.interval_level.set(min(self.interval_level.get() + 1, 3))

    def decrease_interval(self):
        """Diminue le niveau d'écart."""
        self.interval_level.set(max(self.interval_level.get() - 1, 1))

    def on_close(self):
        """Gère la fermeture de la fenêtre."""
        self.stop_animation()
        self.root.destroy()

    def on_resize(self, event):
        """Gère le redimensionnement de la fenêtre."""
        self.create_staff()

def main():
    """Point d'entrée du programme."""
    root = tk.Tk()
    app = MusicTrainer(root)

    # Bind l'événement de redimensionnement
    root.bind('<Configure>', app.on_resize)

    root.mainloop()

if __name__ == "__main__":
    main()
