import sys
import json
import urllib.request
import urllib.error

def buscar_atividade_github(username):
    url = f"https://api.github.com/users/{username}/events"

    try:
        with urllib.request.urlopen(url) as response:
            if response.status != 200:
                print(f"Erro: Status {response.status} ao buscar dados do usuário '{username}'")
                return None

            dados = response.read()
            eventos = json.loads(dados)
            return eventos
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"Usuário '{username}' não encontrado.")
        else:
            print(f"Erro HTTP: {e.code} ao acessar a API do GitHub.")
        return None
    except urllib.error.URLError as e:
        print(f"Erro de conexão: {e.reason}")
        return None
    except Exception as e:
        print(f"Erro inesperado: {e}")
        return None

def formatar_evento(evento):
    tipo = evento.get("type")
    repo = evento.get("repo", {}).get("name", "unknown/repo")

    if tipo == "PushEvent":
        qtd_commits = len(evento.get("payload", {}).get("commits", []))
        return f"Pushed {qtd_commits} commit{'s' if qtd_commits != 1 else ''} to {repo}"

    elif tipo == "IssuesEvent":
        action = evento.get("payload", {}).get("action", "performed an action on")
        issue = evento.get("payload", {}).get("issue", {})
        title = issue.get("title", "an issue")
        return f"{action.capitalize()} issue '{title}' in {repo}"

    elif tipo == "IssueCommentEvent":
        action = evento.get("payload", {}).get("action", "commented on")
        return f"{action.capitalize()} an issue comment in {repo}"

    elif tipo == "PullRequestEvent":
        action = evento.get("payload", {}).get("action", "performed an action on")
        pr = evento.get("payload", {}).get("pull_request", {})
        title = pr.get("title", "a pull request")
        return f"{action.capitalize()} pull request '{title}' in {repo}"

    elif tipo == "WatchEvent":
        return f"Starred {repo}"

    elif tipo == "CreateEvent":
        ref_type = evento.get("payload", {}).get("ref_type", "something")
        ref = evento.get("payload", {}).get("ref", "")
        if ref:
            return f"Created {ref_type} '{ref}' in {repo}"
        else:
            return f"Created {ref_type} in {repo}"

    elif tipo == "ForkEvent":
        return f"Forked {repo}"

    else:
        return f"{tipo} on {repo}"

def main():
    if len(sys.argv) != 2:
        print("Uso: python github_activity.py <username>")
        return

    username = sys.argv[1]

    eventos = buscar_atividade_github(username)
    if eventos is None:
        return

    if len(eventos) == 0:
        print(f"Nenhuma atividade recente encontrada para o usuário '{username}'.")
        return

    for evento in eventos:
        print(formatar_evento(evento))

if __name__ == "__main__":
    main()
