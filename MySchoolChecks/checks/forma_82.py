"""
checks/forma_82.py
══════════════════
Επιβεβαίωση Δεδομένων Σχολείων (8.2).
Εντοπίζει σχολεία που δεν έχουν επιβεβαιώσει τα δεδομένα τους πριν από cutoff ημερομηνία.
"""

import pandas as pd
import config
from core.framework import ask_file, get_downloaded_file, ask_date_ddmmyyyy

# ── Μεταδεδομένα ────────────────────────────────────────────────────────────
CHECK_TITLE    = 'Επιβεβαίωση Δεδομένων Σχολείων'
CHECK_DESCRIPTION = 'Σχολεία που δεν έχουν ολοκληρώσει επιβεβαίωση δεδομένων'
RESULTS_FOLDER = 'epivevaiosi_dedomenon'
HAS_EMAIL      = True

EIDH        = ['Δημοτικά Σχολεία', 'Νηπιαγωγεία']
SRC_DATE_COL = 'Τελευταία Ενημέρωση Φόρμας Επιβεβαίωση Δεδομένων'

COLUMNS = [
    ('Κωδικός Υπ. Σχολ.',              16),
    ('Ονομασία Σχολείου',               40),
    ('Τηλέφωνο',                        16),
    ('Email',                           32),
    ('Τελευταία Επιβεβαίωση Δεδομένων', 30),
]

SCHOOL_COLUMN = 'Ονομασία Σχολείου'
EMAIL_COLUMN  = 'Email'

CENTER_COLS = {'Κωδικός Υπ. Σχολ.', 'Τηλέφωνο', 'Τελευταία Επιβεβαίωση Δεδομένων'}

EMAIL_SUBJECT = 'Υπενθύμιση: Επιβεβαίωση δεδομένων στο myschool'
EMAIL_BODY    = lambda school='': (
    'Καλημέρα σας!\n\n'
    'Για τους παραλήπτες του παρόντος δεν έχει γίνει επιβεβαίωση δεδομένων '
    'στο myschool. Παρακαλούμε για τις ενέργειες σας.\n\n'
    + config.email_signature()
)


# ── Είσοδος ─────────────────────────────────────────────────────────────────
def ask_inputs():
    path   = get_downloaded_file('8.2', 'Αρχείο 8.2 [xls / xlsx]:')
    cutoff = ask_date_ddmmyyyy(
        '\nΗμερομηνία cutoff (DD/MM/YYYY) — εγγραφές ΠΡΙΝ από αυτή θα εμφανιστούν:\n> '
    )
    return {'path': path, 'today': cutoff, 'cutoff': cutoff}


# ── Λογική ──────────────────────────────────────────────────────────────────
def process(ctx):
    cutoff = ctx['cutoff']
    df     = pd.read_excel(ctx['path'])
    print(f'  ✓ {len(df)} γραμμές φορτώθηκαν')

    df = df[df['Είδος Σχολείου'].isin(EIDH)].copy()
    print(f'  → {len(df)} μετά φίλτρο Είδους Σχολείου')

    df = df[df['Αναστολή'].str.strip() == 'Όχι'].copy()
    print(f'  → {len(df)} μετά φίλτρο Αναστολής')

    df[SRC_DATE_COL] = pd.to_datetime(df[SRC_DATE_COL])
    df = df[df[SRC_DATE_COL] < cutoff].copy()
    print(f'  → {len(df)} με τελευταία επιβεβαίωση πριν {cutoff.strftime("%d/%m/%Y")}')

    if df.empty:
        return pd.DataFrame()

    df_out = pd.DataFrame({
        'Κωδικός Υπ. Σχολ.'             : df['Κωδικός Υπ. Σχολ.'].astype(str),
        'Ονομασία Σχολείου'              : df['Ονομασία Σχολείου'],
        'Τηλέφωνο'                       : df['Τηλέφωνο'].astype(str),
        'Email'                          : df['Email'],
        'Τελευταία Επιβεβαίωση Δεδομένων': df[SRC_DATE_COL].dt.strftime('%d/%m/%Y %H:%M'),
    }).sort_values('Ονομασία Σχολείου').reset_index(drop=True)

    return df_out


def test_body(df_out, today, schools):
    date_col = 'Τελευταία Επιβεβαίωση Δεδομένων'
    oldest = newest = ''
    if date_col in df_out.columns and len(df_out) > 0:
        dates = df_out[date_col].dropna()
        if len(dates):
            oldest = dates.min()
            newest = dates.max()
    return (
        f'Σύνοψη ελέγχου επιβεβαίωσης δεδομένων — cutoff {today.strftime("%d/%m/%Y")}\n'
        f'{"─"*50}\n'
        f'Σχολεία που δεν έχουν επιβεβαιώσει: {len(df_out)}\n'
        f'Τελευταία επιβεβαίωση: από {oldest} έως {newest}\n'
    )
