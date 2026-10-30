"""The DELF B2 vocabulary deck as a topic: one chapter (90–96) per theme, each with the word list
and one review card per word. Source: data/vocab_b2.tsv (French <TAB> meaning <TAB> tag)."""
import csv
from pathlib import Path

from fr import NOTE, P, TABLE, Book

THEMES = [  # tag, chapter, title, what the theme covers in the exam
    ("MKF::03_Sante", 90, "La santé", "la santé publique, les addictions, le système de soins"),
    ("MKF::04_Education", 91, "L'éducation et la formation", "l'école, l'université, la formation à distance"),
    ("MKF::07_Travail", 92, "Le travail et l'économie", "l'emploi, les conflits sociaux, la banque, l'économie"),
    ("MKF::08_Medias", 93, "Les médias et la culture", "la presse, la télévision, internet, la lecture"),
    ("MKF::10_Societe", 94, "La société et la politique", "l'immigration, la justice, les élections, les relations internationales"),
    ("MKF::11_Environnement", 95, "L'environnement", "l'écologie, la pollution, le climat, l'agriculture"),
    ("MKF::Tips", 96, "Pièges et faux amis", "les faux amis, les expressions idiomatiques et les pièges de grammaire"),
]

rows = list(csv.reader(open(Path(__file__).with_name("data") / "vocab_b2.tsv", encoding="utf-8"), delimiter="\t", quoting=csv.QUOTE_NONE))
b = Book("vocabulaire")

for tag, n, title, covers in THEMES:
    words = [(front, back) for front, back, t in rows if t == tag]
    tips = tag == "MKF::Tips"
    ch = b.chapter(n, title, focus=[
        P(f"{len(words)} {'pièges' if tips else 'mots'} sur {covers}. Ces thèmes reviennent dans les documents et les sujets du DELF B2."),
        P("Révisez-les dans **Cartes** : le français s'affiche, dites le sens à voix haute, puis évaluez-vous honnêtement."),
    ], los={"a": f"Comprendre et employer le vocabulaire : {title.lower()}." if not tips else "Éviter les faux amis et les pièges courants."})
    ch.module(1, f"{title} : liste {'des pièges' if tips else 'de mots'}", sections=[
        ("a", [TABLE(["Français", "Sens" if not tips else "Explication"], *words),
               NOTE("Notez le **genre** avec chaque nom (_la grève_, _le chômage_) : une faute de genre se voit dans chaque phrase.")]),
    ], chain=[
        ("assumption", f"Le vocabulaire du thème « {title.lower()} » sert à comprendre les documents et à argumenter sans répétition."),
        ("mechanism", "Les cartes utilisent la répétition espacée : un mot revient juste avant que vous l'oubliiez."),
        ("result", "Réviser chaque jour quelques minutes vaut mieux qu'une longue séance par semaine."),
    ], why=f"Un lexique précis sur {covers} fait partie de la note « étendue et maîtrise du vocabulaire » à l'écrit et à l'oral.",
      look=["le genre du nom (le / la)", "la préposition qui accompagne le verbe"],
      traps=["les faux amis (_la librairie_ ≠ library)", "oublier l'article en apprenant un nom"],
      distractors=["un mot proche de l'anglais mais de sens différent"],
      cards=[dict(slug=f"w{k:03d}", los=["a"], name=front, front=front, back=back, examples=[], mistake=None)
             for k, (front, back) in enumerate(words, 1)])

b.write()
