# MySchool Checks — Οδηγός για Claude

## Τι είναι αυτό το project

Python εφαρμογή Windows για αυτοματοποιημένους ελέγχους δεδομένων εκπαιδευτικών στο MySchool (Διεύθυνση Π.Ε. Ανατολικής Θεσσαλονίκης). Κατεβάζει αρχεία μέσω Selenium/Chrome, επεξεργάζεται CSV/Excel με pandas, παράγει αποτελέσματα Excel και στέλνει emails.

**Repo:** https://github.com/MichalisKat/myschool-checks  
**Υπεύθυνος:** Μιχάλης Κατσιρντάκης

---

## Δομή project

```
myschool-checks/
├── MySchoolChecks/
│   ├── main.py              # Κύριο αρχείο — UI, splash, settings, load_checks()
│   ├── config.py            # Ρυθμίσεις — φορτώνει data/local_settings.json
│   ├── checks/              # Ένα .py ανά έλεγχο
│   └── core/
│       ├── framework.py     # run_check(), get_downloaded_file(), send_email()
│       └── downloader.py    # MySchoolDownloader, get_downloads_dir()
├── MySchoolChecks.spec      # PyInstaller spec — ΜΗΝ το διαγράψεις
├── build_executable.bat     # Φτιάχνει dist\MySchoolChecks.exe
├── compile_installer.bat    # Φτιάχνει myschool-checks-1.0-setup.exe
├── myschool-checks.nsi      # NSIS script για τον installer
└── CLAUDE.md                # Αυτό το αρχείο
```

---

## Κρίσιμες αρχιτεκτονικές αποφάσεις

### Paths — _app_base()
Η πιο κρίσιμη συνάρτηση. Βρίσκεται στο `main.py`:
- **Εγκατεστημένο (Program Files)** → `%LOCALAPPDATA%\MySchoolChecks\`
- **Portable (dist\)** → δίπλα στο .exe
- **Development** → φάκελος του κώδικα

Η ίδια λογική υπάρχει και στο `config.py` (`_load_local()`) και στο `framework.py`.

### Αποθήκευση δεδομένων
| Τι | Πού |
|---|---|
| Ρυθμίσεις (credentials) | `%LOCALAPPDATA%\MySchoolChecks\data\local_settings.json` |
| Downloads | `%LOCALAPPDATA%\MySchoolChecks\downloads\YYYYMMDD\` |
| Αποτελέσματα | `Documents\MySchoolChecks\results_YYYYMMDD\` |

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
# Τρέξε myschool-checks-1.0-setup.exe

# 6. Ανέβασε στο GitHub Releases
gh release delete v1.0 --yes
gh release create v1.0 "myschool-checks-1.0-setup.exe" --title "MySchool Checks v1.0" --notes "Ενημερωμένη έκδοση"
```

### Όταν αλλάζει μόνο ο installer (π.χ. .nsi, LICENSE):
Τρέξε μόνο βήματα 3 → 4 → 5 → 6. Το `build_executable.bat` δεν χρειάζεται.

### Backup credentials
Το `build_executable.bat` κρατάει αυτόματα τα credentials:
- Πριν το build: backup από `%LOCALAPPDATA%\MySchoolChecks\data\` ή `dist\data\`
- Μετά το build: επαναφορά και στα δύο μέρη

---

## Εργαλεία που χρειάζονται

| Εργαλείο | Path |
|---|---|
| Python 3.14 | `%LOCALAPPDATA%\Python\pythoncore-3.14-64\` |
| PyInstaller | `%LOCALAPPDATA%\Python\pythoncore-3.14-64\Scripts\pyinstaller.exe` |
| NSIS | `C:\Program Files (x86)\NSIS\makensis.exe` |
| Git | Στο PATH |
| GitHub CLI | Στο PATH (`gh auth login` αν δεν είναι συνδεδεμένο) |

---

## Συνηθισμένα προβλήματα & λύσεις

| Πρόβλημα | Αιτία | Λύση |
|---|---|---|
| Batch file με σκουπίδια | LF αντί CRLF | `$content -replace "(?<!\r)\n", "\`r\`n"` σε PowerShell |
| Settings χάθηκαν μετά rebuild | Backup από λάθος φάκελο | Το νέο build_executable.bat το διορθώνει |
| WinError 5 (Program Files) | Εγγραφή σε Program Files χωρίς admin | `_app_base()` ανακατευθύνει στο LOCALAPPDATA |
| 0 checks φορτώθηκαν | Import error στο frozen exe | Ελέγχα `checks_errors.log` στο Desktop |
| Infinite pip loop | `sys.executable` = το .exe | Skip pip όταν `sys.frozen = True` |
| Spec file not found | `del /q *.spec` στο build script | Το νέο script ΔΕΝ διαγράφει το .spec |

---

## Pending / Επόμενα βήματα

- [ ] MSIX package για Microsoft Store (χρειάζεται Windows SDK + Partner Center account + PNG assets)
- [ ] Αν χρειαστεί νέα έκδοση: αλλαγή version string στο .nsi και .spec

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
