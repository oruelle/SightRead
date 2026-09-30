# Music Reading Trainer

Un programme d'entraînement à la lecture de notes de musique développé en Python avec Tkinter.

## Fonctionnalités

- **Portée musicale** : Affiche une portée standard avec 5 lignes
- **Déplacement des notes** : Les notes (cercles noirs) apparaissent à droite et se déplacent vers la gauche
- **Ligne verticale** : Les notes disparaissent lorsqu'elles passent cette ligne
- **Contrôle de la vitesse** : Ajustable en BPM (battements par minute) avec des boutons + et -
- **Niveau d'amplitude** : Restreint le nombre de notes différentes disponibles
- **Niveau d'écart** : Restreint l'écart maximum entre les notes successives

## Niveaux

### Amplitude (nombre de notes différentes)
- **Niveau 1** : 3 notes (Mi, Sol, La)
- **Niveau 2** : 5 notes (Do, Ré, Mi, Fa, Sol)
- **Niveau 3** : 7 notes (Do, Ré, Mi, Fa, Sol, La, Si)

### Écart maximum entre notes successives
- **Niveau 1** : Écart maximum de 1 (seconde)
- **Niveau 2** : Écart maximum de 2 (terce)
- **Niveau 3** : Écart maximum de 3 (quarte)

## Contrôles

### Interface graphique
- **BPM** : Entrer une valeur ou utiliser les boutons + et -
- **Amplitude** : Sélectionner le niveau avec les boutons + et -
- **Écart** : Sélectionner le niveau avec les boutons + et -
- **Pause/Effacer** : Boutons pour contrôler l'animation

### Raccourcis clavier
- **Espace** : Pause/Reprise
- **Suppr** : Effacer toutes les notes
- **Flèches gauche/droite** : Diminuer/Augmenter le BPM
- **Flèches haut/bas** : Diminuer/Augmenter le niveau d'amplitude

## Installation

```bash
# Assurez-vous d'avoir Python 3 installé
python3 --version

# Installez les dépendances (si nécessaire)
# Sous Debian/Ubuntu:
sudo apt-get install python3-tk

# Exécutez le programme
python3 music_trainer.py
