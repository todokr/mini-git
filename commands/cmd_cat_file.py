from models import GitRepository

def run(repo_path: str, sha: str) -> str:
    repo = GitRepository.load(repo_path)
    obj = repo.load_object(sha)
    return obj.serialize().decode('utf-8')
