define(["underscore", "backbone", "backboneCommon", "ajaxControl", "memoriaUtil"], function(g, n, l, p, q) {
    function r(a, b) {
        if (!a.charaId || !b || !l.storage.gameUser || l.storage.gameUser.toJSON().eventTrainingId !== b.eventId) return !1;
        var d = !1,
            c = a.charaId;
        a = l.storage.gameUser.toJSON().trainingSelectedCharaNos.split(",");
        g.each(a, function(a) {
            c == a && (d = !0)
        });
        return d
    }
    var c = {},
        t = n.Collection.extend();
    n.Model.extend();
    c.totalEventEffectSet = function(a) {
        var b = 0,
            d = a.revision + 1;
        for (a.eventEffect = {}; b < d;) {
            if (a["equipPiece" +
                    (b + 1)]) {
                var c = a["equipPiece" + (b + 1)];
                c.eventType && (a.eventType = c.eventType.toLowerCase());
                c.eventId && (a.eventId = c.eventId);
                c.eventEffect && (a.eventEffect || (a.eventEffect = {}), a.bonusFlag = !0, g.each(c.eventEffect, function(b, d) {
                    d in a.eventEffect || (a.eventEffect[d] = 0);
                    a.eventEffect[d] += b | 0
                }))
            }
            b = b + 1 | 0
        }
        return a
    };
    c.memoriaEventSet = function() {
        var a = l.storage.userPieceList;
        a && a.each(function(a) {
            var b = c.memoriaEventCheck(a.toJSON());
            b && a.set(b)
        })
    };
    c.memoriaEventCheck = function(a) {
        if (!a) return !1;
        var b = [],
            d = {},
            c = p.getPageJson();
        g.each(c.eventList, function(c, e) {
            b.push(c.eventId);
            d[c.eventId] = c.eventType;
            c && c.parameterMap && c.parameterMap.PROTECTED_PIECE_ID && Number(c.parameterMap.PROTECTED_PIECE_ID) == a.pieceId && (a.unprotectLimitFlag = !0)
        });
        if (0 == b.length) return !1;
        if (a && a.piece && a.piece.pieceSkill) {
            c = null;
            c = 4 > a.lbCount ? a.piece.pieceSkill : a.piece.pieceSkill2;
            if (c.eventId && 0 <= b.indexOf(c.eventId)) {
                a.eventId = c.eventId;
                a.eventType = d[c.eventId];
                a.eventEffect = {};
                if (c.eventArt1) {
                    if (!(c.eventArt1.effectCode in a.eventEffect)) {
                        var e =
                            c.eventArt1.effectCode + "_" + c.eventArt1.genericValue;
                        a.eventEffect[e] = 0
                    }
                    a.eventEffect[e] += c.eventArt1.effectValue
                }
                c.eventArt2 && (c.eventArt2.effectCode in a.eventEffect || (e = c.eventArt2.effectCode + "_" + c.eventArt2.genericValue, a.eventEffect[e] = 0), a.eventEffect[e] += c.eventArt2.effectValue);
                c.eventArt3 && (c.eventArt3.effectCode in a.eventEffect || (e = c.eventArt3.effectCode + "_" + c.eventArt3.genericValue, a.eventEffect[e] = 0), a.eventEffect[e] += c.eventArt3.effectValue);
                a.eventDescription = c.eventDescription;
                return a
            }
            if (a.unprotectLimitFlag) return a
        }
        return !1
    };
    c.createCardList = function() {
        var a = [],
            b = p.getPageJson(),
            d = null;
        b.eventList && (d = b.eventList.filter(function(a, b) {
            if ("TRAINING" == a.eventType) return !0
        })[0]);
        var b = l.storage.userCharaList,
            h = l.storage.userCardList,
            e = l.storage.userPieceList,
            f = l.storage.userDeckList,
            k = l.storage.userPieceSetList;
        e.each(function(a) {
            a.set({
                equipFlag: !1,
                eventType: null,
                eventId: null,
                eventEffect: null,
                eventDescription: null,
                equipDeck: []
            }, {
                silent: !0
            })
        });
        f.each(function(a) {
            var b = a.toJSON();
            g.each(b, function(a, c) {
                if (-1 !== c.indexOf("userPieceId")) {
                    c =
                        11 <= b.deckType && 19 >= b.deckType ? "quest" : 20 == b.deckType ? "support" : 21 == b.deckType ? "arena" : 22 == b.deckType ? "eventArena" : "";
                    a = e.findWhere({
                        id: a
                    });
                    var d = a.toJSON();
                    d.equipDeck.push(c);
                    a.set(d, {
                        silent: !0
                    })
                }
            })
        });
        k.each(function(a) {
            a = a.toJSON();
            g.each(a, function(a, b) {
                -1 !== b.indexOf("userPieceId") && (a = e.findWhere({
                    id: a
                }), b = a.toJSON(), b.equipDeck.push("pieceSet"), a.set(b, {
                    silent: !0
                }))
            })
        });
        e.each(function(a) {
            var b = a.toJSON();
            b.equipDeck.filter(function(a, c) {
                return c === b.equipDeck.indexOf(a)
            });
            0 !== b.equipDeck.length &&
                (b.equipFlag = !0);
            a.set(b, {
                silent: !0
            })
        });
        c.memoriaEventSet();
        g.each(b.toJSON(), function(b) {
            var e = b.userCardId;
            d && (b.eventFlag = r(b, d));
            b.chara.description = b.chara.description.replace(/ï¼ /g, "\x3cbr\x3e");
            var m = b.createdAt;
            g.each(h.toJSON(), function(d) {
                e == d.id && (d = c.addExStatus($.extend(b, d)), d.createdAt = m, a.push(d))
            })
        });
        l.hasModel("userCardListEx") ? g.each(a, function(a, b) {
            b = l.storage.userCardListEx.findWhere({
                id: a.id
            });
            b.clear({
                silent: !0
            });
            b.set(a, {
                silent: !0
            })
        }) : l.storage.userCardListEx = new t(a)
    };
    var u = {
        BALANCE: "Balanced",
        ATTACK: "Attack",
        DEFENSE: "Defense",
        MAGIA: "Magia",
        HEAL: "Heal",
        SUPPORT: "Support",
        ULTIMATE: "Ultimate",
        CIRCLE_MAGIA: "Cycle Magia"
    };
    c.addExStatus = function(a, b, d, h) {
        a.maxRare = c.maxRank(a);
        a.maxLevel = c.getMaxLevel(a.card.rank);
        a.expRatio = c.expRatio(a);
        a.expRequire = c.expRequire(a);
        a.nextMaxLevel = c.getNextMaxLevel(a.card.rank);
        a.nextCard = c.nextCard(a);
        a.episodeLevel = c.getEpisodeLevel(a);
        a.epExpRatio = c.getEpisodeExpRatio(a);
        a.epExpRequire = c.getEpisodeExpRequire(a);
        a.charaType = u[a.chara.initialType];
        b && g.each(b, function(a) {
            c.memoriaEventCheck(a)
        });
        if (a.supportFlag) {
            a.chara.description = a.chara.description.replace(/ï¼ /g, "\x3cbr\x3e");
            a.doppelOpenFlag = !1;
            if (d)
                if (a.card.doppel) {
                    d = d.filter(function(b) {
                        return a.card.doppel.id == b.doppelId
                    });
                    var e = 5 <= Number(a.card.rank.split("_")[1]),
                        f = 5 <= a.episodeLevel,
                        k = 5 <= a.magiaLevel;
                    a.doppelOpenFlag = 0 !== d.length && e && f && k ? !0 : !1
                } else a.doppelOpenFlag = !1;
            else a.doppelOpenFlag = !1;
            a.addHp = a.hp;
            a.addAttack = a.attack;
            a.addDefense = a.defense;
            a.memoriaHp = 0;
            a.memoriaAttack =
                0;
            a.memoriaDefense = 0;
            if (a.isNpc)
                for (d = 0; 4 > d;) {
                    e = "equipPiece" + (d + 1);
                    if (b && b.length && b[d]) {
                        if (a[e] = b[d], a[e].maxLevel = q.getMaxLevel(a[e].rank, a[e].lbCount), a.addHp += a[e].hp, a.addAttack += a[e].attack, a.addDefense += a[e].defense, a.memoriaHp += a[e].hp, a.memoriaAttack += a[e].attack, a.memoriaDefense += a[e].defense, e = c.memoriaEventCheck(a[e])) a.bonusMemoriaFlag = !0, a.bonusEventId = e.eventId, a.bonusEventType = e.eventType
                    } else a[e] = null;
                    d = d + 1 | 0
                } else g.each(h, function(d, e) {
                    if (-1 !== e.indexOf("userCardId") && a.userCardId ==
                        d)
                        for (d = "userPieceId" + ("00" + e.split("userCardId")[1]).slice(-2), e = 0; 4 > e;) {
                            var f = "equipPiece" + (e + 1),
                                m = d + (e + 1);
                            if (h[m]) {
                                if (a[f] = g.findWhere(b, {
                                        id: h[m]
                                    }), a[f].maxLevel = q.getMaxLevel(a[f].rank, a[f].lbCount), a.addHp += a[f].hp, a.addAttack += a[f].attack, a.addDefense += a[f].defense, a.memoriaHp += a[f].hp, a.memoriaAttack += a[f].attack, a.memoriaDefense += a[f].defense, f = c.memoriaEventCheck(a[f])) a.bonusMemoriaFlag = !0, a.bonusEventId = f.eventId, a.bonusEventType = f.eventType
                            } else a[f] = null;
                            e = e + 1 | 0
                        }
                });
            a = c.totalEventEffectSet(a)
        } else a.chara.description =
            a.chara.description.replace(/ï¼ /g, "\x3cbr\x3e"), a = c.totalEventEffectSet(a), d = l.storage.userLive2dList, d = d.where({
                charaId: a.charaId
            }) ? d.where({
                charaId: a.charaId
            }) : [], 0 < d.length && d.sort(function(a, b) {
                return a.toJSON().live2dId < b.toJSON().live2dId ? -1 : a.toJSON().live2dId > b.toJSON().live2dId ? 1 : 0
            }), a.live2dList = [], g.each(d, function(b, c) {
                b = b.toJSON();
                a.live2dId == b.live2dId && (a.live2dIndex = c);
                c = {};
                c.live2dId = b.live2dId;
                c.description = b.live2d.description;
                c.voicePrefixNo = b.live2d.voicePrefixNo;
                a.live2dList.push(c)
            }),
            a.live2dList.sort(function(a, b) {
                return a.live2dId < b.live2dId ? -1 : a.live2dId > b.live2dId ? 1 : 0
            }), d = l.storage.userDoppelList, a.card.doppel ? d.findWhere({
                doppelId: a.card.doppel.id
            }) ? a.doppelOpenFlag = !0 : a.doppelOpenFlag = !1 : a.doppelOpenFlag = !1, a.mp && (a.mp = Math.floor(a.mp / 10) | 0, 100 < a.mp && (a.dp = a.mp - 100, a.mp = 100));
        a.customizeBonus = {
            HP: "+0%",
            ATTACK: "+0%",
            DEFENSE: "+0%",
            ACCEL: "+0%",
            BLAST: "+0%",
            CHARGE: "+0%"
        };
        for (d = 0; 6 > d;) e = a.card.cardCustomize ? a.card.cardCustomize["bonusCode" + (d + 1)] || null : null, f = a.card.cardCustomize ?
            a.card.cardCustomize["bonusNum" + (d + 1)] || null : null, a["customized" + (d + 1)] && (a.customizeBonus[e] = "+" + (f | 0) / 10 + "%"), d = d + 1 | 0;
        return a
    };
    c.maxRank = function(a) {
        var b = null;
        if (a && a.chara) {
            for (var c = 1; 5 >= c && a.chara["evolutionCard" + c]; c++) b = a.chara["evolutionCard" + c].rank, b = Number(b.split("_")[1]);
            b || (b = Number(a.card.rank.split("_")[1]))
        } else if (a) {
            for (c = 1; 5 >= c && a["evolutionCard" + c]; c++) b = a["evolutionCard" + c].rank, b = Number(b.split("_")[1]);
            b || (b = Number(a.defaultCard.rank.split("_")[1]))
        }
        return b
    };
    c.nextCard =
        function(a) {
            var b = a.chara,
                c = a.cardId;
            a.card.rank.split("RANK_");
            return b.defaultCardId === c ? b.evolutionCard1 : b.evolutionCardId1 === c ? b.evolutionCard2 : b.evolutionCardId2 === c ? b.evolutionCard3 : b.evolutionCardId3 === c ? b.evolutionCard4 : b.evolutionCardId4 === c ? b.evolutionCard5 : null
        };
    c.expRequire = function(a) {
        var b = a.level;
        return c.exArr[b] - c.exArr[b - 1] - a.experience | 0
    };
    c.expRatio = function(a) {
        var b = a.level,
            b = a.experience / (c.exArr[b] - c.exArr[b - 1]) * 100,
            b = Math.floor(b);
        a.maxLevel && a.level == a.maxLevel && (b = 100);
        b ||
            (b = 0);
        return b
    };
    c.episodeExp = [0, 1E3, 4E3, 14E3, 64E3];
    c.getEpisodeLevel = function(a) {
        var b = 0;
        g.each(c.episodeExp, function(c, h) {
            c <= a.bondsTotalPt && (b = h + 1)
        });
        return b
    };
    c.getEpisodeExpRequire = function(a) {
        var b = 0;
        g.each(c.episodeExp, function(c, h) {
            c > a.bondsTotalPt && 0 == b && (b = c - a.bondsTotalPt | 0)
        });
        return b
    };
    c.getEpisodeExpRatio = function(a) {
        var b = 100,
            d = 0;
        g.each(c.episodeExp, function(b, c) {
            b <= a.bondsTotalPt && (d = c + 1)
        });
        5 !== d && (b = (a.bondsTotalPt - c.episodeExp[d - 1]) / (c.episodeExp[d] - c.episodeExp[d - 1]) * 100 || 0, b = Math.floor(b));
        return b
    };
    c.exArr = [0, 110, 250, 430, 660, 950, 1310, 1750, 2280, 2910, 3640, 4470, 5400, 6430, 7560, 8790, 10120, 11550, 13080, 14710, 16440, 18270, 20200, 22230, 24360, 26590, 28920, 31350, 33880, 36510, 39240, 42070, 45E3, 48030, 51160, 54390, 57720, 61150, 64680, 68310, 72040, 75870, 79800, 83830, 87960, 92190, 96520, 100950, 105480, 110110, 114840, 119670, 124600, 129630, 134760, 139990, 145320, 150750, 156280, 161910, 167640, 173470, 179400, 185430, 191560, 197790, 204120, 210550, 217080, 223710, 230440, 237270, 244200, 251230, 258360, 265590, 272920, 280350, 287880, 295510,
        303240, 311070, 319E3, 327030, 335160, 343390, 351720, 360150, 368680, 377310, 386040, 394870, 403800, 412830, 421960, 431190, 440520, 449950, 459480, 469110
    ];
    c.itemExp = [100, 500, 2500];
    c.getComposeExp = function(a, b, d, h) {
        var e = 0;
        h instanceof Array ? g.each(h, function(a) {
            a = a.model.itemId || a.model.toJSON().itemId;
            var b = -1 != a.indexOf(d) || -1 != a.indexOf("ALL") ? 1.5 : 1;
            e = -1 != a.indexOf("_PP") ? e + c.itemExp[2] * b : -1 != a.indexOf("_P") ? e + c.itemExp[1] * b : e + c.itemExp[0] * b
        }) : $.each(h, function(a, b) {
            if ("length" !== a) {
                var f = -1 != a.indexOf(d) || -1 !=
                    a.indexOf("ALL") ? 1.5 : 1;
                e = -1 != a.indexOf("_PP") ? e + c.itemExp[2] * f * b : -1 != a.indexOf("_P") ? e + c.itemExp[1] * f * b : e + c.itemExp[0] * f * b
            }
        });
        return e
    };
    c.getCanUseComposeItemNum = function(a, b, d, h, e, f) {
        var k = 0;
        $.each(e, function(a, b) {
            if ("length" !== a && a !== f) {
                var d = -1 !== a.indexOf(h) || -1 !== a.indexOf("ALL") ? 1.5 : 1;
                k = -1 != a.indexOf("_PP") ? k + c.itemExp[2] * d * b : -1 != a.indexOf("_P") ? k + c.itemExp[1] * d * b : k + c.itemExp[0] * d * b
            }
        });
        a = c.exArr[a - 1] + d + k;
        b = c.exArr[b - 1];
        d = 0;
        d = -1 !== f.indexOf(h) || -1 !== f.indexOf("ALL") ? 1.5 : 1;
        d = -1 != f.indexOf("_PP") ?
            c.itemExp[2] * d : -1 != f.indexOf("_P") ? c.itemExp[1] * d : c.itemExp[0] * d;
        return Math.ceil((b - a) / d)
    };
    var v = {
            RANK_1: 1,
            RANK_2: 2,
            RANK_3: 3,
            RANK_4: 4,
            RANK_5: 5
        },
        w = {
            RANK_1: 1,
            RANK_2: 2,
            RANK_3: 3
        },
        x = {
            RANK_1: 5,
            RANK_2: 50,
            RANK_3: 400
        };
    c.getComposeCost = function(a, b, c) {
        var d = 0,
            e, f, k = v[a] || 0;
        g.each(c, function(a, c) {
            c = c.split("_")[3] || "N";
            switch (c) {
                case "PP":
                    c = "RANK_3";
                    break;
                case "P":
                    c = "RANK_2";
                    break;
                case "N":
                    c = "RANK_1"
            }
            f = x[c];
            e = w[c];
            d += Math.floor((f + (b - 1) * e) * k) * a
        });
        return d
    };
    var y = function(a) {
            switch (a) {
                case "RANK_1":
                    return 40;
                case "RANK_2":
                    return 50;
                case "RANK_3":
                    return 60;
                case "RANK_4":
                    return 80;
                case "RANK_5":
                    return 100;
                default:
                    return 1
            }
        },
        z = function(a) {
            switch (a) {
                case "RANK_1":
                    return 50;
                case "RANK_2":
                    return 60;
                case "RANK_3":
                    return 80;
                case "RANK_4":
                    return 100;
                case "RANK_5":
                    return 100;
                default:
                    return 1
            }
        };
    c.getMaxLevel = function(a) {
        return y(a)
    };
    c.getNextMaxLevel = function(a) {
        return z(a)
    };
    c.getAfterParam = function(a, b, d, h) {
        a = b.defaultCardId === a ? b.defaultCard : b.evolutionCardId1 === a ? b.evolutionCard1 : b.evolutionCardId2 === a ? b.evolutionCard2 :
            b.evolutionCardId3 === a ? b.evolutionCard3 : b.evolutionCardId4 === a ? b.evolutionCard4 : b.evolutionCard5;
        b = a.growthType;
        d = a.rank;
        var e = c.getMaxLevel(d);
        h > e && (h = e);
        e = {
            attack: a.attack,
            defense: a.defense,
            hp: a.hp
        };
        h = A(d, h);
        var f, k, g;
        switch (b) {
            case "BALANCE":
                g = k = f = 1;
                break;
            case "ATTACK":
                f = 1.03;
                k = .97;
                g = .98;
                break;
            case "DEFENSE":
                f = .98;
                k = 1.05;
                g = .97;
                break;
            case "HP":
                f = .97;
                k = .98;
                g = 1.04;
                break;
            case "ATKDEF":
                f = 1.02;
                k = 1.01;
                g = .99;
                break;
            case "ATKHP":
                f = 1.01;
                k = .99;
                g = 1.02;
                break;
            case "DEFHP":
                f = .99, k = 1.02, g = 1.01
        }
        e.attack = a.attack +
            a.attack * h * f | 0;
        e.defense = a.defense + a.defense * h * k | 0;
        e.hp = a.hp + a.hp * h * g | 0;
        return e
    };
    var A = function(a, b) {
        var c = [0, .05, .1, .15, .2, .25, .3, .35, .41, .46, .51, .56, .61, .66, .71, .76, .82, .87, .92, .97, 1.02, 1.07, 1.12, 1.17, 1.23, 1.28, 1.33, 1.38, 1.43, 1.48, 1.53, 1.58, 1.64, 1.69, 1.74, 1.79, 1.84, 1.89, 1.94, 2],
            g = [0, .04, .08, .13, .17, .22, .26, .31, .35, .4, .44, .49, .53, .58, .62, .67, .71, .76, .8, .85, .89, .94, .98, 1.03, 1.07, 1.12, 1.16, 1.21, 1.25, 1.3, 1.34, 1.39, 1.43, 1.48, 1.52, 1.57, 1.61, 1.66, 1.7, 1.75, 1.79, 1.84, 1.88, 1.93, 1.97, 2.02, 2.06, 2.11, 2.15,
                2.2
            ],
            e = [0, .04, .08, .12, .16, .2, .24, .28, .32, .36, .4, .44, .48, .52, .56, .61, .65, .69, .73, .77, .81, .85, .89, .93, .97, 1.01, 1.05, 1.09, 1.13, 1.17, 1.22, 1.26, 1.3, 1.34, 1.38, 1.42, 1.46, 1.5, 1.54, 1.58, 1.62, 1.66, 1.7, 1.74, 1.78, 1.83, 1.87, 1.91, 1.95, 1.99, 2.03, 2.07, 2.11, 2.15, 2.19, 2.23, 2.27, 2.31, 2.35, 2.4],
            f = [0, .03, .06, .09, .13, .16, .19, .23, .26, .29, .32, .36, .39, .42, .46, .49, .52, .55, .59, .62, .65, .69, .72, .75, .78, .82, .85, .88, .92, .95, .98, 1.02, 1.05, 1.08, 1.11, 1.15, 1.18, 1.21, 1.25, 1.28, 1.31, 1.34, 1.38, 1.41, 1.44, 1.48, 1.51, 1.54, 1.57, 1.61, 1.64,
                1.67, 1.71, 1.74, 1.77, 1.81, 1.84, 1.87, 1.9, 1.94, 1.97, 2, 2.04, 2.07, 2.1, 2.13, 2.17, 2.2, 2.23, 2.27, 2.3, 2.33, 2.36, 2.4, 2.43, 2.46, 2.5, 2.53, 2.56, 2.6
            ],
            k = [0, .03, .06, .09, .12, .15, .18, .21, .24, .27, .3, .33, .36, .39, .42, .45, .48, .51, .54, .57, .6, .63, .66, .69, .72, .75, .78, .81, .84, .87, .9, .93, .96, 1, 1.03, 1.06, 1.09, 1.12, 1.15, 1.18, 1.21, 1.24, 1.27, 1.3, 1.33, 1.36, 1.39, 1.42, 1.45, 1.48, 1.51, 1.54, 1.57, 1.6, 1.63, 1.66, 1.69, 1.72, 1.75, 1.78, 1.81, 1.84, 1.87, 1.9, 1.93, 1.96, 2, 2.03, 2.06, 2.09, 2.12, 2.15, 2.18, 2.21, 2.24, 2.27, 2.3, 2.33, 2.36, 2.39, 2.42, 2.45,
                2.48, 2.51, 2.54, 2.57, 2.6, 2.63, 2.66, 2.69, 2.72, 2.75, 2.78, 2.81, 2.84, 2.87, 2.9, 2.93, 2.96, 3
            ];
        switch (a) {
            case "RANK_1":
                return c[b - 1];
            case "RANK_2":
                return g[b - 1];
            case "RANK_3":
                return e[b - 1];
            case "RANK_4":
                return f[b - 1];
            case "RANK_5":
                return k[b - 1];
            default:
                return 1
        }
    };
    return c
});