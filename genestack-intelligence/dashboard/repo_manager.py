"""
Simple Repository Manager for Genestack Intelligence
Handles cloning and managing any Git repository for analysis
"""
import os
import subprocess
import tempfile
import shutil
from pathlib import Path
import streamlit as st


class RepoManager:
    """Manages Git repository cloning and access"""
    
    def __init__(self):
        self.temp_dir = None
        self.repo_path = None
        
    def get_repo_path(self, repo_url: str = None) -> str:
        """
        Get the path to analyze. If repo_url is provided and different from current,
        clone it to a temp directory. Otherwise use current directory.
        """
        # If no URL provided, use current directory
        if not repo_url:
            return os.getcwd()
        
        # Get current repo URL
        current_url = self._get_current_repo_url()
        
        # If URLs match, use current directory
        if current_url and self._normalize_url(current_url) == self._normalize_url(repo_url):
            return os.getcwd()
        
        # Check if we already have this repo cloned in session
        if 'cloned_repo_path' in st.session_state:
            if st.session_state.get('cloned_repo_url') == repo_url:
                if os.path.exists(st.session_state['cloned_repo_path']):
                    return st.session_state['cloned_repo_path']
        
        # Need to clone the repo
        return self._clone_repo(repo_url)
    
    def _get_current_repo_url(self) -> str:
        """Get the URL of the current Git repository"""
        try:
            result = subprocess.run(
                ['git', 'config', '--get', 'remote.origin.url'],
                cwd=os.getcwd(),
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        return ""
    
    def _normalize_url(self, url: str) -> str:
        """Normalize Git URL for comparison"""
        url = url.strip()
        # Convert SSH to HTTPS
        if url.startswith("git@"):
            url = url.replace(":", "/").replace("git@", "https://")
        elif url.startswith("git://"):
            url = url.replace("git://", "https://")
        # Remove .git suffix
        if url.endswith(".git"):
            url = url[:-4]
        # Remove trailing slash
        url = url.rstrip("/")
        return url.lower()
    
    def _clone_repo(self, repo_url: str) -> str:
        """Clone repository to temp directory"""
        with st.spinner(f"🔄 Cloning repository: {repo_url}"):
            try:
                # Create temp directory
                temp_base = tempfile.gettempdir()
                repo_name = repo_url.split('/')[-1].replace('.git', '')
                clone_path = os.path.join(temp_base, f"genestack_analysis_{repo_name}")
                
                # Remove if exists
                if os.path.exists(clone_path):
                    shutil.rmtree(clone_path)
                
                # Clone repo
                result = subprocess.run(
                    ['git', 'clone', '--depth', '1', repo_url, clone_path],
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minute timeout
                )
                
                if result.returncode != 0:
                    st.error(f"❌ Failed to clone repository: {result.stderr}")
                    return os.getcwd()
                
                # Store in session state
                st.session_state['cloned_repo_path'] = clone_path
                st.session_state['cloned_repo_url'] = repo_url
                
                st.success(f"✅ Repository cloned successfully!")
                return clone_path
                
            except subprocess.TimeoutExpired:
                st.error("❌ Clone operation timed out. Repository may be too large.")
                return os.getcwd()
            except Exception as e:
                st.error(f"❌ Error cloning repository: {str(e)}")
                return os.getcwd()
    
    def cleanup(self):
        """Clean up temporary cloned repositories"""
        if 'cloned_repo_path' in st.session_state:
            path = st.session_state['cloned_repo_path']
            if os.path.exists(path):
                try:
                    shutil.rmtree(path)
                except:
                    pass
            del st.session_state['cloned_repo_path']
            if 'cloned_repo_url' in st.session_state:
                del st.session_state['cloned_repo_url']


# Global instance
_repo_manager = RepoManager()


def get_repo_path(repo_url: str = None) -> str:
    """Get the repository path to analyze"""
    return _repo_manager.get_repo_path(repo_url)


def cleanup_repos():
    """Clean up cloned repositories"""
    _repo_manager.cleanup()
