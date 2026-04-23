# config.py
# ══════════
# Προεπιλεγμένες τιμές — δεν περιέχουν κωδικούς ή προσωπικά στοιχεία.
# Όλες οι πραγματικές τιμές αποθηκεύονται τοπικά στο data/local_settings.json
# και φορτώνονται αυτόματα κατά την εκκίνηση μέσω _load_local().

# ── MySchool credentials (κενά — συμπληρώνονται από Ρυθμίσεις) ────────────
MYSCHOOL_USER = ''
MYSCHOOL_PASS = ''

# ── Email ──────────────────────────────────────────────────────────────────
SMTP_HOST     = 'mail.sch.gr'
FROM_EMAIL    = ''
FROM_NAME     = ''
FROM_PASSWORD = ''
TEST_EMAIL    = ''

# ── Υπογραφή email ────────────────────────────────────────────────────────
EMAIL_SIGNATURE = ''


def email_signature():
    """Επιστρέφει την υπογραφή email βάσει των ρυθμίσεων."""
    return EMAIL_SIGNATURE


# ── Θέμα & σώμα email ──────────────────────────────────────────────────────
SUBJECT       = 'Παρόντες με ενεργή μακροχρόνια άδεια'
BODY_TEMPLATE = (
    'Καλημέρα,\n\n'
    'Εντοπίστηκαν εκπαιδευτικοί στο σχολείο {school} που εμφανίζονται ως παρόντες '
    'ενώ βρίσκονται σε μακροχρόνια άδεια (επισυνάπτεται αρχείο).\n\n'
    'Παρακαλούμε για τις ενέργειές σας.\n\n'
    'Με εκτίμηση,\n'
    'Για τη Δ/νση ΠΕ ...,\n'
    'Υπεύθυνος MySchool\n'
    'τηλ. ...'
)

# ── Αρχείο Αδυνατούντων υπό έγκριση ──────────────────────────────────────
ADY_XORIS_EGKRISI_PATH = ''


# ── Φόρτωση τοπικών ρυθμίσεων (data/local_settings.json) ─────────────────
def _load_local():
    """
    Φορτώνει τοπικές ρυθμίσεις από data/local_settings.json και
    αντικαθιστά τις προεπιλεγμένες τιμές παραπάνω.
    Το αρχείο ΔΕΝ ανεβαίνει στο GitHub (βλ. .gitignore).
    """
    import json, os
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'local_settings.json')
    if not os.path.exists(path):
        return
    try:
        with open(path, encoding='utf-8') as f:
            data = json.load(f)
        g = globals()
        for k, v in data.items():
            if k in g:          # ενημέρωσε μόνο γνωστές μεταβλητές
                g[k] = v
    except Exception:
        pass  # αν το αρχείο είναι κατεστραμμένο, χρησιμοποιούμε defaults


_load_local()
