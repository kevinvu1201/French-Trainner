from fr import NOTE, P, Q, R, S, TABLE, UL, Book

b = Book("pronoms")
REF = "Repère : _Grammaire progressive du français_, chapitre {} (p. {})."

# ================================================================ chapitre 20
c = b.chapter(20, "Le pronom « en »", focus=[
    P("_En_ remplace un nom précédé de **de** (partitif, quantité, verbe en _de_). C'est un pronom de reprise indispensable pour éviter les répétitions, "
      "à l'oral comme à l'écrit : _Des solutions ? Il **en** existe plusieurs._"),
    P(REF.format(20, 90)),
], los={
    "a": "Remplacer un nom partitif ou une quantité par _en_ (en garder la quantité).",
    "b": "Remplacer un complément introduit par _de_ (parler de, avoir besoin de…) par _en_.",
})
c.module(1, "« En » partitif et « en » avec les verbes en « de »", sections=[
    ("a", [
        P("_En_ remplace **du, de la, des** + nom : _Tu veux **du** café ? — Oui, j'**en** veux._"),
        P("Avec une **quantité**, on garde la quantité **après** le verbe : _Tu as **des** frères ? — J'**en** ai **deux**. Il y a **beaucoup de** monde ? — Il y **en** a **beaucoup**._"),
        P("Négation : _Je n'**en** veux **pas**. Il n'y **en** a **plus**._"),
        NOTE("_Un / une_ se répète : _Tu as une voiture ? — Oui, j'**en** ai **une**._ (mais à la négation : _Non, je n'**en** ai **pas**_)."),
    ]),
    ("b", [
        P("_En_ remplace **de + chose / idée** après un verbe : _Tu parles **de ton voyage** ? — Oui, j'**en** parle. J'ai besoin **de ce livre** → J'**en** ai besoin._"),
        P("Pour une **personne**, on garde **de + pronom tonique** : _Tu parles **de ta sœur** ? — Oui, je parle **d'elle**._"),
        NOTE("Place : devant le verbe conjugué, ou devant l'infinitif : _Je vais **en** acheter. J'**en** ai acheté._ À l'impératif affirmatif : _Prends-**en** !_"),
    ]),
], chain=[
    ("assumption", "_En_ reprend un groupe introduit par _de_ (partitif, quantité, construction verbale)."),
    ("mechanism", "On place _en_ devant le verbe et on garde la quantité exprimée après le verbe."),
    ("result", "Pour une personne, on préfère _de_ + pronom tonique (_de lui, d'elle_)."),
], why="_En_ est l'un des pronoms les plus fréquents à l'oral : l'éviter rend le discours répétitif.",
  look=["_de / du / des_ devant le nom à remplacer", "une quantité à garder", "une chose ou une personne ?"],
  traps=["*_j'ai deux_ (oubli de _en_)", "*_j'en parle_ pour une personne", "_en_ mal placé avec un infinitif"],
  distractors=["_le / les_ à la place de _en_", "_y_ à la place de _en_", "la quantité oubliée"],
  questions=[
    Q("a", 1, "form", "Tu bois du café ? — Oui, j'___ bois tous les matins.", ("en", "_du café_ → _en_."), [("le", "_le_ remplace un nom défini (_le café_)."), ("y", "_y_ remplace _à_ + chose.")]),
    Q("a", 1, "form", "Combien de frères as-tu ? — J'___ ai trois.", ("en", "Quantité → _en_ + quantité après le verbe."), [("les", "On garde la quantité : il faut _en_."), ("y", "_y_ ne remplace pas une quantité.")]),
    Q("a", 2, "form", "Il reste du pain ? — Non, il n'y ___ a plus.", ("en", "Partitif à la négation → _en_."), [("le", "On parle d'une quantité, pas du pain en général."), ("lui", "_lui_ remplace une personne.")]),
    Q("a", 2, "form", "Tu as une voiture ? — Oui, ___.", ("j'en ai une", "_une voiture_ → _en … une_."), [("je l'ai", "_l'_ remplace une voiture précise (_la voiture_)."), ("j'en ai", "Avec _un / une_, on répète _une_ à l'affirmatif.")]),
    Q("a", 3, "form", "Des pommes ? Je vais ___ acheter un kilo.", ("en", "_en_ se place devant l'infinitif dont il dépend."), [("les", "Une quantité (_un kilo_) demande _en_."), ("y", "_y_ ne remplace pas une quantité.")]),
    Q("b", 1, "form", "Tu as besoin de ton ordinateur ? — Oui, j'___ ai besoin.", ("en", "_avoir besoin de_ + chose → _en_."), [("le", "_avoir besoin_ se construit avec _de_ → _en_."), ("y", "_y_ remplace _à_ + chose.")]),
    Q("b", 2, "form", "Vous parlez souvent de votre père ? — Oui, je parle souvent ___.", ("de lui", "Personne après _parler de_ → _de lui_."), [("en", "Pour une personne, on préfère _de lui_."), ("lui", "_parler à qqn_ → _lui_, mais ici c'est _parler de_.")]),
    Q("b", 2, "form", "Ce problème ? Nous ___ discuterons à la réunion.", ("en", "_discuter de_ + chose → _en_."), [("le", "_discuter_ se construit avec _de_ → _en_."), ("y", "_y_ remplace _à_ + chose.")]),
  ],
  cards=[R("en-quantite", "a", "En + quantité", "Tu as des enfants ? — Oui, j'… deux.", "J'**en** ai **deux** : _en_ devant le verbe, la quantité après."),
         R("en-de", "b", "En et les verbes en de", "Je parle de mon projet / de ma mère → ?", "J'**en** parle (chose) / Je parle **d'elle** (personne).")])

# ================================================================ chapitre 24
c = b.chapter(24, "Le pronom « y »", focus=[
    P("_Y_ remplace un **lieu** (_à, en, dans, chez…_) ou un complément introduit par **à** (chose ou idée) : _Tu penses **à tes examens** ? — Oui, j'**y** pense._"),
    P(REF.format(24, 104)),
], los={
    "a": "Remplacer un lieu par _y_.",
    "b": "Remplacer _à_ + chose / idée par _y_ (et _à_ + personne par _lui_ ou _à lui_).",
})
c.module(1, "« Y » lieu et « y » avec les verbes en « à »", sections=[
    ("a", [
        P("_Y_ remplace un lieu où l'on va ou où l'on est : _Tu vas **à Lyon** ? — Oui, j'**y** vais. Il habite **en Suisse** ? — Oui, il **y** habite depuis 2015._"),
        NOTE("Le lieu d'origine (_de Lyon_) est remplacé par **en** : _Tu viens de Lyon ? — Oui, j'**en** viens._ Devant _irai, irais_ (futur et conditionnel d'_aller_), "
             "_y_ disparaît : _Tu iras à Lyon ? — Oui, j'irai._"),
    ]),
    ("b", [
        P("_Y_ remplace **à + chose / idée** : _penser à, s'intéresser à, participer à, répondre à (un message), réfléchir à, s'habituer à_ : "
          "_Tu as répondu **à son mail** ? — Oui, j'**y** ai répondu._"),
        P("Pour une **personne** : _répondre, téléphoner, parler, écrire à qqn_ → **lui / leur** ; _penser, s'intéresser, s'habituer à qqn_ → **à lui, à elle** : "
          "_Je **lui** réponds. Je pense **à elle**._"),
    ]),
], chain=[
    ("assumption", "_Y_ reprend un lieu ou un complément introduit par _à_."),
    ("mechanism", "Lieu ou chose → _y_ devant le verbe ; personne → _lui / leur_ ou _à lui / à elle_ selon le verbe."),
    ("result", "L'origine (_de_) passe par _en_, pas par _y_."),
], why="_J'y pense, j'y tiens, je m'y oppose_ : expressions fréquentes du débat oral au DELF.",
  look=["un lieu ou _à_ + chose ?", "une personne ?", "la préposition du verbe (_à_ ou _de_)"],
  traps=["*_j'y pense_ pour une personne", "_y_ pour un lieu d'origine", "*_je lui pense_"],
  distractors=["_en_ à la place de _y_", "_lui_ pour une chose"],
  questions=[
    Q("a", 1, "form", "Tu vas souvent à la piscine ? — Oui, j'___ vais le mardi.", ("y", "Lieu → _y_."), [("en", "_en_ remplace un lieu d'origine (_de_)."), ("la", "_aller_ ne se construit pas avec un COD.")]),
    Q("a", 2, "form", "Vous habitez toujours à Bordeaux ? — Oui, nous ___ habitons depuis dix ans.", ("y", "Lieu → _y_."), [("en", "On reste dans le lieu : _y_."), ("le", "_habiter à_ + lieu → _y_.")]),
    Q("a", 2, "form", "Tu reviens de la plage ? — Oui, j'___ reviens à l'instant.", ("en", "Lieu d'origine (_de_) → _en_."), [("y", "_y_ remplace un lieu où l'on va ou où l'on est."), ("la", "_revenir_ ne prend pas de COD.")]),
    Q("b", 1, "form", "Tu penses à ton entretien de demain ? — Oui, j'___ pense sans arrêt.", ("y", "_penser à_ + chose → _y_."), [("en", "_penser_ se construit avec _à_, pas _de_."), ("lui", "_lui_ remplace une personne.")]),
    Q("b", 2, "form", "Tu as répondu à ta directrice ? — Oui, je ___ ai répondu hier.", ("lui", "_répondre à_ + personne → _lui_."), [("y", "_y_ ne remplace pas une personne."), ("l'", "_répondre_ se construit avec _à_ : COI.")]),
    Q("b", 2, "form", "Tu penses souvent à ta grand-mère ? — Oui, je pense souvent ___.", ("à elle", "_penser à_ + personne → _à elle_."), [("lui", "Avec _penser à_, on ne dit pas *_je lui pense_."), ("y", "_y_ ne remplace pas une personne.")]),
    Q("b", 2, "form", "Ils participeront au débat ? — Non, ils n'___ participeront pas.", ("y", "_participer à_ + chose → _y_."), [("en", "_participer_ se construit avec _à_."), ("le", "_participer_ n'a pas de COD.")]),
  ],
  cards=[R("y-lui", "b", "Y / lui / à lui", "penser à son examen / répondre à sa mère / penser à sa mère ?", "j'**y** pense ; je **lui** réponds ; je pense **à elle**.")])

# ================================================================ chapitre 28
c = b.chapter(28, "Les pronoms compléments", focus=[
    P("Les pronoms COD (_le, la, les_) et COI (_lui, leur_) évitent les répétitions et rendent un texte fluide. Leur choix dépend de la construction du verbe "
      "(avec ou sans _à_) ; leur ordre, quand il y en a deux, est fixe. C'est un point clé du niveau B1–B2."),
    P(REF.format(28, 124)),
], los={
    "a": "Remplacer un complément direct par _le, la, l', les_ (et _me, te, nous, vous_).",
    "b": "Remplacer un complément indirect de personne par _lui, leur_.",
    "c": "Ordonner deux pronoms compléments et placer les pronoms avec un infinitif ou un temps composé.",
})
c.module(1, "Les pronoms directs et indirects", sections=[
    ("a", [
        P("**COD** (verbe sans préposition) : _Je regarde **le film** → Je **le** regarde. J'aime **ces chansons** → Je **les** aime._"),
        TABLE(["me (m')", "te (t')", "le / la (l')", "nous", "vous", "les"]),
        P("Ils peuvent remplacer une **personne** ou une **chose** déterminée (défini, possessif, démonstratif). _Le_ neutre reprend une idée : _Il est parti ? Je **le** sais._"),
    ]),
    ("b", [
        P("**COI de personne** (verbe + **à** + personne) : _Je parle **à Marie** → Je **lui** parle. Je téléphone **à mes parents** → Je **leur** téléphone._"),
        TABLE(["me", "te", "**lui** (masc. et fém.)", "nous", "vous", "**leur** (invariable)"]),
        UL("Verbes de communication et d'échange : _parler, dire, écrire, téléphoner, répondre, demander, donner, envoyer, offrir, prêter, emprunter, plaire, sourire, ressembler **à** qqn_.",
           "Mais : _aider, appeler, remercier, inviter, écouter, attendre, regarder **qqn**_ sont des verbes **directs** : _Je **l'**aide. Je **les** remercie._"),
        NOTE("_Leur_ pronom ne prend jamais de _s_ : _Je **leur** écris_ (≠ possessif _leurs livres_)."),
    ]),
], chain=[
    ("assumption", "Le pronom dépend de la construction du verbe : direct (sans préposition) ou indirect (avec _à_)."),
    ("mechanism", "COD → _le, la, les_ ; COI de personne → _lui, leur_ ; on vérifie la construction : _aider qqn_ (direct), _téléphoner à qqn_ (indirect)."),
    ("result", "Les deux séries sont identiques à la 1re et à la 2e personne (_me, te, nous, vous_)."),
], why="Confondre _le / lui_ (_*je lui aide_) est l'une des erreurs les plus pénalisées à l'oral comme à l'écrit.",
  look=["la construction du verbe : avec ou sans _à_ ?", "personne ou chose ?", "singulier ou pluriel ?"],
  traps=["*_je lui aide_", "*_je le téléphone_", "*_je leurs parle_"],
  distractors=["COD / COI inversés", "_leurs_ avec un _s_"],
  questions=[
    Q("a", 1, "form", "Tu connais ce restaurant ? — Oui, je ___ connais bien.", ("le", "_connaître qqch_ (direct), masculin → _le_."), [("lui", "_connaître_ est un verbe direct."), ("en", "_en_ remplace un nom introduit par _de_.")]),
    Q("a", 1, "form", "Tu as vu mes lunettes ? — Non, je ne ___ ai pas vues.", ("les", "COD pluriel → _les_."), [("leur", "_voir_ est un verbe direct."), ("en", "Les lunettes sont déterminées (_mes_) → _les_.")]),
    Q("b", 1, "form", "Tu as téléphoné à ta mère ? — Oui, je ___ ai téléphoné hier.", ("lui", "_téléphoner à qqn_ → _lui_."), [("l'", "_téléphoner_ est un verbe indirect."), ("la", "_téléphoner_ est un verbe indirect.")]),
    Q("b", 1, "form", "J'ai écrit à mes cousins pour ___ annoncer la nouvelle.", ("leur", "_annoncer qqch à qqn_ → _leur_ (pluriel)."), [("les", "On annonce quelque chose _à_ quelqu'un."), ("leurs", "Le pronom _leur_ est invariable.")]),
    Q("b", 2, "form", "Ton frère a besoin d'aide ? Je vais ___ aider.", ("l'", "_aider qqn_ est un verbe direct."), [("lui", "*_aider à qqn_ n'existe pas : _aider_ est direct."), ("y", "_y_ ne remplace pas une personne.")]),
    Q("b", 2, "form", "Les clients sont satisfaits ? — Oui, le nouveau service ___ plaît beaucoup.", ("leur", "_plaire à qqn_ → _leur_."), [("les", "_plaire_ se construit avec _à_."), ("leurs", "_leur_ pronom est invariable.")]),
    Q("b", 2, "form", "Mes collègues m'ont beaucoup aidé : je ___ remercie.", ("les", "_remercier qqn_ est un verbe direct."), [("leur", "_remercier_ est direct : _remercier qqn de qqch_."), ("lui", "_mes collègues_ est pluriel, et le verbe est direct.")]),
    Q("a", 3, "form", "Le directeur va démissionner ? Je ne ___ savais pas !", ("le", "_le_ neutre reprend une idée."), [("la", "_le_ neutre est masculin."), ("en", "_savoir qqch_ est direct.")]),
  ],
  cards=[R("cod-coi", "b", "Le / lui", "aider, appeler, remercier qqn ; téléphoner, répondre, parler à qqn ?", "directs → **le / la / les** ; indirects (_à_) → **lui / leur**.", mistake="*_Je lui aide_ ; *_je leurs écris_.")])
c.module(2, "L'ordre et la place des pronoms", sections=[
    ("c", [
        P("**Place** : devant le verbe conjugué (_je **le** vois_) ; aux temps composés, devant l'auxiliaire (_je **l'**ai vu_) ; avec un infinitif, devant l'infinitif (_je vais **le** voir_)."),
        TABLE(["1", "2", "3", "4", "5"], ["me, te, se, nous, vous", "le, la, les", "lui, leur", "y", "en"]),
        UL("_Il **me le** donne. Je **le lui** donne. Je **les leur** envoie. Il **m'en** parle. Il **y en** a._"),
        P("**Accord du participe** : avec _avoir_, le participe s'accorde avec le COD placé avant : _Ces photos ? Je **les** ai pris**es**._ (pas d'accord avec _lui, leur, en_)."),
        NOTE("À l'**impératif affirmatif**, les pronoms suivent le verbe, COD d'abord : _Donne-**le-moi**. Envoie-**la-leur**._ (chapitre 30)"),
    ]),
], chain=[
    ("assumption", "Quand deux pronoms se suivent, leur ordre est fixe."),
    ("mechanism", "_me/te/nous/vous_ → _le/la/les_ → _lui/leur_ → _y_ → _en_ ; le groupe se place devant le verbe conjugué ou l'infinitif."),
    ("result", "Avec _avoir_, le participe passé s'accorde avec un COD placé avant."),
], why="Les doubles pronoms (_je le lui ai dit_) sont un marqueur clair du niveau B2.",
  look=["le nombre de pronoms", "un infinitif ou un temps composé", "un COD placé avant le participe"],
  traps=["*_je lui le donne_", "*_je l'ai pris_ pour _les photos_", "*_je le vais voir_"],
  distractors=["l'ordre inversé", "le pronom placé devant le verbe conjugué au lieu de l'infinitif"],
  questions=[
    Q("c", 2, "form", "Tu as rendu le livre à Paul ? — Oui, je ___ ai rendu hier.", ("le lui", "Ordre : _le_ avant _lui_."), [("lui le", "L'ordre est _le lui_."), ("lui l'", "L'ordre est _le lui_.")]),
    Q("c", 2, "form", "Ta sœur t'a montré ses photos ? — Oui, elle ___ a montrées.", ("me les", "Ordre : _me_ avant _les_."), [("les me", "L'ordre est _me les_."), ("me leur", "_ses photos_ est COD : _les_.")]),
    Q("c", 2, "form", "Je veux voir ce film : je ___ voir ce soir.", ("vais le", "Le pronom se place devant l'infinitif dont il dépend."),
      [("le vais", "Le pronom complète _voir_, pas _aller_ : il se place devant l'infinitif."), ("vais lui", "_voir_ est un verbe direct : _le_.")]),
    Q("c", 3, "form", "Ces lettres ? Je les ai ___ ce matin.", ("écrites", "COD _les_ (féminin pluriel) placé avant → accord."), [("écrit", "Le participe s'accorde avec le COD placé avant."), ("écrits", "_lettres_ est féminin.")]),
    Q("c", 3, "form", "Des conseils ? Mon professeur ___ a donné beaucoup.", ("m'en", "Ordre : _me_ avant _en_."), [("en m'", "L'ordre est _m'en_."), ("me les", "_beaucoup_ (quantité) demande _en_.")]),
    Q("c", 2, "form", "Tu peux prêter ta voiture à tes parents ? — Oui, je peux ___ prêter.", ("la leur", "Ordre : _la_ avant _leur_, devant l'infinitif."), [("leur la", "L'ordre est _la leur_."), ("les leur", "_ta voiture_ est singulier.")]),
  ],
  sets=[S("Le cadeau d'anniversaire",
    "Deux amies parlent au téléphone :\n\n« — Tu as acheté le cadeau pour Julie ?\n\n— Oui, je **(1)** ___ ai acheté hier. Je vais **(2)** ___ donner samedi.\n\n"
    "— Et les invitations ? Tu **(3)** ___ as envoyées aux autres ?\n\n— Oui, je **(4)** ___ ai envoyées lundi. »",
    [Q("a", 1, "form", "Blanc (1) :", ("l'", "_le cadeau_ (COD) → _l'_ devant _ai_."), [("lui", "_acheter qqch_ : le cadeau est COD."), ("en", "Le cadeau est déterminé → _le_.")]),
     Q("c", 2, "form", "Blanc (2) :", ("le lui", "_donner le cadeau à Julie_ → _le lui_."), [("lui le", "L'ordre est _le lui_."), ("la lui", "_cadeau_ est masculin.")]),
     Q("a", 1, "form", "Blanc (3) :", ("les", "_les invitations_ (COD) → _les_."), [("leur", "Les invitations sont le COD."), ("en", "Les invitations sont déterminées → _les_.")]),
     Q("c", 3, "form", "Blanc (4) :", ("les leur", "_envoyer les invitations aux autres_ → _les leur_."), [("leur les", "L'ordre est _les leur_."), ("les leurs", "_leur_ est invariable.")])])],
  cards=[R("ordre-pronoms", "c", "Ordre des doubles pronoms", "me / le / lui / y / en : ordre ?", "**me, te, nous, vous → le, la, les → lui, leur → y → en**.", examples=["Je te le donne. Je le lui donne. Il m'en parle."])])

# ================================================================ chapitre 29
c = b.chapter(29, "Les pronoms toniques", focus=[
    P("Les pronoms toniques (_moi, toi, lui, elle, nous, vous, eux, elles_) servent à insister, après une préposition et dans les réponses courtes. "
      "Ils renforcent l'opinion : _**Moi**, je pense que…_"),
    P(REF.format(29, 132)),
], los={"a": "Employer les pronoms toniques pour insister, après une préposition, après _c'est_ et dans les comparaisons."})
c.module(1, "Les pronoms toniques", sections=[
    ("a", [
        TABLE(["je → **moi**", "tu → **toi**", "il → **lui**", "elle → **elle**", "nous → **nous**", "vous → **vous**", "ils → **eux**", "elles → **elles**"]),
        UL("**Insistance** : _**Moi**, je préfère la mer. **Eux**, ils ne viennent pas._",
           "**Après une préposition** : _avec **moi**, chez **eux**, pour **elle**, sans **toi**, à côté de **lui**_.",
           "**Après c'est / ce sont** : _C'est **moi** qui ai appelé. Ce sont **eux** qui ont gagné._",
           "**Réponses courtes et comparaisons** : _Qui veut du café ? — **Moi** ! Il est plus grand que **toi**. **Moi aussi / moi non plus**._",
           "**Soi** pour un sujet indéfini : _**On** doit penser à **soi**. Chacun pour **soi**._"),
        NOTE("_C'est moi qui **ai**_ : le verbe s'accorde avec le pronom tonique (_c'est nous qui **sommes**_)."),
    ]),
], chain=[
    ("assumption", "Les pronoms toniques s'emploient là où les pronoms sujets ou compléments ne peuvent pas aller."),
    ("mechanism", "Ils suivent une préposition, _c'est_, _que_ (comparaison) ou se placent en tête pour insister."),
    ("result", "Après _c'est … qui_, le verbe s'accorde avec le pronom tonique."),
], why="_Moi, je…_, _quant à moi_, _selon eux_ : les pronoms toniques structurent la prise de position à l'oral.",
  look=["une préposition, _c'est_ ou _que_ avant le pronom", "un sujet indéfini (_on, chacun_)"],
  traps=["*_avec ils_", "*_c'est moi qui a_", "*_chacun pour lui_ au sens général"],
  distractors=["le pronom sujet après une préposition", "le verbe à la 3e personne après _c'est moi qui_"],
  questions=[
    Q("a", 1, "form", "Tu viens au cinéma avec ___ ?", ("nous", "Après une préposition → pronom tonique."), [("on", "_on_ ne s'emploie pas après une préposition."), ("nos", "_nos_ est un possessif.")]),
    Q("a", 1, "form", "Mes voisins sont absents : je garde le chat chez ___.", ("eux", "_ils_ → _eux_ après une préposition."), [("ils", "Après une préposition → tonique."), ("leur", "_leur_ est un pronom COI ou un possessif.")]),
    Q("a", 2, "form", "C'est moi qui ___ organisé la soirée.", ("ai", "Accord avec _moi_ → _j'ai_."), [("a", "Le verbe s'accorde avec le pronom tonique."), ("avons", "_moi_ = 1re personne du singulier.")]),
    Q("a", 2, "form", "Je n'aime pas les films d'horreur. — ___ non plus.", ("Moi", "Réponse courte → tonique."), [("Je", "_je_ ne s'emploie pas seul."), ("Me", "_me_ est un pronom complément.")]),
    Q("a", 2, "form", "Ma sœur est plus âgée que ___.", ("moi", "Comparaison → tonique après _que_."), [("je", "Après _que_ (comparaison) sans verbe → tonique."), ("me", "_me_ est un pronom complément.")]),
    Q("a", 3, "form", "Quand on est malade, on doit prendre soin de ___.", ("soi", "Sujet indéfini (_on_) → _soi_."), [("lui", "Avec _on_, le pronom tonique est _soi_."), ("eux", "_on_ est singulier et indéfini.")]),
  ],
  cards=[R("toniques", "a", "Pronoms toniques", "Après une préposition ou c'est : je / il / ils ?", "**moi, lui, eux** (_avec moi, chez lui, c'est eux_) ; sujet indéfini → **soi**.")])

b.write()
