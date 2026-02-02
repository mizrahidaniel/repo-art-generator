"""Extract features from Git repository history."""

import subprocess
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict


class RepositoryAnalyzer:
    """Analyze Git repository and extract artistic features."""
    
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path).resolve()
        if not (self.repo_path / ".git").exists():
            raise ValueError(f"Not a git repository: {repo_path}")
    
    def extract_features(self) -> Dict[str, Any]:
        """Extract all features for art generation."""
        return {
            "commits": self._get_commits(),
            "file_stats": self._get_file_stats(),
            "contributors": self._get_contributors(),
            "timeline": self._get_timeline(),
            "branches": self._get_branches(),
        }
    
    def _run_git(self, *args) -> str:
        """Run git command and return output."""
        result = subprocess.run(
            ["git", "-C", str(self.repo_path)] + list(args),
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    
    def _get_commits(self) -> List[Dict[str, Any]]:
        """Get commit history with metadata."""
        try:
            log = self._run_git(
                "log",
                "--pretty=format:%H|%an|%ae|%at|%s",
                "--numstat",
                "--no-merges"
            )
        except subprocess.CalledProcessError:
            return []
        
        commits = []
        current_commit = None
        
        for line in log.split("\n"):
            if "|" in line and len(line.split("|")) == 5:
                # New commit header
                if current_commit:
                    commits.append(current_commit)
                
                hash_, author, email, timestamp, subject = line.split("|")
                current_commit = {
                    "hash": hash_,
                    "author": author,
                    "email": email,
                    "timestamp": int(timestamp),
                    "datetime": datetime.fromtimestamp(int(timestamp)),
                    "subject": subject,
                    "additions": 0,
                    "deletions": 0,
                    "files_changed": []
                }
            elif line and current_commit and "\t" in line:
                # File change stats
                parts = line.split("\t")
                if len(parts) == 3:
                    add, delete, filename = parts
                    if add != "-" and delete != "-":
                        current_commit["additions"] += int(add)
                        current_commit["deletions"] += int(delete)
                        current_commit["files_changed"].append({
                            "name": filename,
                            "additions": int(add),
                            "deletions": int(delete)
                        })
        
        if current_commit:
            commits.append(current_commit)
        
        return commits
    
    def _get_file_stats(self) -> Dict[str, int]:
        """Get file type distribution."""
        try:
            files = self._run_git("ls-files").split("\n")
        except subprocess.CalledProcessError:
            return {}
        
        stats = defaultdict(int)
        for file in files:
            if not file:
                continue
            ext = Path(file).suffix or "no-extension"
            stats[ext] += 1
        
        return dict(stats)
    
    def _get_contributors(self) -> List[Dict[str, Any]]:
        """Get contributor statistics."""
        try:
            shortlog = self._run_git("shortlog", "-sne", "--no-merges")
        except subprocess.CalledProcessError:
            return []
        
        contributors = []
        for line in shortlog.split("\n"):
            if not line.strip():
                continue
            # Format: "    12  Author Name <email>"
            parts = line.strip().split("\t")
            if len(parts) == 2:
                count = int(parts[0])
                # Extract name and email
                author_email = parts[1]
                if "<" in author_email and ">" in author_email:
                    name = author_email[:author_email.index("<")].strip()
                    email = author_email[author_email.index("<")+1:author_email.index(">")]
                else:
                    name = author_email
                    email = ""
                
                contributors.append({
                    "name": name,
                    "email": email,
                    "commits": count
                })
        
        return contributors
    
    def _get_timeline(self) -> Dict[str, int]:
        """Get commit activity over time (by month)."""
        commits = self._get_commits()
        timeline = defaultdict(int)
        
        for commit in commits:
            month = commit["datetime"].strftime("%Y-%m")
            timeline[month] += 1
        
        return dict(sorted(timeline.items()))
    
    def _get_branches(self) -> List[str]:
        """Get list of branches."""
        try:
            branches = self._run_git("branch", "-a").split("\n")
            return [b.strip().lstrip("* ") for b in branches if b.strip()]
        except subprocess.CalledProcessError:
            return []
