from fr import NOTE, P, Q, R, S, TABLE, UL, Book

b = Book("futur")
REF = "Repère : _Grammaire progressive du français_, chapitre {} (p. {})."

# ================================================================ chapitre 39
c = b.chapter(39, "Le futur proche", focus=[
    P("Le futur proche (_aller_ + infinitif) exprime un projet ou une conséquence imminente. Il est très fréquent à l'oral ; "
      "la place des pronoms et de la négation y est un point délicat."),
    P(REF.format(39, 166)),
], los={
    "a": "Former et employer le futur proche.",
    "b": "Placer les pronoms, les adverbes et la négation avec le futur proche.",
})
c.module(1, "Le futur proche : formation, pronoms et négation", sections=[
    ("a", [
        P("**Formation** : _aller_ au présent + **infinitif** : _Je **vais partir**. Il **va pleuvoir**._"),
        UL("**Projet** décidé : _L'an prochain, je **vais étudier** à Montréal._", "**Événement imminent ou certain** : _Attention, tu **vas tomber** !_"),
    ]),
    ("b", [
        UL("**Pronoms** : devant l'**infinitif** : _Je **vais le** faire. Elle **va s'**inscrire. Nous **allons en** parler._",
           "**Négation** : autour d'_aller_ : _Je **ne** vais **pas** venir. Il **ne** va **jamais** comprendre._",
           "**Adverbes** : souvent entre _aller_ et l'infinitif : _Tu vas **bien** dormir. On va **encore** attendre._"),
    ]),
], chain=[
    ("assumption", "Le futur proche présente l'avenir comme lié au présent (projet décidé, signe visible)."),
    ("mechanism", "_aller_ au présent + infinitif ; le pronom complément accompagne l'infinitif."),
    ("result", "La négation encadre _aller_, pas l'infinitif."),
], why="À l'oral du DELF, le futur proche est naturel pour présenter des projets ou des conséquences.",
  look=["le verbe dont dépend le pronom (l'infinitif)", "une négation"],
  traps=["*_je le vais faire_", "*_je vais ne pas venir_ (sens différent)", "*_nous allons se voir_"],
  distractors=["le pronom devant _aller_", "la négation autour de l'infinitif"],
  questions=[
    Q("a", 1, "form", "Regarde ces nuages : il ___ pleuvoir.", ("va", "_aller_ au présent + infinitif."), [("vas", "_vas_ va avec _tu_."), ("allait", "C'est l'imparfait.")]),
    Q("a", 1, "form", "Ce soir, nous ___ dîner chez des amis.", ("allons", "_nous allons_ + infinitif."), [("vont", "_vont_ va avec _ils_."), ("allions", "C'est l'imparfait.")]),
    Q("a", 1, "form", "Attention, le vase ___ tomber !", ("va", "Événement imminent → futur proche (_il va_)."),
      [("vas", "_vas_ va avec _tu_."), ("allait", "C'est l'imparfait.")]),
    Q("b", 2, "form", "Ce dossier ? Je ___ terminer demain.", ("vais le", "Le pronom se place devant l'infinitif."), [("le vais", "Le pronom accompagne l'infinitif, pas _aller_."), ("vais lui", "_terminer_ est direct : _le_.")]),
    Q("b", 2, "form", "Désolé, je ___ venir à la réunion.", ("ne vais pas", "La négation encadre _aller_."), [("vais ne pas", "Ici la négation doit encadrer _aller_."), ("ne vais venir pas", "_pas_ se place après _aller_.")]),
    Q("b", 2, "form", "Nous ___ voir demain matin, d'accord ?", ("allons nous", "Pronom réfléchi accordé avec _nous_, devant l'infinitif."), [("allons se", "Avec _nous_, le pronom est _nous_."), ("nous allons se", "Le pronom accompagne l'infinitif et s'accorde avec _nous_.")]),
  ],
  cards=[R("futur-proche-pronom", "b", "Pronoms au futur proche", "Je vais … faire (le) ?", "Je vais **le** faire : pronom devant l'infinitif ; négation autour d'_aller_ : _je ne vais pas le faire_.")])

# ================================================================ chapitre 47
c = b.chapter(47, "Le futur simple", focus=[
    P("Le futur simple exprime des **prévisions**, des **promesses** et des **conséquences** (_si tu viens, tu verras_). "
      "À l'écrit formel du DELF (lettre, article), il est préféré au futur proche."),
    P(REF.format(47, 224)),
], los={
    "a": "Former le futur simple (radical de l'infinitif et radicaux irréguliers).",
    "b": "Employer le futur simple et le distinguer du futur proche ; employer le futur après _quand_.",
})
c.module(1, "Formation du futur simple", sections=[
    ("a", [
        P("**Formation** : infinitif + **-ai, -as, -a, -ons, -ez, -ont** : _parler → je parler**ai**, finir → nous finir**ons**_. Verbes en _-re_ : on supprime le _e_ : _prendre → je prendr**ai**_."),
        TABLE(["Infinitif", "Futur", "Infinitif", "Futur"],
              ["être", "je **ser**ai", "avoir", "j'**aur**ai"], ["aller", "j'**ir**ai", "faire", "je **fer**ai"],
              ["venir", "je **viendr**ai", "voir", "je **verr**ai"], ["pouvoir", "je **pourr**ai", "vouloir", "je **voudr**ai"],
              ["devoir", "je **devr**ai", "savoir", "je **saur**ai"], ["envoyer", "j'**enverr**ai", "falloir", "il **faudr**a"],
              ["courir, mourir", "je **courr**ai, il **mourr**a", "recevoir", "je **recevr**ai"]),
        NOTE("Verbes en _-er_ à changement : _j'achèterai, j'appellerai, je paierai, je jetterai_ (le radical du présent de _je_ + _-r-_)."),
    ]),
], chain=[
    ("assumption", "Le futur simple se forme sur l'infinitif."),
    ("mechanism", "Infinitif (sans le _e_ final) + _-ai, -as, -a, -ons, -ez, -ont_ ; une quinzaine de verbes ont un radical irrégulier en _-r-_."),
    ("result", "Ces mêmes radicaux servent au conditionnel présent."),
], why="Les radicaux irréguliers du futur servent aussi au conditionnel : les maîtriser sécurise deux temps à la fois.",
  look=["l'infinitif et sa terminaison", "un radical irrégulier (être, avoir, aller, faire, voir…)"],
  traps=["*_je voirai_", "*_j'envoierai_", "*_je prendrerai_"],
  distractors=["un futur régularisé", "le conditionnel (_-ais_)"],
  questions=[
    Q("a", 1, "form", "Demain, nous ___ au musée d'Orsay.", ("irons", "_aller_ → _ir-_."), [("allerons", "_aller_ a un radical irrégulier : _ir-_."), ("irions", "C'est le conditionnel.")]),
    Q("a", 1, "form", "Je ___ chez toi vers 19 heures.", ("serai", "_être_ → _ser-_."), [("serais", "C'est le conditionnel."), ("étrai", "Le radical du futur d'_être_ est _ser-_.")]),
    Q("a", 2, "form", "Vous ___ les résultats par courriel.", ("recevrez", "_recevoir_ → _recevr-_."), [("recevoirez", "Le _oi_ de l'infinitif disparaît : _recevr-_."), ("recevriez", "C'est le conditionnel.")]),
    Q("a", 2, "form", "Quand tu ___ grand, tu comprendras.", ("seras", "_être_ au futur après _quand_."), [("es", "Après _quand_ à valeur future, on emploie le futur."), ("serais", "C'est le conditionnel.")]),
    Q("a", 2, "form", "On ___ bien si le projet est accepté.", ("verra", "_voir_ → _verr-_."), [("voira", "Le radical de _voir_ au futur est _verr-_."), ("verrait", "C'est le conditionnel.")]),
    Q("a", 3, "form", "Je vous ___ le dossier complet avant vendredi.", ("enverrai", "_envoyer_ → _enverr-_."), [("envoierai", "Le radical d'_envoyer_ au futur est _enverr-_."), ("envoyerai", "Le radical d'_envoyer_ au futur est _enverr-_.")]),
    Q("a", 3, "form", "Il ___ faire des efforts pour atteindre les objectifs.", ("faudra", "_falloir_ → _faudr-_."), [("fallera", "Le radical de _falloir_ est _faudr-_."), ("fera", "_fera_ vient de _faire_.")]),
  ],
  cards=[R("futur-irreg", "a", "Radicaux irréguliers du futur", "être, avoir, aller, faire, venir, voir, pouvoir, savoir, envoyer ?", "ser-, aur-, ir-, fer-, viendr-, verr-, pourr-, saur-, enverr- (+ -ai, -as, -a…).")])
c.module(2, "Futur simple ou futur proche ?", sections=[
    ("b", [
        TABLE(["Futur proche", "Futur simple"],
              ["projet décidé, lié au présent : _Je **vais déménager** (j'ai signé le bail)._", "prévision, promesse, avenir plus lointain : _Un jour, je **vivrai** à la mer._"],
              ["oral, registre courant", "écrit, registre soutenu (lettres, articles, programmes)"]),
        P("**Après _quand, lorsque, dès que, aussitôt que_** à sens futur, on emploie le **futur** (pas le présent comme en anglais) : _**Quand** tu **arriveras**, appelle-moi._"),
        P("**Si + présent → futur** : _**Si** tu **viens**, nous **irons** au concert._ (jamais de futur après _si_ conditionnel)."),
    ]),
], chain=[
    ("assumption", "Les deux futurs parlent de l'avenir, avec des nuances de lien au présent et de registre."),
    ("mechanism", "Futur proche : projet ou conséquence imminente (oral) ; futur simple : prévision, promesse (écrit)."),
    ("result", "Après _quand_ à sens futur → futur ; après _si_ → présent."),
], why="Le futur après _quand_ et le présent après _si_ sont deux points de grammaire typiquement testés.",
  look=["_quand, dès que_ ou _si_ avant le verbe", "le registre (oral / écrit)"],
  traps=["*_quand tu arrives demain_ (calque de l'anglais)", "*_si tu viendras_"],
  distractors=["le présent après _quand_ futur", "le futur après _si_"],
  questions=[
    Q("b", 1, "form", "Quand vous ___ à Paris, venez nous voir.", ("viendrez", "_quand_ + sens futur → futur."), [("venez", "Après _quand_ à sens futur, on emploie le futur."), ("viendriez", "C'est le conditionnel.")]),
    Q("b", 2, "form", "Si tu ___ ce soir, on ira au restaurant.", ("viens", "_si_ + présent → futur dans la principale."), [("viendras", "Jamais de futur après _si_ de condition."), ("venais", "_si_ + imparfait demande un conditionnel.")]),
    Q("b", 2, "form", "Je t'appellerai dès que j'___ les résultats.", ("aurai", "_dès que_ + sens futur → futur."), [("ai", "Après _dès que_ à sens futur, on emploie le futur."), ("aurais", "C'est le conditionnel.")]),
    Q("b", 3, "conceptual", "Dans une lettre de motivation : « Je ___ ravi de vous rencontrer pour un entretien. »", ("serai", "Écrit formel, promesse → futur simple."), [("vais être", "Le futur proche est plutôt oral."), ("suis", "Le présent ne situe pas la rencontre dans l'avenir.")]),
  ],
  cards=[R("quand-futur", "b", "Quand + futur, si + présent", "Quand tu ___ (arriver) / Si tu ___ (venir) ?", "Quand tu **arriveras** (futur) ; si tu **viens** (présent).")])

# ================================================================ chapitre 48
c = b.chapter(48, "Le futur antérieur", focus=[
    P("Le futur antérieur présente une action **accomplie avant** une autre action future, ou une **supposition** sur le passé. "
      "C'est un temps typique de l'écrit soutenu et des plans d'action : _Quand nous aurons réduit nos déchets, nous pourrons…_"),
    P(REF.format(48, 228)),
], los={
    "a": "Former et employer le futur antérieur (antériorité dans le futur, supposition).",
    "b": "Situer les temps de l'indicatif les uns par rapport aux autres.",
})
c.module(1, "Le futur antérieur et le résumé des temps de l'indicatif", sections=[
    ("a", [
        P("**Formation** : _avoir_ ou _être_ au **futur** + participe passé : _j'**aurai fini**, elle **sera partie**, nous nous **serons inscrits**_."),
        UL("**Antériorité dans le futur** (souvent après _quand, dès que, après que, une fois que_) : _**Quand** tu **auras lu** ce livre, tu me le prêteras._",
           "**Action accomplie à un moment futur** : _**D'ici** 2030, nous **aurons divisé** nos émissions par deux._",
           "**Supposition** sur un fait passé : _Il n'est pas là ? Il **aura oublié** le rendez-vous._ (= il a probablement oublié)"),
    ]),
    ("b", [
        TABLE(["Passé", "Présent", "Futur"],
              ["plus-que-parfait : _il avait fini_ (avant un moment passé)", "présent : _il finit_", "futur antérieur : _il aura fini_ (avant un moment futur)"],
              ["passé composé : _il a fini_", "", "futur simple : _il finira_"],
              ["imparfait : _il finissait_", "", "futur proche : _il va finir_"]),
    ]),
], chain=[
    ("assumption", "Comme le plus-que-parfait pour le passé, le futur antérieur marque l'antériorité dans le futur."),
    ("mechanism", "Auxiliaire au futur + participe passé, avec les règles d'accord habituelles."),
    ("result", "Il s'emploie après _quand / dès que_ pour l'action accomplie d'abord, et pour une supposition sur le passé."),
], why="Le futur antérieur rend un plan d'action ou une proposition (lettre au maire, article) précise et crédible.",
  look=["deux actions futures : laquelle est accomplie d'abord ?", "_d'ici_ + date"],
  traps=["*_quand tu finiras, tu sortiras_ (succession floue)", "*_il aura parti_"],
  distractors=["le futur simple pour l'action accomplie", "l'auxiliaire _avoir_ avec un verbe de mouvement"],
  questions=[
    Q("a", 1, "form", "Quand tu ___ tes devoirs, tu pourras regarder la télé.", ("auras fini", "Action accomplie avant une autre action future."), [("finiras", "La télé vient après la fin des devoirs : futur antérieur."), ("as fini", "Le contexte est futur.")]),
    Q("a", 2, "form", "D'ici la fin de l'année, nous ___ dix nouveaux salariés.", ("aurons recruté", "Action accomplie à un moment futur (_d'ici_)."), [("recrutons", "_d'ici la fin de l'année_ : action accomplie dans le futur."), ("aurions recruté", "C'est le conditionnel passé.")]),
    Q("a", 2, "form", "Dès que les invités ___, nous servirons le dîner.", ("seront arrivés", "Antériorité dans le futur, verbe avec _être_."), [("auront arrivé", "_arriver_ se conjugue avec _être_."), ("arrivent", "Après _dès que_ à sens futur, on emploie un futur.")]),
    Q("a", 3, "conceptual", "Elle n'est pas encore là ? Elle ___ son train.", ("aura raté", "Supposition sur un fait passé → futur antérieur."), [("ratera", "Le futur simple parle de l'avenir."), ("raterait", "Le conditionnel exprime l'hypothèse, pas la supposition probable.")]),
    Q("b", 2, "conceptual", "Quand tu liras cette lettre, je ___ déjà.", ("serai parti", "Action accomplie avant un moment futur → futur antérieur."),
      [("étais parti", "Le plus-que-parfait se situe dans le passé."), ("partirai", "Le départ précède la lecture : il est accompli.")]),
    Q("b", 3, "conceptual", "Lundi, j'ai appris que mon dossier ___ accepté la semaine précédente.", ("avait été", "Antériorité dans le passé → plus-que-parfait (passif)."),
      [("aura été", "Le futur antérieur se situe dans l'avenir."), ("sera", "Le futur ne convient pas à un fait passé.")]),
    Q("b", 2, "conceptual", "Je partirai quand j'___ mes valises.", ("aurai fait", "Les valises sont faites avant le départ : futur antérieur."), [("avais fait", "Le plus-que-parfait se situe dans le passé."), ("ai fait", "Le contexte est futur.")]),
  ],
  cards=[R("futur-anterieur", "a", "Futur antérieur", "Formation et emplois ?", "auxiliaire au **futur** + participe : _j'aurai fini_. Action accomplie avant une autre action future ; supposition (_il aura oublié_).")])

b.write()
