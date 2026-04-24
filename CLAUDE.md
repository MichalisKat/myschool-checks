# MySchool Checks — Οδηγός για Claude

## Τι είναι αυτό το project

Python εφαρμογή Windows για αυτοματοποιημένους ελέγχους δεδομένων εκπαιδευτικών στο MySchool (Διεύθυνση Π.Ε. Ανατολικής Θεσσαλονίκης). Κατεβάζει αρχεία μέσω Selenium/Chrome ή Firefox, επεξεργάζεται CSV/Excel με pandas, παράγει αποτελέσματα Excel και στέλνει emails.

**Repo:** https://github.com/MichalisKat/myschool-checks  
**Υπεύθυνος:** Μιχάλης Κατσιρντάκης  
**Τρέχουσα έκδοση:** 0.9.0 (beta)

---

## Δομή project

```
myschool-checks/
├── MySchoolChecks/
│   ├── main.py              # Κύριο αρχείο — UI, splash, settings, load_checks()
│   ├── config.py            # Ρυθμίσεις — φορτώνει JSON + keyring
│   ├── encryption.py        # Keyring wrapper — store/get/delete credentials
│   ├── setup_credentials.py # CLI wizard πρώτης ρύθμισης credentials
│   ├── app.ico              # Εικονίδιο εφαρμογής (6 μεγέθη: 16-256px)
│   ├── startup.mp3          # Μουσική splash (Pixabay License — δεν ανεβαίνει στο GitHub)
│   ├── checks/              # Ένα .py ανά έλεγχο
│   └── core/
│       ├── framework.py     # run_check(), get_downloaded_file(), send_email()
│       └── downloader.py    # MySchoolDownloader, get_downloads_dir()
├── MySchoolChecks_Odigos.pdf  # Οδηγός χρήστη (ReportLab, ελληνικά)
├── MySchoolChecks.spec      # PyInstaller spec — ΜΗΝ το διαγράψεις
├── build_executable.bat     # Φτιάχνει dist\MySchoolChecks.exe
├── compile_installer.bat    # Φτιάχνει myschool-checks-0.9.0-setup.exe
├── myschool-checks.nsi      # NSIS script για τον installer
├── SECURITY.md              # Τεκμηρίωση ασφάλειας credentials
└── CLAUDE.md                # Αυτό το αρχείο
```

---

## Κρίσιμες αρχιτεκτονικές αποφάσεις

### Credentials — Keyring (Windows Credential Manager)
Τα ευαίσθητα credentials (`MYSCHOOL_USER`, `MYSCHOOL_PASS`, `FROM_PASSWORD`) αποθηκεύονται **μόνο** στο Windows Credential Manager μέσω του `keyring` module. Δεν γράφονται σε κανένα αρχείο.

- `encryption.py` — wrapper: `store_credential`, `get_credential`, `delete_credential`
- `config.py` → `_load_local()` — φορτώνει μη-ευαίσθητα από JSON, ευαίσθητα από keyring
- `main.py` → `_save_config()` — αποθηκεύει ευαίσθητα στο keyring, μη-ευαίσθητα στο JSON
- `*.mp3` είναι στο `.gitignore` — δεν ανεβαίνει στο GitHub

### Paths — _app_base()
Βρίσκεται στο `main.py`:
- **Εγκατεστημένο (Program Files)** → `%LOCALAPPDATA%\MySchoolChecks\`
- **Portable (dist\)** → δίπλα στο .exe
- **Development** → φάκελος του κώδικα

Η ίδια λογική υπάρχει και στο `config.py` (`_load_local()`) και στο `framework.py`.

### Downloads — _docs_base()
Τα κατεβασμένα στατιστικά αρχεία πηγαίνουν στο `Documents\MySchoolChecks\downloads\YYYYMMDD\` (ίδιος φάκελος με τα results) — ΟΧΙ στο LOCALAPPDATA.

### Αποθήκευση δεδομένων
| Τι | Πού |
|---|---|
| Μη-ευαίσθητες ρυθμίσεις | `%LOCALAPPDATA%\MySchoolChecks\data\local_settings.json` |
| Ευαίσθητα credentials | Windows Credential Manager (keyring) |
| Downloads | `Documents\MySchoolChecks\downloads\YYYYMMDD\` |
| Αποτελέσματα | `Documents\MySchoolChecks\results_YYYYMMDD\` |

### Browser
Υποστηρίζονται Chrome και Firefox. Επιλογή από Ρυθμίσεις → Σύνδεση → radio button.
- `BROWSER = 'chrome'` ή `'firefox'` στο config
- `downloader.py` → `MySchoolDownloader(browser=...)` — split λογική Chrome/Firefox

### Frozen exe (PyInstaller)
- `sys.frozen = True` → το app τρέχει ως .exe
- `sys._MEIPASS` → temp φάκελος (διαγράφεται μετά) — ΔΕΝ γράφουμε εκεί
- `sys.executable` → το .exe αρχείο
- Τα checks φορτώνονται δυναμικά — στο frozen exe δεν υπάρχουν .py, γι' αυτό το spec τα bundlάρει με `--add-data`

### Checks
Κάθε αρχείο στο `checks/` είναι ανεξάρτητος έλεγχος. Πρέπει να έχει:
- `CHECK_TITLE` — τίτλος
- `run()` — κύρια συνάρτηση που καλεί `framework.run_check()`

---

## Διαδικασία build & release

### Όταν αλλάζει κώδικας:

```bash
# 1. Πάρε τελευταίες αλλαγές
git pull origin main

# 2. Φτιάξε νέο exe (κρατάει αυτόματα τα credentials)
build_executable.bat

# 3. Φτιάξε νέο installer
compile_installer.bat

# 4. Απεγκατάστησε παλιά έκδοση
# Ρυθμίσεις → Εφαρμογές → MySchool Checks → Απεγκατάσταση

# 5. Εγκατάστησε νέα
# Τρέξε myschool-checks-0.9.0-setup.exe

# 6. Ανέβασε στο GitHub Releases
gh release delete v0.9.0 --yes
gh release create v0.9.0 "myschool-checks-0.9.0-setup.exe" --title "MySchool Checks v0.9.0 (beta)" --notes "Ενημερωμένη έκδοση"
```

### Όταν αλλάζει μόνο ο installer (π.χ. .nsi, LICENSE):
Τρέξε μόνο βήματα 3 → 4 → 5 → 6. Το `build_executable.bat` δεν χρειάζεται.

### Versioning
- Τρέχουσα: `0.9.0` (beta)
- Stable release: `1.0.0` (μετά από testing)
- Αλλαγή version: στο `myschool-checks.nsi` (`APP_VERSION`) και στο `compile_installer.bat`

### Backup credentials
Το `build_executable.bat` κρατάει αυτόματα τα credentials:
- Πριν το build: backup από `%LOCALAPPDATA%\MySchoolChecks\data\` ή `dist\data\`
- Μετά το build: επαναφορά και στα δύο μέρη

---

## Εργαλεία που χρειάζονται

| Εργαλείο | Path |
|---|---|
| Python 3.11 | `C:\Users\katsi\AppData\Local\Programs\Python\Python311\` |
| PyInstaller | `C:\Users\katsi\AppData\Local\Programs\Python\Python311\Scripts\pyinstaller.exe` |
| keyring | `pip install keyring` (απαιτείται για build) |
| NSIS | `C:\Program Files (x86)\NSIS\makensis.exe` |
| Git | Στο PATH |
| GitHub CLI | Στο PATH (`gh auth login` αν δεν είναι συνδεδεμένο) |

---

## Συνηθισμένα προβλήματα & λύσεις

| Πρόβλημα | Αιτία | Λύση |
|---|---|---|
| "keyring μη διαθέσιμο" στο app | keyring δεν είναι εγκατεστημένο στο Python | `pip install keyring` → ξανabuild |
| Batch file με σκουπίδια | LF αντί CRLF | `$content -replace "(?<!\r)\n", "\`r\`n"` σε PowerShell |
| Settings χάθηκαν μετά rebuild | Backup από λάθος φάκελο | Το build_executable.bat το διορθώνει αυτόματα |
| WinError 5 (Program Files) | Εγγραφή σε Program Files χωρίς admin | `_app_base()` ανακατευθύνει στο LOCALAPPDATA |
| 0 checks φορτώθηκαν | Import error στο frozen exe | Ελέγχα `checks_errors.log` στο Desktop |
| Infinite pip loop | `sys.executable` = το .exe | Skip pip όταν `sys.frozen = True` |
| Spec file not found | `del /q *.spec` στο build script | Το script ΔΕΝ διαγράφει το .spec |
| git index.lock | Crashed git process | `del /f .git\index.lock` στο repo folder |

---

## Pending / Επόμενα βήματα

- [ ] Beta testing → stable release v1.0.0
- [ ] MSIX package για Microsoft Store (αναβλήθηκε — χρειάζεται Windows SDK + Partner Center)
- [ ] Αν χρειαστεί νέα έκδοση: αλλαγή `APP_VERSION` στο `.nsi` και όνομα setup στο `compile_installer.bat`

---

## Git workflow (δύο υπολογιστές)

**Πάντα πριν δουλέψεις:**
```bash
git pull origin main
```

**Μετά από αλλαγές:**
```bash
git add .
git commit -m "περιγραφή"
git push origin main
```
