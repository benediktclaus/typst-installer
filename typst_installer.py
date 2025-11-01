import tkinter as tk
from tkinter import messagebox
import requests
from pathlib import Path
from urllib.parse import urlparse
import threading
import zipfile
import os
import shutil
import tempfile

# --- KONFIGURATION ---
# Der finale Zielordner für die Typst-Pakete
# os.getenv('APPDATA') zeigt auf C:\Users\DeinName\AppData\Roaming
TYPST_PACKAGE_PATH = Path(os.getenv('APPDATA')) / 'typst' / 'packages' / 'local'

# --- HILFSFUNKTIONEN FÜR THREAD-SICHERES FEEDBACK ---

def show_success_and_quit(root, msg):
    """Zeigt die Erfolgsmeldung und schließt dann die App."""
    messagebox.showinfo("Erfolg", msg)
    root.destroy()

def show_error_and_quit(root, msg):
    """Zeigt die Fehlermeldung und schließt dann die App."""
    messagebox.showerror("Fehler", msg)
    root.destroy()

# --- KERNLOGIK ---

def get_repo_owner_and_name(url):
    """Extrahiert 'owner/name' aus einer GitHub-URL."""
    parsed_path = urlparse(url).path
    # Entfernt führende/nachfolgende Schrägstriche, z.B. '/user/repo/' -> 'user/repo'
    parts = parsed_path.strip('/').split('/')
    if len(parts) >= 2 and parts[0] and parts[1]:
        return parts[0], parts[1]
    else:
        raise ValueError(f"Konnte Owner/Repo aus der URL nicht extrahieren: {url}")

def download_and_install_package(root, repo_url):
    """
    Nimmt eine URL, lädt das Release herunter, entpackt es und installiert es
    im Typst-Paketordner. Diese Funktion läuft in einem separaten Thread.
    """
    try:
        # 1. Repo-Infos holen
        owner, repo = get_repo_owner_and_name(repo_url)
        print(f"Extrahiert: Owner={owner}, Repo={repo}")

        # 2. GitHub-API nach dem neuesten Release fragen
        api_url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
        print(f"Frage API an: {api_url}")
        response = requests.get(api_url)
        response.raise_for_status() # Löst Fehler aus (z.B. 404), wenn Release/Repo fehlt
        data = response.json()

        # 3. Download-URL für den Quellcode (ZIP) finden
        zip_url = data.get('zipball_url')
        tag_name = data.get('tag_name', 'latest')
        if not zip_url:
            # Zeigt Fehler an, schließt aber nicht (damit Nutzer URL korrigieren kann)
            root.after(0, lambda: messagebox.showerror("Fehler", "Konnte 'zipball_url' im Release nicht finden."))
            return

        # 4. Gesamten Prozess in einem temporären Ordner durchführen
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            print(f"Arbeite im temporären Ordner: {temp_path}")

            # 5. ZIP-Datei in den temporären Ordner herunterladen
            file_name = f"{repo}-{tag_name}.zip"
            destination_zip = temp_path / file_name
            print(f"Lade '{file_name}' herunter nach '{destination_zip}'...")

            file_response = requests.get(zip_url)
            file_response.raise_for_status()
            
            with open(destination_zip, 'wb') as f:
                f.write(file_response.content)
                
            print(f"Download abgeschlossen. Beginne Entpacken...")

            # 6. ZIP-Datei im selben temporären Ordner entpacken
            with zipfile.ZipFile(destination_zip, 'r') as zip_ref:
                zip_ref.extractall(temp_path)

            # 7. Den inneren, von GitHub benannten Ordner finden
            extracted_folders = [f for f in temp_path.iterdir() if f.is_dir()]
            if not extracted_folders:
                raise Exception("Konnte den Hauptordner in der ZIP-Datei nicht finden.")
            
            inner_folder_path = extracted_folders[0]
            print(f"Gefundener Quellordner: {inner_folder_path.name}")

            # 8. Finalen Zielordner im Typst-Verzeichnis definieren
            final_dest_folder = TYPST_PACKAGE_PATH / repo 
            print(f"Zielordner: {final_dest_folder}")

            # 9. Sicherstellen, dass der Typst-Zielordner (.../local) existiert
            TYPST_PACKAGE_PATH.mkdir(parents=True, exist_ok=True)

            # 10. Alten Zielordner löschen, falls er existiert (wurde vom Nutzer genehmigt)
            if final_dest_folder.exists():
                print(f"Lösche altes Paket: {final_dest_folder}")
                shutil.rmtree(final_dest_folder)
            
            # 11. Den entpackten Ordner an den finalen Ort verschieben & umbenennen
            shutil.move(str(inner_folder_path), str(final_dest_folder))
            print(f"Paket installiert nach: {final_dest_folder}")

        # 12. Aufräumen (ZIP, Temp-Ordner) passiert automatisch durch 'with tempfile.TemporaryDirectory()'
        
        # 13. Erfolgsmeldung an Haupt-Thread senden
        success_msg = f"Paket '{repo}' erfolgreich im Typst-Verzeichnis installiert!"
        root.after(0, lambda: show_success_and_quit(root, success_msg))
        
    except Exception as e:
        # 14. Fehlermeldung an Haupt-Thread senden
        error_msg = f"Ein Fehler ist aufgetreten:\n{e}"
        print(error_msg)
        root.after(0, lambda: show_error_and_quit(root, error_msg))

# --- VERBINDUNGSFUNKTION (GUI-THREAD) ---

def start_download_thread(root, url_entry):
    """
    Prüft die Eingabe, checkt auf Konflikte und startet DANN 
    erst den Download-Thread. Läuft im Haupt-Thread.
    """
    repo_url = url_entry.get()
    
    if not repo_url:
        messagebox.showwarning("Leere Eingabe", "Bitte eine GitHub-Repository-URL einfügen.")
        return

    # 1. Konfliktprüfung (im Haupt-Thread, vor dem Download)
    try:
        # Repo-Namen holen, um den Zielpfad zu kennen
        owner, repo = get_repo_owner_and_name(repo_url)
    except ValueError as e:
        messagebox.showerror("Ungültige URL", f"Konnte die URL nicht verarbeiten:\n{e}")
        return

    # 2. Finalen Zielpfad konstruieren
    final_dest_folder = TYPST_PACKAGE_PATH / repo
    
    # 3. Prüfen, ob dieser Ordner bereits existiert
    if final_dest_folder.exists():
        # 4. Den Nutzer fragen (sicher, da im Haupt-Thread)
        user_choice = messagebox.askyesno(
            "Konflikt",
            f"Das Paket '{repo}' existiert bereits im local-Ordner.\n\n"
            f"Möchtest du es überschreiben?"
        )
        
        # 5. Bei "Nein" die ganze Aktion abbrechen
        if not user_choice:
            print("Installation durch Nutzer abgebrochen.")
            return
    
    # 6. Wenn wir hier ankommen, Download-Thread starten
    print("Starte Download-Thread...")
    download_thread = threading.Thread(target=download_and_install_package, args=(root, repo_url,))
    download_thread.start()


# --- GUI ERSTELLEN ---

# 1. Das Hauptfenster
root = tk.Tk()
root.title("Typst Paket-Installer")
root.geometry("500x150")

# 2. Label für die Anweisung
url_label = tk.Label(root, text="GitHub-Repository-URL einfügen:")
url_label.pack(pady=5)

# 3. Eingabefeld für die URL
url_entry = tk.Entry(root, width=60)
url_entry.pack(pady=5, padx=10)

# 4. Download/Install-Button
#    lambda ist nötig, um Argumente (root, url_entry) an die Funktion zu übergeben
download_button = tk.Button(root, text="Paket herunterladen & installieren",
                            command=lambda: start_download_thread(root, url_entry)) 
download_button.pack(pady=20)

# 5. Anwendung starten und auf Events warten
root.mainloop()
