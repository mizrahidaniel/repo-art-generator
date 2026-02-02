"""Generate visual art from repository data."""

import random
import math
from PIL import Image, ImageDraw
from typing import Dict, Any, Tuple, List


class ArtGenerator:
    """Generate abstract art from repository features."""
    
    def __init__(
        self,
        width: int = 1920,
        height: int = 1080,
        style: str = "particle",
        seed: int = None
    ):
        self.width = width
        self.height = height
        self.style = style
        self.seed = seed or 42
        random.seed(self.seed)
    
    def generate(self, features: Dict[str, Any]) -> Image.Image:
        """Generate artwork from repository features."""
        if self.style == "particle":
            return self._generate_particle_art(features)
        elif self.style == "flow":
            return self._generate_flow_art(features)
        elif self.style == "heatmap":
            return self._generate_heatmap_art(features)
        else:
            return self._generate_particle_art(features)
    
    def _generate_particle_art(self, features: Dict[str, Any]) -> Image.Image:
        """Generate particle-based visualization.
        
        Each commit is a particle, positioned by time and colored by activity.
        """
        img = Image.new("RGB", (self.width, self.height), color=(10, 10, 20))
        draw = ImageDraw.Draw(img)
        
        commits = features.get("commits", [])
        if not commits:
            return img
        
        # Normalize timestamps to canvas
        timestamps = [c["timestamp"] for c in commits]
        min_time, max_time = min(timestamps), max(timestamps)
        time_range = max_time - min_time or 1
        
        # Calculate total activity for normalization
        max_activity = max(c["additions"] + c["deletions"] for c in commits) or 1
        
        # Draw each commit as a particle
        for i, commit in enumerate(commits):
            # Position: time-based x, activity-based y
            t_norm = (commit["timestamp"] - min_time) / time_range
            x = int(t_norm * (self.width - 100)) + 50
            
            activity = commit["additions"] + commit["deletions"]
            activity_norm = activity / max_activity
            y = int((1 - activity_norm) * (self.height - 100)) + 50
            
            # Size based on changes
            size = max(2, min(20, int(activity_norm * 15)))
            
            # Color based on add/delete ratio
            if activity > 0:
                add_ratio = commit["additions"] / activity
                # Warm colors for additions, cool for deletions
                r = int(255 * add_ratio)
                b = int(255 * (1 - add_ratio))
                g = int(100 + 155 * activity_norm)
            else:
                r, g, b = 128, 128, 128
            
            # Add glow effect
            for glow in range(3, 0, -1):
                alpha = int(100 / glow)
                glow_color = (r, g, b)
                draw.ellipse(
                    [x - size * glow, y - size * glow,
                     x + size * glow, y + size * glow],
                    fill=self._blend_color(glow_color, (10, 10, 20), alpha / 255)
                )
            
            # Draw core particle
            draw.ellipse(
                [x - size, y - size, x + size, y + size],
                fill=(r, g, b)
            )
        
        # Connect nearby particles with faint lines (temporal flow)
        for i in range(len(commits) - 1):
            c1, c2 = commits[i], commits[i + 1]
            
            t1 = (c1["timestamp"] - min_time) / time_range
            x1 = int(t1 * (self.width - 100)) + 50
            a1 = (c1["additions"] + c1["deletions"]) / max_activity
            y1 = int((1 - a1) * (self.height - 100)) + 50
            
            t2 = (c2["timestamp"] - min_time) / time_range
            x2 = int(t2 * (self.width - 100)) + 50
            a2 = (c2["additions"] + c2["deletions"]) / max_activity
            y2 = int((1 - a2) * (self.height - 100)) + 50
            
            # Only connect if not too far apart
            if abs(x2 - x1) < 100:
                draw.line(
                    [x1, y1, x2, y2],
                    fill=(50, 50, 80),
                    width=1
                )
        
        return img
    
    def _generate_flow_art(self, features: Dict[str, Any]) -> Image.Image:
        """Generate flowing abstract art based on commit velocity."""
        img = Image.new("RGB", (self.width, self.height), color=(15, 15, 25))
        draw = ImageDraw.Draw(img)
        
        commits = features.get("commits", [])
        if not commits:
            return img
        
        # Create flowing curves based on commit density over time
        timeline = features.get("timeline", {})
        if not timeline:
            return img
        
        months = sorted(timeline.keys())
        max_commits = max(timeline.values())
        
        # Generate flowing bezier curves
        for i, month in enumerate(months):
            t = i / max(len(months) - 1, 1)
            x = int(t * (self.width - 100)) + 50
            
            commit_count = timeline[month]
            intensity = commit_count / max_commits
            
            # Generate wave pattern
            amplitude = intensity * (self.height // 3)
            y_base = self.height // 2
            
            # Draw flowing wave
            for wave in range(3):
                phase = wave * math.pi / 3
                points = []
                for offset in range(-20, 21, 2):
                    x_wave = x + offset
                    if 0 <= x_wave < self.width:
                        y_wave = int(y_base + amplitude * math.sin(t * 4 + phase) +
                                   intensity * 50 * math.sin((t * 8 + wave) * math.pi))
                        points.append((x_wave, y_wave))
                
                if len(points) > 1:
                    color = self._get_wave_color(intensity, wave)
                    for i in range(len(points) - 1):
                        draw.line([points[i], points[i+1]], fill=color, width=2)
        
        return img
    
    def _generate_heatmap_art(self, features: Dict[str, Any]) -> Image.Image:
        """Generate heatmap of activity over time."""
        img = Image.new("RGB", (self.width, self.height), color=(5, 5, 10))
        draw = ImageDraw.Draw(img)
        
        timeline = features.get("timeline", {})
        if not timeline:
            return img
        
        months = sorted(timeline.keys())
        max_commits = max(timeline.values())
        
        cell_width = self.width // (len(months) + 1)
        cell_height = self.height // 10
        
        for i, month in enumerate(months):
            commit_count = timeline[month]
            intensity = commit_count / max_commits
            
            x = i * cell_width
            color = self._intensity_to_color(intensity)
            
            for row in range(10):
                y = row * cell_height
                alpha = intensity * (1 - row * 0.08)  # Fade vertically
                blend_color = self._blend_color(color, (5, 5, 10), alpha)
                draw.rectangle(
                    [x, y, x + cell_width - 2, y + cell_height - 2],
                    fill=blend_color
                )
        
        return img
    
    @staticmethod
    def _blend_color(
        color1: Tuple[int, int, int],
        color2: Tuple[int, int, int],
        alpha: float
    ) -> Tuple[int, int, int]:
        """Blend two colors with alpha."""
        return tuple(
            int(c1 * alpha + c2 * (1 - alpha))
            for c1, c2 in zip(color1, color2)
        )
    
    @staticmethod
    def _intensity_to_color(intensity: float) -> Tuple[int, int, int]:
        """Convert intensity (0-1) to heat color."""
        if intensity < 0.3:
            return (0, int(intensity * 255 / 0.3), 128)
        elif intensity < 0.6:
            return (int((intensity - 0.3) * 255 / 0.3), 255, 128)
        else:
            return (255, 255, int(255 * (1 - (intensity - 0.6) / 0.4)))
    
    @staticmethod
    def _get_wave_color(intensity: float, wave_index: int) -> Tuple[int, int, int]:
        """Get color for wave based on intensity."""
        base_colors = [
            (100, 150, 255),  # Blue
            (150, 100, 255),  # Purple
            (255, 100, 150),  # Pink
        ]
        color = base_colors[wave_index % len(base_colors)]
        return tuple(int(c * (0.3 + intensity * 0.7)) for c in color)
