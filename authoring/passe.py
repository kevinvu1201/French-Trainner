from fr import NOTE, P, Q, R, S, TABLE, UL, Book

b = Book("passe")
REF = "Repère : _Grammaire progressive du français_, chapitre {} (p. {})."

# ================================================================ chapitre 40
c = b.chapter(40, "Le passé composé", focus=[
    P("Le passé composé est le temps du récit au passé à l'oral et dans la plupart des écrits. Il pose trois difficultés : le **participe passé**, "
      "le choix de l'**auxiliaire** (_avoir_ ou _être_) et l'**accord** du participe. Toutes trois sont évaluées dans chaque production."),
    P(REF.format(40, 174)),
], los={
    "a": "Former le passé composé avec _avoir_ et les participes passés réguliers et irréguliers.",
    "b": "Choisir l'auxiliaire _être_ (verbes de mouvement, pronominaux) ou _avoir_ (verbes à double emploi).",
    "c": "Accorder le participe passé (avec _être_, avec un COD placé avant, verbes pronominaux).",
    "d": "Placer la négation, les pronoms et les adverbes au passé composé.",
})
c.module(1, "Le passé composé avec « avoir » et le participe passé", sections=[
    ("a", [
        P("**Formation** : _avoir_ (ou _être_) au présent + **participe passé** : _J'**ai mangé**. Nous **avons fini**._"),
        TABLE(["Infinitif", "Participe", "Infinitif", "Participe"],
              ["-er : parler", "parl**é**", "-ir : finir, partir", "fin**i**, part**i**"],
              ["avoir", "**eu**", "être", "**été**"], ["faire", "**fait**", "dire, écrire", "**dit**, **écrit**"],
              ["prendre, mettre", "**pris**, **mis**", "voir, savoir", "**vu**, **su**"], ["pouvoir, vouloir", "**pu**, **voulu**", "devoir, boire", "**dû**, **bu**"],
              ["lire, croire", "**lu**, **cru**", "venir, tenir", "**venu**, **tenu**"], ["ouvrir, offrir", "**ouvert**, **offert**", "naître, mourir", "**né**, **mort**"],
              ["recevoir, connaître", "**reçu**, **connu**", "vivre, suivre", "**vécu**, **suivi**"]),
        NOTE("Prononciation : _je mangeais_ (imparfait) et _j'ai mangé_ (passé composé) se distinguent par l'auxiliaire. Ne confondez pas _j'ai_ [ʒe] et _je_ [ʒə] à l'oral."),
    ]),
], chain=[
    ("assumption", "Le passé composé présente une action passée comme accomplie."),
    ("mechanism", "Auxiliaire au présent + participe passé ; les verbes en _-er_ font _-é_, les autres ont des participes à apprendre (_eu, fait, pris, vu, dû…_)."),
    ("result", "Une vingtaine de participes irréguliers couvrent l'essentiel des besoins."),
], why="Les participes irréguliers fautifs (*_il a prendu_, *_j'ai vouler_) sont parmi les erreurs les plus visibles d'une copie.",
  look=["l'infinitif du verbe", "son groupe (-er, -ir, irrégulier)"],
  traps=["*_prendu_", "*_ouvri_", "*_j'ai devu_"],
  distractors=["un participe régularisé (_prendu, mettu_)", "l'infinitif ou l'imparfait"],
  questions=[
    Q("a", 1, "form", "Hier, nous ___ un film italien.", ("avons vu", "_voir_ → _vu_."), [("avons voir", "Il faut le participe passé."), ("avons voyé", "Le participe de _voir_ est _vu_.")]),
    Q("a", 1, "form", "Elle ___ le train de 7 heures.", ("a pris", "_prendre_ → _pris_."), [("a prendu", "Ce participe n'existe pas."), ("a prené", "Ce participe n'existe pas.")]),
    Q("a", 2, "form", "J'___ partir plus tôt à cause de la grève.", ("ai dû", "_devoir_ → _dû_ (avec accent)."), [("ai devu", "Le participe de _devoir_ est _dû_."), ("ai du", "Le participe masculin singulier s'écrit _dû_.")]),
    Q("a", 2, "form", "Le musée ___ ses portes à 10 heures.", ("a ouvert", "_ouvrir_ → _ouvert_."), [("a ouvri", "Le participe de _ouvrir_ est _ouvert_."), ("a ouvré", "Le participe de _ouvrir_ est _ouvert_.")]),
    Q("a", 2, "form", "Ils ___ dix ans à Montréal.", ("ont vécu", "_vivre_ → _vécu_."), [("ont vivé", "Le participe de _vivre_ est _vécu_."), ("ont vivu", "Le participe de _vivre_ est _vécu_.")]),
    Q("a", 3, "form", "Nous ___ votre courrier du 3 mars.", ("avons reçu", "_recevoir_ → _reçu_ (cédille)."), [("avons recevu", "Le participe de _recevoir_ est _reçu_."), ("avons reçus", "Pas d'accord : le COD est placé après.")]),
  ],
  cards=[R("participes", "a", "Participes passés irréguliers", "avoir, être, faire, prendre, mettre, voir, devoir, ouvrir, vivre ?", "eu, été, fait, pris, mis, vu, dû, ouvert, vécu.")])
c.module(2, "« Être » ou « avoir » ?", sections=[
    ("b", [
        P("**Avec être** : une quinzaine de verbes de **mouvement / changement d'état** et leurs dérivés : _aller, venir (devenir, revenir), arriver, partir, entrer (rentrer), sortir, "
          "monter, descendre, passer, tomber, naître, mourir, rester, retourner_."),
        P("**Avec être** aussi : **tous les verbes pronominaux** : _Je **me suis** levé. Ils **se sont** rencontrés._"),
        P("**Verbes à double emploi** : _monter, descendre, sortir, rentrer, passer, retourner_ prennent **avoir** quand ils ont un **COD** : "
          "_Elle **est** montée au 5e étage._ / _Elle **a** monté **ses valises**._ _Il **est** sorti._ / _Il **a** sorti **le chien**._ _J'**ai** passé **une semaine** à Rome._"),
    ]),
], chain=[
    ("assumption", "La grande majorité des verbes forment le passé composé avec _avoir_."),
    ("mechanism", "_Être_ s'emploie avec une quinzaine de verbes de mouvement ou de changement d'état et avec tous les pronominaux."),
    ("result", "Si l'un de ces verbes de mouvement a un COD, il reprend l'auxiliaire _avoir_."),
], why="L'auxiliaire est le premier point vérifié dans un récit au passé (production écrite et orale).",
  look=["le verbe : mouvement ? pronominal ?", "un COD après le verbe"],
  traps=["*_j'ai tombé_", "*_il a resté_", "*_elle est sortie la poubelle_"],
  distractors=["_avoir_ avec un verbe de mouvement", "_être_ avec un verbe de mouvement suivi d'un COD"],
  questions=[
    Q("b", 1, "form", "Mes amis ___ à Paris la semaine dernière.", ("sont venus", "_venir_ → _être_."), [("ont venu", "_venir_ se conjugue avec _être_."), ("sont venu", "Avec _être_, le participe s'accorde.")]),
    Q("b", 1, "form", "Je ___ dans l'escalier et je me suis fait mal.", ("suis tombé", "_tomber_ → _être_."), [("ai tombé", "_tomber_ se conjugue avec _être_."), ("me suis tombé", "_tomber_ n'est pas pronominal.")]),
    Q("b", 2, "form", "Hier soir, nous ___ à la maison.", ("sommes restés", "_rester_ → _être_."), [("avons resté", "_rester_ se conjugue avec _être_."), ("sommes resté", "Avec _être_, accord avec _nous_.")]),
    Q("b", 2, "form", "Elle ___ ses valises au troisième étage.", ("a monté", "_monter_ + COD (_ses valises_) → _avoir_."), [("est montée", "Avec un COD, _monter_ prend _avoir_."), ("a montée", "Avec _avoir_, pas d'accord avec le sujet.")]),
    Q("b", 2, "form", "Ce matin, il ___ très tôt.", ("s'est réveillé", "Verbe pronominal → _être_."), [("a réveillé", "Sans pronom, il manque le COD : _se réveiller_ est pronominal."), ("s'a réveillé", "Les pronominaux prennent _être_.")]),
    Q("b", 3, "form", "Nous ___ trois semaines merveilleuses en Grèce.", ("avons passé", "_passer_ + COD (_trois semaines_) → _avoir_."), [("sommes passés", "_passer_ + durée (COD) prend _avoir_."), ("sommes passé", "Il faut _avoir_ avec un COD.")]),
    Q("b", 3, "form", "N'oublie pas : tu ___ la poubelle hier ?", ("as sorti", "_sortir_ + COD → _avoir_."), [("es sorti", "Avec un COD (_la poubelle_), _sortir_ prend _avoir_."), ("es sortie", "Avec un COD, _sortir_ prend _avoir_.")]),
  ],
  cards=[R("etre-aux", "b", "Verbes avec être", "Quels verbes prennent être au passé composé ?", "aller, venir, arriver, partir, entrer, sortir, monter, descendre, passer, tomber, naître, mourir, rester, retourner (+ dérivés) et **tous les pronominaux**.",
           mistake="_Elle a sorti le chien_ : avec un COD, _avoir_.")])
c.module(3, "L'accord du participe passé et la place des mots", sections=[
    ("c", [
        UL("**Avec être** : accord avec le **sujet** : _Elle est part**ie**. Ils sont arriv**és**._",
           "**Avec avoir** : pas d'accord avec le sujet ; accord avec le **COD placé avant** le verbe (pronom _le, la, les_, relatif _que_, _quel(le)s_) : "
           "_J'ai acheté **des fleurs**._ / _Les fleurs **que** j'ai achet**ées**. Je **les** ai achet**ées**._",
           "**Pronominaux** : accord avec le pronom s'il est COD : _Elle s'est lav**ée**._ Pas d'accord s'il est COI : _Elles se sont **parlé**. Elle s'est lavé **les mains**._"),
        NOTE("Pas d'accord avec _en_ ni avec _lui / leur_ : _Des pommes ? J'en ai mangé. Je leur ai parlé._"),
    ]),
    ("d", [
        P("**Négation** : autour de l'auxiliaire : _Je **n'**ai **pas** compris. Il **ne** s'est **jamais** marié._"),
        P("**Pronoms** : devant l'auxiliaire : _Je **l'**ai vu. Je **lui** ai répondu. Nous **y** sommes allés._"),
        P("**Adverbes courts** : entre l'auxiliaire et le participe : _Il a **bien** dormi. J'ai **déjà** mangé._"),
        P("**Inversion** : _**As-tu** compris ? **Est-elle** partie ?_"),
    ]),
], chain=[
    ("assumption", "Le participe passé se comporte comme un adjectif avec _être_ et reste invariable avec _avoir_… sauf exception."),
    ("mechanism", "Avec _avoir_, il s'accorde avec un COD **placé avant** : _la lettre que j'ai écrit**e**_."),
    ("result", "Négation, pronoms et adverbes s'organisent autour de l'**auxiliaire**."),
], why="L'accord avec le COD antéposé est le test de grammaire le plus classique au niveau B2.",
  look=["l'auxiliaire", "un COD placé avant (le, la, les, que)", "un verbe pronominal : COD ou COI ?"],
  traps=["*_elle a partie_", "*_les photos que j'ai pris_", "*_elles se sont parlées_"],
  distractors=["l'accord avec le sujet après _avoir_", "l'absence d'accord avec un COD antéposé"],
  questions=[
    Q("c", 1, "form", "Mes sœurs sont ___ hier soir.", ("arrivées", "_être_ → accord avec le sujet (féminin pluriel)."), [("arrivé", "Avec _être_, le participe s'accorde."), ("arrivés", "_sœurs_ est féminin.")]),
    Q("c", 2, "form", "La lettre que tu m'as ___ m'a beaucoup touché.", ("écrite", "COD _que_ (= la lettre) placé avant → accord."), [("écrit", "Le COD est placé avant : accord."), ("écrits", "_lettre_ est féminin singulier.")]),
    Q("c", 2, "form", "Tes clés ? Je les ai ___ sur la table.", ("laissées", "COD _les_ (= les clés, féminin pluriel) placé avant."), [("laissé", "Le COD _les_ précède le verbe : accord."), ("laissés", "_clés_ est féminin.")]),
    Q("c", 2, "form", "Elles ont ___ toute la nuit.", ("dansé", "Avec _avoir_, pas d'accord avec le sujet."), [("dansées", "Avec _avoir_, on n'accorde pas avec le sujet."), ("dansés", "Avec _avoir_, on n'accorde pas avec le sujet.")]),
    Q("c", 3, "form", "Elles se sont ___ pendant des heures au téléphone.", ("parlé", "_parler à qqn_ : _se_ est COI → pas d'accord."), [("parlées", "_se_ est COI (_parler à_) : pas d'accord."), ("parlés", "_se_ est COI : pas d'accord.")]),
    Q("c", 3, "form", "Elle s'est ___ avant de partir.", ("maquillée", "_se_ est COD (elle maquille elle-même) → accord."), [("maquillé", "_se_ est COD : accord avec le sujet."), ("maquillés", "Le sujet est féminin singulier.")]),
    Q("c", 3, "form", "Des tomates ? J'en ai ___ au marché.", ("acheté", "Pas d'accord avec _en_."), [("achetées", "On n'accorde pas avec _en_."), ("achetés", "On n'accorde pas avec _en_.")]),
    Q("d", 2, "form", "Il est fatigué : il ___ cette nuit.", ("a mal dormi", "Adverbe court entre l'auxiliaire et le participe."),
      [("a dormi mal", "_mal_ se place entre l'auxiliaire et le participe."), ("mal a dormi", "L'adverbe ne précède pas l'auxiliaire.")]),
    Q("d", 1, "form", "Je ___ compris la question.", ("n'ai pas", "La négation encadre l'auxiliaire."), [("ai ne pas", "_ne_ se place devant l'auxiliaire."), ("n'ai compris pas", "_pas_ se place avant le participe.")]),
    Q("d", 2, "form", "Ton message ? Je ___ hier soir.", ("l'ai lu", "Pronom devant l'auxiliaire."), [("ai le lu", "Le pronom précède l'auxiliaire."), ("ai lu le", "Le pronom précède l'auxiliaire.")]),
  ],
  sets=[S("Un week-end à Lyon",
    "Clara raconte :\n\n« Samedi, nous **(1)** ___ (partir) tôt de Paris. Nous avons visité le Vieux-Lyon et j'ai acheté des cartes postales : je les ai **(2)** ___ (envoyer) à mes "
    "cousins. Le soir, mes amies **(3)** ___ (rester) à l'hôtel, mais moi, je **(4)** ___ (sortir) dans un bouchon lyonnais. »",
    [Q("b", 1, "form", "Blanc (1) :", ("sommes partis", "_partir_ → _être_, accord avec _nous_."), [("avons parti", "_partir_ se conjugue avec _être_."), ("sommes parti", "Avec _être_, accord avec _nous_ (pluriel).")]),
     Q("c", 2, "form", "Blanc (2) :", ("envoyées", "COD _les_ (= les cartes, féminin pluriel) placé avant."), [("envoyé", "Le COD précède : accord."), ("envoyés", "_cartes_ est féminin.")]),
     Q("b", 1, "form", "Blanc (3) :", ("sont restées", "_rester_ → _être_, accord féminin pluriel."), [("ont resté", "_rester_ se conjugue avec _être_."), ("sont restés", "_amies_ est féminin.")]),
     Q("b", 2, "form", "Blanc (4) :", ("suis sortie", "_sortir_ sans COD → _être_, Clara est une femme."), [("ai sorti", "Sans COD, _sortir_ prend _être_."), ("suis sorti", "Clara est une femme : accord féminin.")])])],
  cards=[R("accord-cod", "c", "Accord avec avoir", "Avec avoir, le participe s'accorde quand ?", "Avec le **COD placé avant** (_le, la, les, que_) : _la robe que j'ai achetée_. Jamais avec le sujet ni avec _en_."),
         R("accord-pronominal", "c", "Accord des pronominaux", "Elles se sont lavées / parlé ?", "_se_ COD → accord (_lavées_) ; _se_ COI → pas d'accord (_parlé_, _téléphoné_, _écrit_).")])

# ================================================================ chapitre 43
c = b.chapter(43, "L'imparfait", focus=[
    P("L'imparfait décrit le **décor** et les **habitudes** du passé ; le passé composé raconte les **événements**. Leur alternance donne du relief "
      "au récit et c'est l'un des points les plus évalués au B1–B2."),
    P(REF.format(43, 206)),
], los={
    "a": "Former l'imparfait et l'employer pour les habitudes et les descriptions passées.",
    "b": "Choisir entre imparfait et passé composé dans un récit.",
})
c.module(1, "L'imparfait d'habitude et de description", sections=[
    ("a", [
        P("**Formation** : radical de **nous** au présent + **-ais, -ais, -ait, -ions, -iez, -aient** : _nous **finiss**ons → je finiss**ais**_. Seule exception : _être → j'**ét**ais_."),
        TABLE(["Infinitif", "nous (présent)", "Imparfait"], ["parler", "nous parl-ons", "je parlais"], ["faire", "nous fais-ons", "je faisais"],
              ["prendre", "nous pren-ons", "je prenais"], ["manger", "nous mange-ons", "je mangeais (nous mangions)"], ["commencer", "nous commenç-ons", "je commençais (nous commencions)"]),
        UL("**Habitude passée** : _Quand j'étais petit, je **passais** mes vacances chez mes grands-parents._",
           "**Description** (décor, personnes, état, sentiment) : _Il **faisait** beau, la plage **était** déserte, j'**étais** heureux._",
           "**Proposition** (avec _si_) : _**Si on allait** au cinéma ?_"),
        NOTE("_Nous étudi**i**ons, vous étudi**i**ez_ : deux _i_ quand le radical se termine par _i_."),
    ]),
], chain=[
    ("assumption", "L'imparfait présente une action passée **sans début ni fin** visibles."),
    ("mechanism", "Radical de _nous_ au présent + _-ais, -ait, -ions, -iez, -aient_ ; seule exception : _être → ét-_."),
    ("result", "On l'emploie pour les habitudes, les descriptions et les états du passé."),
], why="Chaque récit (lettre, témoignage, expérience personnelle) mobilise l'imparfait : formes et emplois sont évalués.",
  look=["habitude, description ou événement ?", "la forme de _nous_ au présent"],
  traps=["*_j'étudais_", "*_nous mangions_ / _nous mangeons_ confusion", "*_j'avais_ pour _j'étais_"],
  distractors=["le passé composé pour une habitude", "un radical fautif"],
  questions=[
    Q("a", 1, "form", "Quand j'étais enfant, je ___ au foot tous les mercredis.", ("jouais", "Habitude passée → imparfait."), [("ai joué", "Une habitude répétée s'exprime à l'imparfait."), ("jouerais", "C'est le conditionnel.")]),
    Q("a", 1, "form", "Ce jour-là, il ___ très froid.", ("faisait", "Description (météo) → imparfait de _faire_."), [("fesait", "L'orthographe est _faisait_."), ("a fait", "La météo sert de décor : imparfait.")]),
    Q("a", 2, "form", "Avant, nous ___ en banlieue.", ("habitions", "_nous_ + _-ions_."), [("habitons", "C'est le présent."), ("habitiions", "Un seul _i_ : le radical est _habit-_.")]),
    Q("a", 2, "form", "À l'université, vous ___ le droit ?", ("étudiiez", "Radical _étudi-_ + _-iez_ : deux _i_."), [("étudiez", "C'est le présent."), ("étudiaiez", "La terminaison est _-iez_.")]),
    Q("a", 2, "form", "Mes grands-parents ___ une petite ferme en Auvergne.", ("avaient", "Description d'une situation passée → imparfait."), [("avait", "Le sujet est pluriel."), ("ont eu", "La situation durable s'exprime à l'imparfait.")]),
  ],
  cards=[R("imparfait", "a", "Formation de l'imparfait", "Imparfait = ?", "radical de **nous** au présent + **-ais, -ais, -ait, -ions, -iez, -aient** ; exception : _être → j'étais_.")])
c.module(2, "L'imparfait et le passé composé", sections=[
    ("b", [
        TABLE(["Imparfait", "Passé composé"],
              ["décor, circonstances, état : _Il pleuvait._", "événement, action ponctuelle : _Le téléphone a sonné._"],
              ["action en cours (interrompue) : _Je dormais quand…_", "action qui interrompt : _… quand le téléphone a sonné._"],
              ["habitude : _Je partais tous les étés._", "action unique ou délimitée : _Je suis parti trois fois. J'ai vécu dix ans à Rome._"]),
        P("Indices : _tous les jours, souvent, d'habitude, autrefois, à cette époque_ → imparfait ; _un jour, soudain, tout à coup, ce jour-là, pendant trois ans_ → passé composé."),
        NOTE("_Pendant + durée_ délimitée appelle le passé composé, même pour une action longue : _J'**ai habité** à Lyon pendant dix ans._"),
    ]),
], chain=[
    ("assumption", "Un récit superpose un arrière-plan (le décor) et un premier plan (les événements)."),
    ("mechanism", "L'imparfait peint l'arrière-plan et les habitudes ; le passé composé fait avancer l'action."),
    ("result", "Une action délimitée (_pendant dix ans_, _trois fois_) se met au passé composé, même si elle est longue."),
], why="Le bon dosage imparfait / passé composé rend un récit clair et est explicitement noté au DELF.",
  look=["décor ou événement ?", "les indicateurs de temps (soudain, tous les jours, pendant…)"],
  traps=["*_j'étais à Lyon pendant dix ans_ (durée délimitée)", "*_soudain, le téléphone sonnait_"],
  distractors=["l'imparfait pour l'événement", "le passé composé pour le décor"],
  questions=[
    Q("b", 1, "conceptual", "Je ___ quand tu m'as appelé.", ("dormais", "Action en cours interrompue → imparfait."), [("ai dormi", "L'action en cours est à l'imparfait."), ("dormirai", "C'est le futur.")]),
    Q("b", 1, "conceptual", "Nous marchions dans la forêt quand soudain un cerf ___.", ("est apparu", "Événement soudain → passé composé."), [("apparaissait", "_soudain_ introduit un événement ponctuel."), ("apparaît", "Le récit est au passé.")]),
    Q("b", 2, "conceptual", "Elle ___ à Berlin pendant cinq ans, puis elle est rentrée en France.", ("a travaillé", "Durée délimitée → passé composé."), [("travaillait", "_pendant cinq ans_ délimite l'action : passé composé."), ("travaille", "Le récit est au passé.")]),
    Q("b", 2, "conceptual", "Quand j'étais étudiant, je ___ toujours le même bus.", ("prenais", "Habitude → imparfait."), [("ai pris", "_toujours_ + habitude : imparfait."), ("prendrais", "C'est le conditionnel.")]),
    Q("b", 2, "conceptual", "Il ___ beau, alors nous avons décidé de pique-niquer.", ("faisait", "Circonstance (météo) → imparfait."), [("a fait", "La météo est le décor de la décision."), ("fera", "C'est le futur.")]),
    Q("b", 3, "conceptual", "Ce matin-là, j'___ trois fois mon réveil avant de me lever.", ("ai éteint", "Action répétée mais comptée (_trois fois_) → passé composé."), [("éteignais", "Une répétition comptée et délimitée se met au passé composé."), ("éteins", "Le récit est au passé.")]),
  ],
  sets=[S("Un souvenir d'enfance",
    "Marc raconte :\n\n« Quand j'**(1)** ___ (avoir) dix ans, nous passions l'été à la campagne. Chaque matin, mon grand-père m'**(2)** ___ (emmener) pêcher. "
    "Un jour, pendant que nous attendions au bord de la rivière, il **(3)** ___ (tomber) dans l'eau ! Nous **(4)** ___ (rire) pendant des heures. »",
    [Q("a", 1, "form", "Blanc (1) :", ("avais", "Âge, situation passée → imparfait."), [("ai eu", "L'âge comme cadre du souvenir s'exprime à l'imparfait."), ("étais", "L'âge se dit avec _avoir_.")]),
     Q("b", 1, "conceptual", "Blanc (2) :", ("emmenait", "_Chaque matin_ : habitude → imparfait."), [("a emmené", "Une habitude répétée → imparfait."), ("emmène", "Le récit est au passé.")]),
     Q("b", 2, "conceptual", "Blanc (3) :", ("est tombé", "_Un jour_ : événement ponctuel → passé composé avec _être_."), [("tombait", "_Un jour_ introduit un événement."), ("a tombé", "_tomber_ se conjugue avec _être_.")]),
     Q("b", 2, "conceptual", "Blanc (4) :", ("avons ri", "Durée délimitée (_pendant des heures_) → passé composé."), [("riions", "La durée délimitée appelle le passé composé."), ("avons rit", "Le participe de _rire_ est _ri_.")])])],
  cards=[R("imp-pc", "b", "Imparfait ou passé composé ?", "décor / événement ; habitude / action comptée ?", "**Imparfait** : décor, état, habitude, action en cours. **Passé composé** : événement, action délimitée (_pendant 3 ans, 3 fois_).")])

# ================================================================ chapitre 44
c = b.chapter(44, "Le plus-que-parfait", focus=[
    P("Le plus-que-parfait exprime une action **antérieure** à une autre action passée. Il est indispensable pour le discours rapporté, "
      "les hypothèses (_si j'avais su_) et les regrets."),
    P(REF.format(44, 214)),
], los={
    "a": "Former le plus-que-parfait et l'employer pour l'antériorité dans le passé.",
    "b": "Situer les temps du passé les uns par rapport aux autres (passé composé, imparfait, plus-que-parfait).",
})
c.module(1, "Le plus-que-parfait et le résumé des temps du passé", sections=[
    ("a", [
        P("**Formation** : _avoir_ ou _être_ à l'**imparfait** + participe passé : _j'**avais** fini, elle **était** partie, nous nous **étions** rencontrés_. Mêmes règles d'auxiliaire et d'accord qu'au passé composé."),
        UL("**Antériorité** : _Quand je suis arrivé, le film **avait** déjà **commencé**._",
           "**Regret** : _Si seulement j'**avais su** !_",
           "**Discours rapporté au passé** : _Il m'a dit qu'il **avait perdu** ses clés._"),
    ]),
    ("b", [
        TABLE(["Avant le moment passé", "Moment passé de référence", "Cadre"],
              ["**plus-que-parfait** : _il avait plu_", "**passé composé** : _je suis sorti_", "**imparfait** : _il faisait froid_"]),
        NOTE("_Déjà_ et _ne … pas encore_ accompagnent souvent le plus-que-parfait : _Il n'**avait pas encore** fini quand nous sommes arrivés._"),
    ]),
], chain=[
    ("assumption", "Dans un récit, certaines actions se sont produites **avant** le moment raconté."),
    ("mechanism", "On forme le plus-que-parfait avec l'auxiliaire à l'imparfait + participe passé."),
    ("result", "Il marque l'antériorité, le regret (_si seulement…_) et la concordance au discours indirect."),
], why="Le plus-que-parfait conditionne la réussite des hypothèses irréelles (_si j'avais…, j'aurais…_) et du discours rapporté.",
  look=["une action antérieure à une autre action passée", "l'auxiliaire (avoir / être)"],
  traps=["*_quand je suis arrivé, il est déjà parti_", "*_il avait parti_"],
  distractors=["le passé composé à la place du plus-que-parfait", "l'auxiliaire _avoir_ avec un verbe de mouvement"],
  questions=[
    Q("a", 1, "form", "Quand nous sommes arrivés à la gare, le train ___.", ("était déjà parti", "Action antérieure → plus-que-parfait avec _être_."), [("est déjà parti", "Le départ précède l'arrivée : plus-que-parfait."), ("avait déjà parti", "_partir_ se conjugue avec _être_.")]),
    Q("a", 2, "form", "Elle a réussi l'examen parce qu'elle ___ toute l'année.", ("avait travaillé", "Cause antérieure → plus-que-parfait."), [("a travaillé", "Le travail précède la réussite : antériorité."), ("travaillerait", "C'est le conditionnel.")]),
    Q("a", 2, "form", "Il m'a raconté qu'il ___ son passeport à l'aéroport.", ("avait perdu", "Discours rapporté au passé : antériorité → plus-que-parfait."), [("a perdu", "Après _il m'a raconté que_, le passé composé devient plus-que-parfait."), ("perdait", "L'imparfait décrirait une action en cours.")]),
    Q("a", 3, "form", "Si seulement je ___ ton conseil !", ("avais écouté", "Regret → _si seulement_ + plus-que-parfait."), [("ai écouté", "Le regret s'exprime au plus-que-parfait."), ("écouterais", "Pas de conditionnel après _si_.")]),
    Q("b", 2, "conceptual", "Le matin de l'examen, j'étais épuisé : la veille, je n'___ pas dormi.", ("avais", "Action antérieure à un moment passé → plus-que-parfait."),
      [("ai", "_la veille_ d'un moment passé : il faut le plus-que-parfait."), ("aurais", "Le conditionnel passé exprime un fait irréel.")]),
    Q("b", 2, "conceptual", "Ce matin, j'ai enfin retrouvé le portefeuille que j'___ la veille.", ("avais perdu", "Perte antérieure au moment raconté → plus-que-parfait."),
      [("ai perdu", "_la veille_ d'un moment passé : plus-que-parfait."), ("perdrai", "Le futur ne convient pas.")]),
    Q("b", 3, "conceptual", "Les invités ___ quand le gâteau est enfin arrivé.", ("étaient déjà partis", "Action antérieure et accomplie → plus-que-parfait."), [("partaient déjà", "L'imparfait montrerait le départ en cours."), ("sont déjà partis", "L'antériorité demande le plus-que-parfait.")]),
  ],
  cards=[R("pqp", "a", "Plus-que-parfait", "Formation et emploi ?", "auxiliaire à l'**imparfait** + participe : _j'avais fini, elle était partie_ ; action **antérieure** à une autre action passée.")])

# ================================================================ chapitre 46
c = b.chapter(46, "« Venir de », « être en train de », « être sur le point de »", focus=[
    P("Ces trois périphrases situent une action par rapport au moment présent (ou passé) : juste avant, pendant, juste après. "
      "Elles sont très fréquentes à l'oral et dans les informations."),
    P(REF.format(46, 222)),
], los={"a": "Exprimer le passé récent, le présent progressif et le futur immédiat (venir de, être en train de, être sur le point de)."})
c.module(1, "Passé récent, action en cours, futur immédiat", sections=[
    ("a", [
        TABLE(["Périphrase", "Sens", "Exemple"],
              ["**venir de** + infinitif", "passé récent", "_Le train **vient de** partir._"],
              ["**être en train de** + infinitif", "action en cours", "_Je **suis en train de** cuisiner._"],
              ["**être sur le point de** + infinitif", "futur immédiat", "_Le spectacle **est sur le point de** commencer._"]),
        P("Au passé, on met _venir_ et _être_ à l'**imparfait** : _Il **venait d'**arriver quand tu as appelé. J'**étais en train de** dormir._"),
        NOTE("Ne confondez pas _venir de_ + infinitif (passé récent) et _venir de_ + lieu (origine) : _Je viens **de manger**_ / _Je viens **de Lyon**_."),
    ]),
], chain=[
    ("assumption", "Ces périphrases ajoutent une nuance d'aspect : juste avant, pendant, juste après."),
    ("mechanism", "_venir de_, _être en train de_, _être sur le point de_ + infinitif ; on conjugue seulement le premier verbe."),
    ("result", "Au passé, le premier verbe se met à l'imparfait."),
], why="Les flashs d'information et les annonces (compréhension orale) emploient constamment ces périphrases.",
  look=["le moment de l'action par rapport à maintenant"],
  traps=["*_j'ai venu de manger_", "_venir de_ (récent) confondu avec _aller_ (futur)"],
  distractors=["une périphrase de sens opposé", "le passé composé de _venir_"],
  questions=[
    Q("a", 1, "conceptual", "Le gouvernement ___ annoncer une nouvelle réforme : c'était il y a dix minutes.", ("vient d'", "Passé récent → _venir de_."), [("va", "_aller_ + infinitif = futur proche."), ("est sur le point d'", "C'est le futur immédiat.")]),
    Q("a", 1, "conceptual", "Ne le dérange pas, il ___ réviser ses examens.", ("est en train de", "Action en cours → _être en train de_."), [("vient de", "Il est occupé maintenant, pas juste avant."), ("est sur le point de", "L'action a déjà commencé.")]),
    Q("a", 2, "conceptual", "Dépêche-toi, le film ___ commencer !", ("est sur le point de", "Futur immédiat → _être sur le point de_."), [("vient de", "Le film n'a pas encore commencé."), ("est en train de", "Le film n'a pas encore commencé.")]),
    Q("a", 2, "form", "Quand tu m'as appelé, je ___ rentrer.", ("venais de", "Passé récent dans un récit → imparfait de _venir de_."), [("suis venu de", "Au passé, _venir de_ se met à l'imparfait."), ("viens de", "Le récit est au passé.")]),
    Q("a", 3, "form", "Nous ___ dîner quand l'orage a éclaté.", ("étions en train de", "Action en cours dans le passé → imparfait d'_être en train de_."), [("avons été en train de", "Au passé, on met _être_ à l'imparfait."), ("sommes en train de", "Le récit est au passé.")]),
  ],
  cards=[R("periphrases", "a", "Venir de / être en train de / être sur le point de", "Trois périphrases d'aspect ?", "**venir de** : passé récent ; **être en train de** : en cours ; **être sur le point de** : futur immédiat (+ infinitif).")])

b.write()
