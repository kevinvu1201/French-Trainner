from fr import NOTE, P, Q, R, S, TABLE, UL, Book

b = Book("questions")
REF = "Repère : _Grammaire progressive du français_, chapitre {} (p. {})."

# ================================================================ chapitre 3
c = b.chapter(3, "La négation et l'interrogation (1)", focus=[
    P("Poser une question et répondre négativement sont les gestes de base de l'interaction orale. Il y a trois registres de question, "
      "et la réponse à une question négative se fait avec **si**."),
    P(REF.format(3, 18)),
], los={
    "a": "Former la négation simple (_ne … pas_) et la question totale dans les trois registres.",
    "b": "Répondre _oui, non, si_ et _moi aussi / moi non plus_.",
})
c.module(1, "La négation simple, la question simple et la réponse", sections=[
    ("a", [
        P("**Négation** : _ne_ + verbe + _pas_ : _Je **ne** parle **pas** chinois. Il **n'**est **pas** là._ À l'oral familier, le _ne_ disparaît souvent (_je parle pas_) — pas à l'écrit."),
        TABLE(["Registre", "Question totale (réponse oui / non)"],
              ["familier (intonation)", "_Tu viens ?_"], ["courant", "_**Est-ce que** tu viens ?_"], ["soutenu (inversion)", "_Viens-**tu** ? Votre fils vient-**il** ?_"]),
        NOTE("Inversion avec _il / elle / on_ et un verbe terminé par une voyelle : **-t-** : _Parle-**t**-il anglais ? A-**t**-elle fini ?_"),
    ]),
    ("b", [
        UL("Question affirmative : **oui** / **non** : _Tu aimes le jazz ? — Oui. / Non._",
           "Question **négative** : **si** pour contredire, **non** pour confirmer : _Tu n'aimes pas le jazz ? — **Si**, j'adore ! / **Non**, pas du tout._",
           "Accord : _J'aime le jazz. — **Moi aussi**._ / _Je n'aime pas le jazz. — **Moi non plus**._"),
    ]),
], chain=[
    ("assumption", "La négation encadre le verbe ; la question existe en trois registres."),
    ("mechanism", "_ne … pas_ autour du verbe conjugué ; question par intonation, _est-ce que_ ou inversion (avec _-t-_ entre deux voyelles)."),
    ("result", "On répond _si_ à une question négative pour la contredire."),
], why="Les registres de question comptent dans l'épreuve orale : l'inversion convient à l'entretien formel.",
  look=["le registre attendu", "une question négative ?"],
  traps=["*_parle-il_", "_oui_ en réponse à une question négative", "*_moi aussi_ après une négation"],
  distractors=["l'inversion sans _-t-_", "_oui_ au lieu de _si_"],
  questions=[
    Q("a", 1, "form", "Je ___ fume ___ : j'ai arrêté il y a deux ans.", ("ne … pas", "_ne_ + verbe + _pas_."), [("pas … ne", "L'ordre est _ne … pas_."), ("non … pas", "La négation verbale est _ne … pas_.")]),
    Q("a", 2, "form", "___ il au cinéma ce soir ?", ("Va-t-", "Inversion _va + il_ → _va-t-il_."), [("Va-", "Il faut _-t-_ entre deux voyelles."), ("Vat-", "Le _t_ s'écrit entre deux traits d'union.")]),
    Q("a", 2, "form", "Question soutenue : « ___ vous la réponse ? »", ("Connaissez-", "Inversion verbe-sujet avec trait d'union."), [("Est-ce que connaissez", "_est-ce que_ ne s'emploie pas avec l'inversion."), ("Vous connaissez-", "L'inversion place le verbe avant le sujet.")]),
    Q("b", 1, "conceptual", "Tu n'as pas faim ? — ___, j'ai très faim !", ("Si", "Contredire une question négative → _si_."), [("Oui", "Après une question négative, on contredit avec _si_."), ("Non", "_non_ confirmerait qu'il n'a pas faim.")]),
    Q("b", 1, "conceptual", "J'adore le chocolat noir. — Moi ___ !", ("aussi", "Accord avec une phrase affirmative → _aussi_."),
      [("non plus", "_non plus_ suit une phrase négative."), ("si", "_si_ contredit une négation.")]),
    Q("b", 2, "conceptual", "Je ne suis jamais allé au Japon. — Moi ___.", ("non plus", "Accord avec une phrase négative → _non plus_."), [("aussi", "_moi aussi_ suit une phrase affirmative."), ("si", "_si_ contredirait.")]),
  ],
  cards=[R("si", "b", "Oui / si", "Réponse positive à une question négative ?", "**Si** : _Tu ne viens pas ? — Si !_"),
         R("inversion-t", "a", "Inversion et -t-", "Parle … il ?", "**Parle-t-il** : _-t-_ entre deux voyelles (_a-t-elle, va-t-on_).")])

# ================================================================ chapitre 33
c = b.chapter(33, "L'interrogation (2) : les mots interrogatifs", focus=[
    P("Les mots interrogatifs (_où, quand, comment, pourquoi, qui, que, quoi, quel, lequel_) servent à demander une information précise. "
      "Au DELF oral, on doit poser des questions variées et correctes à l'examinateur (débat, simulation)."),
    P(REF.format(33, 148)),
], los={
    "a": "Poser une question partielle avec _où, quand, comment, combien, pourquoi_ dans les trois registres.",
    "b": "Choisir entre _qui, que, quoi_ et _qu'est-ce qui / qu'est-ce que_.",
    "c": "Employer _quel(s), quelle(s)_, _lequel_ et l'exclamation.",
})
c.module(1, "« Où », « quand », « comment », « qui », « que », « quoi »", sections=[
    ("a", [
        TABLE(["Registre", "Exemple"], ["familier", "_Tu pars **quand** ? Tu vas **où** ?_"], ["courant", "_**Quand est-ce que** tu pars ?_"], ["soutenu", "_**Quand** partez-vous ? **Où** votre fils travaille-t-il ?_"]),
        P("_Où, quand, comment, combien (de), pourquoi_ : on peut aussi faire l'inversion simple avec un nom sujet court : _**Où** travaille **ton frère** ?_"),
    ]),
    ("b", [
        TABLE(["", "Personne", "Chose"],
              ["Sujet", "**Qui** / Qui est-ce qui téléphone ?", "**Qu'est-ce qui** se passe ?"],
              ["COD", "**Qui** cherches-tu ? / Qui est-ce que tu cherches ?", "**Que** cherches-tu ? / **Qu'est-ce que** tu cherches ? / Tu cherches **quoi** ?"],
              ["après préposition", "**Avec qui** pars-tu ?", "**À quoi** penses-tu ? **De quoi** parlez-vous ?"]),
        NOTE("**Quoi** se place en fin de question (familier) ou après une préposition. **Que** se place en tête avec l'inversion. *_Qu'est-ce qui tu veux_ est faux : _qui_ = sujet, _que_ = COD."),
    ]),
], chain=[
    ("assumption", "Une question partielle demande une information précise : lieu, temps, manière, personne, chose."),
    ("mechanism", "Pour les personnes : _qui_ ; pour les choses : _qu'est-ce qui_ (sujet), _que / qu'est-ce que_ (COD), _quoi_ (après une préposition ou en fin)."),
    ("result", "Le registre se choisit selon la situation : _est-ce que_ (courant), inversion (soutenu)."),
], why="L'épreuve orale valorise les questions variées et adaptées au registre (interaction avec l'examinateur).",
  look=["personne ou chose ?", "sujet, COD ou après une préposition ?", "le registre"],
  traps=["*_qu'est-ce qui tu fais_", "*_de qui tu parles ?_ pour une chose", "*_que tu fais ?_"],
  distractors=["_qui / que_ inversés", "_quoi_ en tête de question sans préposition"],
  questions=[
    Q("a", 1, "form", "___ est-ce que vous partez en vacances ? — En juillet.", ("Quand", "Réponse temporelle → _quand_."), [("Où", "_où_ demande un lieu."), ("Comment", "_comment_ demande une manière.")]),
    Q("a", 2, "form", "Question soutenue : « ___ votre fille fait-elle ses études ? »", ("Où", "_où_ + inversion complexe (_votre fille fait-elle_)."), [("Où est-ce que", "_est-ce que_ ne se combine pas avec l'inversion."), ("Qu'", "_que_ demanderait l'objet, pas le lieu.")]),
    Q("a", 1, "form", "___ coûte ce billet ? — 45 euros.", ("Combien", "Prix → _combien_."), [("Comment", "_comment_ demande une manière."), ("Quand", "_quand_ demande un moment.")]),
    Q("b", 1, "form", "___ s'est passé hier soir ? Il y a eu un accident ?", ("Qu'est-ce qui", "Chose sujet → _qu'est-ce qui_."), [("Qu'est-ce que", "_que_ = COD ; ici la chose est sujet."), ("Qui", "_qui_ désigne une personne.")]),
    Q("b", 1, "form", "___ tu fais ce week-end ?", ("Qu'est-ce que", "Chose COD → _qu'est-ce que_."), [("Qu'est-ce qui", "_qui_ = sujet ; ici le sujet est _tu_."), ("Que", "_que_ seul demande l'inversion (_que fais-tu_).")]),
    Q("b", 2, "form", "De ___ avez-vous parlé pendant la réunion ?", ("quoi", "Chose après une préposition → _quoi_."), [("que", "Après une préposition, on emploie _quoi_ pour une chose."), ("qu'est-ce que", "Cette forme ne suit pas une préposition.")]),
    Q("b", 2, "form", "___ est-ce que tu as invité à ton mariage ?", ("Qui", "Personne COD → _qui est-ce que_."), [("Qu'", "_qu'est-ce que_ demande une chose."), ("Quoi", "_quoi_ demande une chose.")]),
    Q("b", 3, "form", "Avec ___ partez-vous en voyage ?", ("qui", "Personne après une préposition → _qui_."), [("quoi", "_quoi_ désigne une chose."), ("lequel", "_lequel_ demande un choix entre des éléments déjà cités.")]),
  ],
  cards=[R("qui-que", "b", "Qui / que / quoi", "Qu'est-ce qui / qu'est-ce que ?", "**qu'est-ce qui** : chose sujet (_qu'est-ce qui se passe ?_) ; **qu'est-ce que** : chose COD (_qu'est-ce que tu fais ?_) ; **quoi** après une préposition.")])
c.module(2, "« Quel », « lequel » et l'exclamation", sections=[
    ("c", [
        P("**Quel / quelle / quels / quelles** + nom ou + _être_ : _**Quelle** heure est-il ? **Quels** sont vos projets ?_"),
        P("**Lequel / laquelle / lesquels / lesquelles** : choix entre des éléments connus : _J'ai deux robes. **Laquelle** préfères-tu ?_ "
          "Contractions : **auquel, auxquels, duquel, desquels** : _**Auquel** de ces projets participes-tu ?_"),
        P("**Exclamation** : _**Quel** beau paysage ! **Quelle** chance ! **Comme** c'est beau ! **Qu'**il est gentil !_"),
    ]),
], chain=[
    ("assumption", "_Quel_ accompagne un nom ; _lequel_ le remplace dans un choix."),
    ("mechanism", "Les deux s'accordent en genre et en nombre ; _lequel_ se contracte avec _à_ et _de_."),
    ("result", "_Quel_ et _comme_ servent aussi à l'exclamation."),
], why="_Quels sont, selon vous…?_ est une formule utile pour relancer le débat oral.",
  look=["le genre et le nombre du nom", "un nom après le mot (quel) ou non (lequel) ?"],
  traps=["*_quel sont vos projets_", "*_à lequel_"],
  distractors=["l'accord fautif de _quel_", "_quel_ sans nom pour un choix"],
  questions=[
    Q("c", 1, "form", "___ sont vos disponibilités la semaine prochaine ?", ("Quelles", "_disponibilités_, féminin pluriel."), [("Quels", "_disponibilités_ est féminin."), ("Quel", "Le sujet est pluriel.")]),
    Q("c", 2, "form", "Il y a trois parcours possibles. ___ conseillez-vous ?", ("Lequel", "Choix entre des éléments connus, masculin singulier."), [("Quel", "_quel_ doit être suivi d'un nom ou de _être_."), ("Laquelle", "_parcours_ est masculin.")]),
    Q("c", 2, "form", "Parmi ces associations, ___ avez-vous adhéré ?", ("à laquelle", "_adhérer à_ + féminin singulier."), [("laquelle", "_adhérer_ se construit avec _à_."), ("auquel", "_association_ est féminin.")]),
    Q("c", 1, "form", "___ belle surprise !", ("Quelle", "Exclamation + nom féminin."), [("Comme", "_comme_ se construit avec une phrase (_comme c'est beau_)."), ("Quel", "_surprise_ est féminin.")]),
  ],
  cards=[R("lequel", "c", "Lequel et contractions", "à + lequel / de + lesquels ?", "**auquel**, **auxquels**, **à laquelle** ; **duquel**, **desquels**, **de laquelle**.")])

# ================================================================ chapitre 34
c = b.chapter(34, "La négation (2)", focus=[
    P("Au-delà de _ne … pas_, la négation se nuance : _ne … jamais, ne … plus, ne … rien, ne … personne, ne … aucun, ne … que, ni … ni, sans_. "
      "Ces formes enrichissent l'expression et sont souvent testées en compréhension (_il ne reste que…_ = seulement)."),
    P(REF.format(34, 152)),
], los={
    "a": "Employer _ne … jamais, plus, rien, personne, aucun, nulle part_ (et leur place aux temps composés).",
    "b": "Employer _ne … que_ (restriction), _ni … ni_ et _sans_.",
})
c.module(1, "« Ne … jamais », « ne … plus », etc.", sections=[
    ("a", [
        TABLE(["Affirmation", "Négation"], ["toujours, souvent", "**ne … jamais**"], ["encore (continuité)", "**ne … plus**"], ["déjà", "**ne … pas encore**"],
              ["quelque chose, tout", "**ne … rien**"], ["quelqu'un, tout le monde", "**ne … personne**"], ["un, des, quelques", "**ne … aucun(e)**"], ["quelque part, partout", "**ne … nulle part**"]),
        P("**Temps composés** : _jamais, plus, rien, pas_ se placent **avant** le participe : _Je n'ai **jamais** vu ça. Il n'a **rien** compris._ "
          "Mais _personne, aucun, nulle part_ se placent **après** : _Je n'ai vu **personne**. Il n'a trouvé **aucune** solution._"),
        P("**Infinitif** : les deux éléments se placent avant : _Il a décidé de **ne plus** fumer. Attention à **ne rien** oublier._"),
        NOTE("En position sujet : _**Personne n'**est venu. **Rien ne** marche. **Aucun** étudiant **n'**a réussi._ (jamais de _pas_ en plus)."),
    ]),
    ("b", [
        UL("**ne … que** = seulement (restriction, sens positif) : _Il **ne** boit **que** de l'eau. Il **n'**y a **qu'**une solution._",
           "**ni … ni … ne** / **ne … ni … ni** : _Je **n'**aime **ni** le thé **ni** le café. **Ni** Paul **ni** Marie **ne** sont venus._",
           "**sans** + infinitif / nom (sans article) : _Il est parti **sans** dire au revoir. Un café **sans** sucre._"),
        NOTE("Après _ni … ni_ ou _sans_, l'article indéfini et le partitif disparaissent : _Je n'ai ni frère ni sœur. Sans argent._"),
    ]),
], chain=[
    ("assumption", "La négation française a deux éléments : _ne_ + un second mot qui précise le sens."),
    ("mechanism", "_jamais, plus, rien_ suivent l'auxiliaire ; _personne, aucun, nulle part_ suivent le participe ; à l'infinitif, _ne_ + second mot le précèdent."),
    ("result", "_ne … que_ n'est pas une vraie négation : il signifie _seulement_."),
], why="Les QCM de compréhension reformulent souvent _ne … que_ par _seulement_, ou _ne … plus_ par _a cessé de_.",
  look=["le sens voulu (plus du tout, jamais, seulement ?)", "un temps composé ou un infinitif"],
  traps=["*_je n'ai vu pas personne_", "*_personne n'est pas venu_", "_ne … que_ compris comme une négation"],
  distractors=["le second mot mal placé", "_pas_ ajouté à une autre négation"],
  questions=[
    Q("a", 1, "form", "Il a arrêté de fumer : il ne fume ___.", ("plus", "Fin d'une habitude → _ne … plus_."), [("jamais", "_jamais_ signifie qu'il n'a jamais fumé."), ("rien", "_rien_ remplace un objet, pas une habitude.")]),
    Q("a", 1, "form", "Tu as déjà fini ? — Non, je n'ai ___ fini.", ("pas encore", "Négation de _déjà_ → _pas encore_."), [("plus", "_ne … plus_ indique la fin d'une action."), ("jamais", "_jamais_ ne répond pas à _déjà_ ici.")]),
    Q("a", 2, "form", "J'ai cherché partout mais je n'ai trouvé ___.", ("personne", "_personne_ après le participe passé."), [("pas personne", "On n'ajoute pas _pas_ à _personne_."), ("aucun", "_aucun_ doit être suivi d'un nom ou repris par _en_.")]),
    Q("a", 2, "form", "___ n'a répondu à mon annonce.", ("Personne", "_personne ne_ en position sujet."), [("Personne ne", "Le _n'_ est déjà dans la phrase."), ("Quelqu'un", "La phrase est négative (_n'_).")]),
    Q("a", 3, "form", "Il nous a demandé de ___ toucher.", ("ne rien", "À l'infinitif, _ne rien_ se place avant."), [("rien ne", "L'ordre est _ne rien_."), ("ne toucher rien", "À l'infinitif, _ne rien_ précède le verbe.")]),
    Q("a", 3, "form", "Elle n'a ___ expérience dans ce domaine.", ("aucune", "_aucune_ + nom féminin."), [("aucun", "_expérience_ est féminin."), ("pas aucune", "On n'ajoute pas _pas_ à _aucune_.")]),
    Q("b", 1, "conceptual", "« Il ne reste que trois places » signifie…", ("il reste seulement trois places.", "_ne … que_ = seulement."), [("il ne reste aucune place.", "_ne … que_ n'est pas une négation totale."), ("il reste plus de trois places.", "_ne … que_ indique une limite.")]),
    Q("b", 2, "form", "Je ne bois ___ café ___ thé le soir.", ("ni … ni", "Double négation coordonnée, sans article."), [("pas de … ni de", "La structure est _ne … ni … ni_."), ("ni du … ni du", "Après _ni … ni_, le partitif disparaît.")]),
    Q("b", 2, "form", "Il est parti ___ prévenir personne.", ("sans", "_sans_ + infinitif."), [("sans de", "_sans_ est suivi directement de l'infinitif."), ("ne pas", "Il faudrait un verbe conjugué.")]),
  ],
  sets=[S("Un village qui se vide",
    "Un journaliste décrit un village :\n\n« Il y a vingt ans, on comptait trois commerces. Aujourd'hui, il **(1)** ___ y a plus aucun. **(2)** ___ ne s'installe ici : les jeunes partent "
    "et ils ne reviennent **(3)** ___. Le maire n'a trouvé **(4)** ___ solution pour attirer de nouvelles familles. »",
    [Q("a", 1, "form", "Blanc (1) :", ("n'", "_ne … plus aucun_ : il faut _ne_."), [("ne", "Devant une voyelle → _n'_."), ("pas", "_pas_ ne s'ajoute pas à _plus aucun_.")]),
     Q("a", 2, "form", "Blanc (2) :", ("Personne", "Sujet négatif → _personne ne_."), [("Quelqu'un", "La phrase contient _ne_ : sens négatif."), ("Rien", "_rien_ désigne une chose ; ici, des personnes s'installent.")]),
     Q("a", 1, "form", "Blanc (3) :", ("jamais", "_ne … jamais_ = à aucun moment."), [("rien", "_revenir_ n'a pas de complément d'objet."), ("aucun", "_aucun_ doit accompagner un nom.")]),
     Q("a", 2, "form", "Blanc (4) :", ("aucune", "_aucune_ + nom féminin (_solution_)."), [("pas de", "_n'a trouvé pas de_ : l'ordre serait _n'a pas trouvé de_."), ("personne", "_personne_ désigne des gens.")])])],
  cards=[R("place-negation", "a", "Place de la négation au passé composé", "jamais / personne au passé composé ?", "Je n'ai **jamais** vu (avant le participe) ; je n'ai vu **personne** (après le participe)."),
         R("ne-que", "b", "Ne … que", "« Il ne mange que des légumes » = ?", "Il mange **seulement** des légumes (restriction, pas négation).")])

b.write()
