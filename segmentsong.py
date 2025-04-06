import json
import numpy as np

import json

class SongWorkoutMapper:
    def __init__(self, json_file_path):
        """
        Initialize the SongWorkoutMapper with the path to the song analysis JSON file.
        
        Args:
            json_file_path: Path to the song analysis JSON file
        """
        self.json_file_path = json_file_path
        self.workouts_fp = "workouts/workouts.json" ###check filepaths functioning
        with open(json_file_path, 'r') as f:
            self.song_data = json.load(f)
        with open(self.workouts_fp, 'r') as f:
            self.workouts = json.load(f)
        
        # Extract useful song properties
        self.duration = self.song_data['track']['duration']
        self.tempo = self.song_data['track']['tempo']
        self.beats = self.song_data['beats']
        self.sections = self.song_data['sections']
        
    def create_dance_sections(self,max_section = 45):
        with open(json_file_path, 'r') as f:
            data = json.load(f)
        
        time=[]
        for section in data['sections']:
            if float(section['duration'])<=max_section:
                time.append(section['start'])
            else:
                n = int(np.floor(float(section['duration']))/max_section)+1
                piece = float(section['duration'])/n
                initial = float(section['start'])
                for i in list(range(n)):
                    time.append(initial+i*piece)
        time.append(data['track']['duration'])
        return time

    def create_workout(self, intensity=30, stamina = 45):
        """
        Creates a song cut by selecting and repeating sections to match the desired length
        while maintaining musical coherence.
        
        Args:
            sections: List of time intervals from create_dance_sections()
            
        Returns:
            List of tuples representing the final song cut with repeated sections
        """
        sections = self.create_dance_sections(self,stamina)
        
        routine = []
        for i in list(range(len(sections)-1)):
            if i == 0:
                cond_2 = sections[i+1]-sections[i]>intensity
                filtered = list(filter(lambda k: not cond_2 in self.workouts[k], self.workouts))
                choice = np.random.choice(filtered)
                routine.append(choice)
            else:
                cond_1 = self.workouts[routine[i-1]][0]
                cond_2 = sections[i+1]-sections[i]>intensity
                filtered = list(filter(lambda k: not cond_1 in self.workouts[k] and not cond_2 in self.workouts[k], self.workouts))
                choice = np.random.choice(filtered)
                routine.append(choice)
        return routine