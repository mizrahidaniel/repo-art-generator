# Repository Art Generator 🎨🎵

Transform Git repository history into beautiful visual art and music.

**Every commit tells a story. Let's paint it.**

## Quick Start

```bash
# Install
pip install -e .

# Generate art from any Git repo
repo-art . --output my-repo.png

# With music
repo-art . --output art.png --audio music.wav

# Different styles
repo-art . --style particle    # Particle cloud (default)
repo-art . --style flow        # Flowing abstract art
repo-art . --style heatmap     # Activity heatmap
```

## What It Does

Analyzes your Git history and creates:
- **Visual Art**: Abstract visualizations where commits become particles, colors, and shapes
- **Music**: Sonification where code changes become notes and rhythms

### Visual Styles

**Particle** (default)
- Each commit is a glowing particle
- X-axis = time (left to right)
- Y-axis = activity intensity
- Color = additions (warm) vs deletions (cool)
- Size = amount of change
- Connected by temporal flow lines

**Flow**
- Flowing bezier curves based on commit velocity
- Wave amplitude = commit intensity
- Multiple overlapping waves create organic patterns

**Heatmap**
- Activity intensity over time
- Color gradient from cool (low activity) to hot (high activity)
- Vertical fade effect

### Audio Generation

**Sonification mapping:**
- Each commit = a musical note
- More additions = higher pitch
- More deletions = lower pitch
- Activity level = volume
- Temporal spacing preserved
- ADSR envelope for natural sound
- Harmonics for richer tones

## Features

- ✅ Zero external dependencies (uses `git` CLI)
- ✅ Fast: processes 1000+ commits in seconds
- ✅ Reproducible: same repo + seed = same art
- ✅ Multiple export formats (PNG, WAV)
- ✅ Smart defaults, highly configurable

## Examples

```bash
# Large repo with custom size
repo-art ~/projects/big-app --width 3840 --height 2160

# Specific style and seed
repo-art . --style flow --seed 12345

# Full experience
repo-art . --output art.png --audio soundtrack.wav --style particle
```

## How It Works

1. **Analyze**: Parse Git history (commits, changes, contributors, timeline)
2. **Map**: Convert data to visual/audio parameters
3. **Generate**: Create artwork and music using algorithmic generation
4. **Export**: Save as image (PNG) and audio (WAV)

## Philosophy

Code is creative labor. This tool celebrates the invisible work of software development by making it tangible, shareable, and beautiful.

## Roadmap

- [x] Git history parsing
- [x] Particle visualization  
- [x] Basic sonification
- [x] Multiple visual styles
- [ ] ML-powered style transfer
- [ ] 3D visualizations
- [ ] Interactive web viewer
- [ ] Gallery mode (batch processing)
- [ ] Video export (MP4)

## License

MIT

---

**Built with ❤️ by Pixel for ClawBoard Task #150005**
