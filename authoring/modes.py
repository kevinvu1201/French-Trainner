from fr import NOTE, P, Q, R, S, TABLE, UL, Book

b = Book("modes")
REF = "Repère : _Grammaire progressive du français_, chapitre {} (p. {})."

# ================================================================ chapitre 30
c = b.chapter(30, "L'impératif", focus=[
    P("L'impératif sert à donner un ordre, un conseil ou une consigne. On le rencontre dans les modes d'emploi, les affiches et les slogans "
      "(compréhension écrite) et on l'utilise pour conseiller (production orale)."),
    P(REF.format(30, 134)),
], los={
    "a": "Former l'impératif (trois personnes, verbes en _-er_ sans _s_, irréguliers).",
    "b": "Placer les pronoms à l'impératif affirmatif et négatif.",
})
c.module(1, "Utilisation, formation et place des pronoms", sections=[
    ("a", [
        P("Trois personnes, sans sujet : **tu, nous, vous** : _Parle ! Parlons ! Parlez !_ Les verbes en _-er_ (et _aller_) perdent le **s** à la 2e personne : _**Mange** ! **Va** !_ "
          "Mais on le garde devant _en_ et _y_ : _Manges-**en** ! Vas-**y** !_"),
        TABLE(["Verbe", "tu", "nous", "vous"], ["être", "**sois**", "**soyons**", "**soyez**"], ["avoir", "**aie**", "**ayons**", "**ayez**"],
              ["savoir", "**sache**", "**sachons**", "**sachez**"], ["vouloir", "**veuille**", "—", "**veuillez**"]),
        NOTE("_**Veuillez** agréer, Madame, Monsieur, …_ : l'impératif de _vouloir_ sert à la politesse dans les lettres formelles."),
    ]),
    ("b", [
        UL("**Affirmatif** : pronoms **après** le verbe, avec trait d'union ; _me / te_ deviennent **moi / toi** : _Regarde-**moi**. Lève-**toi**. Parle-**lui**._",
           "Ordre à l'affirmatif : COD avant COI : _Envoie-**la-leur**. Rends-**le-moi**._",
           "**Négatif** : pronoms **devant** le verbe, ordre normal : _Ne **me** regarde pas. Ne **te** lève pas. Ne **me le** donne pas._"),
    ]),
], chain=[
    ("assumption", "L'impératif n'a pas de sujet exprimé et seulement trois personnes."),
    ("mechanism", "Formes du présent (sans _s_ final pour _-er_ à _tu_) ; _être, avoir, savoir, vouloir_ prennent les formes du subjonctif."),
    ("result", "À l'affirmatif, les pronoms suivent le verbe (_moi, toi_) ; au négatif, ils le précèdent."),
], why="Consignes et conseils à l'impératif sont omniprésents dans les documents authentiques (affiches, notices, articles pratiques).",
  look=["la personne (tu / nous / vous)", "un verbe en _-er_ à la 2e personne", "affirmatif ou négatif ?"],
  traps=["*_manges !_", "*_sois patiente_ / _soit patiente_ (orthographe)", "*_donne-moi-le_"],
  distractors=["la forme du présent avec _s_", "le pronom mal placé"],
  questions=[
    Q("a", 1, "form", "___ tes légumes, s'il te plaît !", ("Mange", "Verbe en _-er_ : pas de _s_ à l'impératif (tu)."), [("Manges", "À l'impératif, _-er_ perd le _s_ à la 2e personne."), ("Mangez", "On s'adresse à _tu_ (_tes légumes_).")]),
    Q("a", 1, "form", "___ patients, les résultats arrivent bientôt.", ("Soyez", "Impératif d'_être_ (vous)."), [("Êtes", "C'est l'indicatif présent."), ("Soyiez", "Pas de _i_ après le _y_.")]),
    Q("a", 2, "form", "N'___ pas peur, ce chien est très gentil.", ("aie", "Impératif d'_avoir_ (tu)."), [("as", "C'est l'indicatif présent."), ("ais", "Cette forme n'existe pas.")]),
    Q("a", 2, "form", "Tu veux du gâteau ? ___-en un morceau !", ("Prends", "_prendre_ (tu) : _prends_."), [("Prend", "Seuls les verbes en _-er_ perdent le _s_."), ("Prenez", "On s'adresse à _tu_.")]),
    Q("a", 2, "form", "Le métro ? ___-y à pied, c'est à cinq minutes.", ("Vas", "Devant _y_, _va_ reprend un _s_."), [("Va", "Devant _y_, on écrit _vas-y_."), ("Vat", "On écrit _vas-y_ : le _s_ revient, pas un _t_.")]),
    Q("b", 1, "form", "Tu as fini le livre ? ___ !", ("Prête-le-moi", "Affirmatif : verbe + COD + _moi_."), [("Prête-moi-le", "Ordre à l'affirmatif : COD avant COI."), ("Me le prête", "À l'affirmatif, les pronoms suivent le verbe.")]),
    Q("b", 2, "form", "Ne ___ pas, il est tôt.", ("te lève", "Négatif : pronom devant le verbe."), [("lève-toi", "Au négatif, le pronom précède le verbe."), ("toi lève", "Au négatif, _te_ précède le verbe.")]),
    Q("b", 2, "form", "Ta grand-mère t'a écrit ? ___ vite !", ("Réponds-lui", "_répondre à qqn_ → _lui_, après le verbe à l'affirmatif."), [("Réponds-la", "_répondre_ se construit avec _à_ : _lui_."), ("Lui réponds", "À l'affirmatif, le pronom suit le verbe.")]),
  ],
  cards=[R("imperatif-s", "a", "Impératif des verbes en -er", "Tu : manger / aller ?", "**Mange ! Va !** (sans _s_) ; mais **Manges-en ! Vas-y !**"),
         R("imperatif-pronoms", "b", "Pronoms à l'impératif", "Donne + le + moi ? / négatif ?", "**Donne-le-moi** ; **Ne me le donne pas**.")])

# ================================================================ chapitre 36
c = b.chapter(36, "Le gérondif et le participe présent", focus=[
    P("Le gérondif (_en_ + participe présent) exprime la simultanéité, la manière, le moyen ou la condition. C'est un outil élégant pour condenser deux actions "
      "dans une phrase : _**En réduisant** nos déplacements, nous protégeons la planète._"),
    P(REF.format(36, 158)),
], los={
    "a": "Former le participe présent et le gérondif ; l'employer pour la simultanéité, la manière, le moyen et la condition.",
    "b": "Distinguer le gérondif, le participe présent et l'adjectif verbal.",
})
c.module(1, "Utilisation et formation du gérondif", sections=[
    ("a", [
        P("**Formation** : radical de **nous** au présent + **-ant** : _nous **pren**ons → **en pren**ant_. Trois exceptions : _être → **étant**, avoir → **ayant**, savoir → **sachant**_."),
        UL("**Simultanéité** : _Il chante **en prenant** sa douche._", "**Manière / moyen** : _Elle a appris l'anglais **en regardant** des séries._",
           "**Condition** : _**En partant** maintenant, vous arriverez à l'heure._ (= si vous partez)", "**Opposition** (avec _tout_) : _**Tout en** étant malade, il est venu._"),
        NOTE("Le sujet du gérondif est toujours celui du verbe principal : _J'ai vu Paul **en sortant**_ = c'est moi qui sortais."),
    ]),
    ("b", [
        UL("**Gérondif** (_en_ + _-ant_), invariable, lié au sujet : _Il travaille **en écoutant** de la musique._",
           "**Participe présent** (sans _en_), invariable, souvent équivalent d'une relative ou d'une cause (écrit) : _Les étudiants **ayant** réussi recevront un diplôme. **Étant** malade, il est resté chez lui._",
           "**Adjectif verbal**, qui s'accorde, parfois avec une orthographe différente : _une histoire **passionnante** ; des employés **négligents** (participe : négligeant), **fatigants** (participe : fatiguant)_."),
    ]),
], chain=[
    ("assumption", "Le gérondif relie une seconde action au sujet de la phrase principale."),
    ("mechanism", "_en_ + radical de _nous_ + _-ant_ ; il exprime simultanéité, manière, moyen ou condition."),
    ("result", "Sans _en_, le participe présent appartient à l'écrit ; l'adjectif verbal, lui, s'accorde."),
], why="Le gérondif et le participe présent condensent le style : valorisés dans l'essai et la lettre formelle.",
  look=["le sujet des deux actions (le même ?)", "_en_ présent ou non", "un accord (adjectif) ?"],
  traps=["*_en faisant_ avec un autre sujet", "*_en sachant_ / _savant_", "_fatiguant_ / _fatigant_"],
  distractors=["un participe mal formé", "l'infinitif après _en_"],
  questions=[
    Q("a", 1, "form", "Ne téléphone pas ___ !", ("en conduisant", "Simultanéité → gérondif (_nous conduisons_ → _conduisant_)."), [("en conduire", "_en_ est suivi du participe présent."), ("en conduisent", "Il faut la forme en _-ant_.")]),
    Q("a", 2, "form", "C'est ___ qu'on devient forgeron.", ("en forgeant", "Moyen → gérondif (_forger_ → _forgeant_, avec _e_)."), [("en forgant", "Il faut un _e_ pour garder le son [ʒ]."), ("à forger", "Le proverbe emploie le gérondif.")]),
    Q("a", 2, "conceptual", "___, vous économiserez 20 % (si vous réservez en ligne).", ("En réservant en ligne", "Condition → gérondif."), [("Réservant en ligne", "Sans _en_, le sens de condition se perd."), ("En réserver en ligne", "_en_ est suivi du participe présent.")]),
    Q("a", 2, "form", "___ la réponse, elle aurait pu nous aider.", ("Sachant", "_savoir_ → _sachant_ (exception)."), [("Savant", "_savant_ est un adjectif ou un nom."), ("Savoirant", "Cette forme n'existe pas.")]),
    Q("b", 2, "form", "Les candidats ___ le niveau B2 pourront s'inscrire.", ("ayant", "Participe présent (= qui ont)."), [("ayants", "Le participe présent est invariable."), ("en ayant", "Le gérondif se rapporte au sujet du verbe principal, pas au nom.")]),
    Q("b", 3, "form", "Les résultats ___ de l'étude ont surpris les chercheurs.", ("convaincants", "Adjectif verbal, accordé : _convaincant(s)_."),
      [("convainquants", "_convainquant_ est le participe présent ; l'adjectif s'écrit _convaincant_."), ("convaincant", "L'adjectif s'accorde avec _résultats_.")]),
    Q("b", 3, "form", "Ce trajet quotidien est vraiment ___.", ("fatigant", "Adjectif verbal : _fatigant_ (sans _u_)."), [("fatiguant", "_fatiguant_ est le participe présent ; l'adjectif s'écrit _fatigant_."), ("en fatiguant", "Il faut un adjectif après _être_.")]),
  ],
  cards=[R("gerondif", "a", "Le gérondif", "Formation et sens ?", "**en** + radical de _nous_ + **-ant** (étant, ayant, sachant) : simultanéité, manière, moyen, condition. Même sujet que le verbe principal.")])

# ================================================================ chapitre 42
c = b.chapter(42, "Le passif", focus=[
    P("Le passif met en avant le **résultat** ou la **victime** d'une action, et permet de ne pas nommer l'agent. "
      "Il est très fréquent dans la presse et les textes informatifs du DELF : _Une loi **a été adoptée**. Trois personnes **ont été blessées**._"),
    P(REF.format(42, 204)),
], los={
    "a": "Former le passif à tous les temps (être + participe passé accordé).",
    "b": "Introduire l'agent (_par / de_) et choisir entre passif, _on_ et forme pronominale.",
})
c.module(1, "Utilisation et formation du passif", sections=[
    ("a", [
        P("**Formation** : **être** au temps du verbe actif + **participe passé** accordé avec le sujet."),
        TABLE(["Actif", "Passif"],
              ["Le maire **inaugure** le pont.", "Le pont **est inauguré** par le maire."],
              ["Le maire **a inauguré** le pont.", "Le pont **a été inauguré** par le maire."],
              ["Le maire **inaugurait** le pont.", "Le pont **était inauguré** par le maire."],
              ["Le maire **inaugurera** le pont.", "Le pont **sera inauguré** par le maire."],
              ["Le maire **va inaugurer** le pont.", "Le pont **va être inauguré** par le maire."]),
        NOTE("Seuls les verbes avec un **COD** se mettent au passif. _Obéir, répondre, téléphoner_ (indirects) ne le peuvent pas."),
    ]),
    ("b", [
        UL("**par** : agent d'une action : _La décision a été prise **par** le conseil._",
           "**de** : après les verbes de sentiment ou de description : _Il est aimé **de** tous. La ville est entourée **de** montagnes._",
           "Sans agent : _Le voleur a été arrêté._ (on ne sait pas ou peu importe qui)"),
        P("Alternatives : **on** (_On a arrêté le voleur_) et la **forme pronominale** de sens passif (_Ce livre se vend bien_)."),
    ]),
], chain=[
    ("assumption", "Le passif fait du COD de la phrase active le sujet de la phrase."),
    ("mechanism", "_être_ prend le temps du verbe actif ; le participe s'accorde avec le nouveau sujet ; l'agent est introduit par _par_ (ou _de_)."),
    ("result", "On peut omettre l'agent, ou le remplacer par _on_ ou une forme pronominale."),
], why="Comprendre et produire le passif est indispensable pour les articles de presse (compréhension écrite) et l'écrit formel.",
  look=["le temps du verbe actif", "le genre et le nombre du nouveau sujet", "un agent : action (par) ou sentiment (de) ?"],
  traps=["*_la loi a été adopté_", "_a été_ / _était_ (temps)", "passif d'un verbe indirect"],
  distractors=["le participe non accordé", "_être_ au mauvais temps", "_par_ après un verbe de sentiment"],
  questions=[
    Q("a", 1, "form", "La nouvelle loi ___ hier par l'Assemblée.", ("a été adoptée", "Passé composé passif, accord avec _loi_."), [("a été adopté", "Le participe s'accorde avec le sujet _loi_."), ("est adoptée", "_hier_ demande un temps passé.")]),
    Q("a", 2, "form", "Les résultats ___ la semaine prochaine.", ("seront publiés", "Futur passif : _être_ au futur."), [("sont publiés", "_la semaine prochaine_ demande le futur."), ("auront publié", "C'est un futur antérieur actif.")]),
    Q("a", 2, "form", "Trois personnes ___ dans l'accident.", ("ont été blessées", "Passé composé passif, féminin pluriel."), [("ont été blessés", "_personnes_ est féminin."), ("ont blessé", "C'est la forme active.")]),
    Q("a", 3, "form", "Ce château ___ au XVIe siècle.", ("a été construit", "Événement passé daté → passé composé passif."), [("est construit", "Le présent ne situe pas l'action au XVIe siècle."), ("a construit", "C'est la forme active, sans sujet logique.")]),
    Q("b", 1, "form", "Cette chanteuse est admirée ___ tous.", ("de", "Verbe de sentiment → _de_."), [("par", "Avec un verbe de sentiment, on préfère _de_."), ("pour", "L'agent n'est pas introduit par _pour_.")]),
    Q("b", 2, "form", "Le suspect a été interrogé ___ la police.", ("par", "Agent d'une action → _par_."), [("de", "_de_ s'emploie avec les verbes de sentiment ou de description."), ("pour", "L'agent est introduit par _par_.")]),
    Q("b", 3, "conceptual", "Phrase équivalente à « On a annulé le concert » :", ("Le concert a été annulé.", "Passif sans agent, même temps."), [("Le concert est annulé par on.", "_on_ ne devient jamais agent."), ("Le concert a annulé.", "Le concert n'est pas l'auteur de l'action.")]),
  ],
  sets=[S("Brève d'actualité",
    "« Hier soir, un incendie **(1)** ___ (déclarer) dans un entrepôt de la zone industrielle. Les pompiers **(2)** ___ (appeler) vers 22 heures par un voisin. "
    "Le bâtiment **(3)** ___ (détruire) en grande partie. Une enquête **(4)** ___ (ouvrir) demain pour déterminer les causes. »",
    [Q("a", 2, "form", "Blanc (1) :", ("s'est déclaré", "_se déclarer_ (pronominal) : l'incendie commence."), [("a été déclaré", "Un incendie _se déclare_ : forme pronominale."), ("a déclaré", "L'incendie ne déclare rien : forme active impossible.")]),
     Q("a", 1, "form", "Blanc (2) :", ("ont été appelés", "Passé composé passif, accord avec _pompiers_."), [("ont appelé", "Les pompiers ne sont pas ceux qui appellent."), ("ont été appelé", "Accord avec le sujet pluriel.")]),
     Q("a", 1, "form", "Blanc (3) :", ("a été détruit", "Passé composé passif, accord avec _bâtiment_."), [("a détruit", "Le bâtiment subit l'action."), ("a été détruite", "_bâtiment_ est masculin.")]),
     Q("a", 2, "form", "Blanc (4) :", ("sera ouverte", "Futur passif (_demain_), accord avec _enquête_."), [("sera ouvert", "_enquête_ est féminin."), ("a été ouverte", "_demain_ demande le futur.")])])],
  cards=[R("passif", "a", "Le passif", "Formation ?", "**être** au temps du verbe actif + participe **accordé** avec le sujet (+ _par_ agent, _de_ avec les sentiments).",
           examples=["La loi a été votée. Les résultats seront publiés."])])

b.write()
