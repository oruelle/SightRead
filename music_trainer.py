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
    NOTE_NAMES = ['Do', 'Ré', 'Mi', 'Fa', 'Sol', 'La', 'Si']
    # Positions des notes sur la portée
    NOTE_POSITIONS = {
        'Do': 0,   # Sous la portée
        'Ré': 0.5,
        'Mi': 1,
        'Fa': 1.5,
        'Sol': 2,
        'La': 2.5,
        'Si': 3,
        'Do2': 3.5,  # Au-dessus de la portée
    }

    # Niveaux d'amplitude (nombre de notes différentes)
    AMPLITUDE_LEVELS = {
        1: ['Mi', 'Sol', 'La'],           # Niveau 1: 3 notes
        2: ['Do', 'Ré', 'Mi', 'Fa', 'Sol'],  # Niveau 2: 5 notes
        3: ['Do', 'Ré', 'Mi', 'Fa', 'Sol', 'La', 'Si'],  # Niveau 3: 7 notes
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

        # Position de la ligne verticale
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

    # [Le reste du code continue avec les méthodes de la classe...]
