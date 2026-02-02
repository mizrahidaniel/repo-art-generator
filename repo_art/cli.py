#!/usr/bin/env python3
"""CLI for Repository Art Generator."""

import argparse
import sys
from pathlib import Path

from .analyzer import RepositoryAnalyzer
from .visualizer import ArtGenerator
from .sonifier import MusicGenerator


def main():
    parser = argparse.ArgumentParser(
        description="Generate visual and audio art from Git repositories"
    )
    parser.add_argument(
        "repo_path",
        type=str,
        nargs="?",
        default=".",
        help="Path to Git repository (default: current directory)"
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default="repo-art.png",
        help="Output image file path (default: repo-art.png)"
    )
    parser.add_argument(
        "--audio",
        "-a",
        type=str,
        default=None,
        help="Output audio file path (e.g., repo-art.wav)"
    )
    parser.add_argument(
        "--style",
        "-s",
        choices=["particle", "flow", "heatmap"],
        default="particle",
        help="Visual style (default: particle)"
    )
    parser.add_argument(
        "--width",
        "-w",
        type=int,
        default=1920,
        help="Image width in pixels (default: 1920)"
    )
    parser.add_argument(
        "--height",
        "-H",
        type=int,
        default=1080,
        help="Image height in pixels (default: 1080)"
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility (default: 42)"
    )
    
    args = parser.parse_args()
    
    # Validate repository
    repo_path = Path(args.repo_path).resolve()
    if not (repo_path / ".git").exists():
        print(f"Error: Not a git repository: {repo_path}", file=sys.stderr)
        sys.exit(1)
    
    print(f"🎨 Analyzing repository: {repo_path}")
    
    # Extract features
    analyzer = RepositoryAnalyzer(str(repo_path))
    features = analyzer.extract_features()
    
    commit_count = len(features["commits"])
    contributor_count = len(features["contributors"])
    print(f"   Found {commit_count} commits from {contributor_count} contributors")
    
    if commit_count == 0:
        print("Error: No commits found in repository", file=sys.stderr)
        sys.exit(1)
    
    # Generate visual art
    print(f"🖼️  Generating {args.style} visualization...")
    art_gen = ArtGenerator(
        width=args.width,
        height=args.height,
        style=args.style,
        seed=args.seed
    )
    image = art_gen.generate(features)
    
    # Save image
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(output_path)
    print(f"   ✓ Saved artwork: {output_path}")
    
    # Generate audio if requested
    if args.audio:
        print(f"🎵 Generating sonification...")
        music_gen = MusicGenerator()
        music_gen.generate(features, args.audio)
        print(f"   ✓ Saved audio: {args.audio}")
    
    print("✨ Done!")


if __name__ == "__main__":
    main()
