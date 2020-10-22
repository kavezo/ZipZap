define("underscore backbone backboneCommon ajaxControl command TutorialUtil text!template/top/TopPage.html text!template/etc/RulePopup.html text!template/etc/GameStartPopup.html text!css/top/Top.css".split(" "), function(k, p, a, f, b, C, u, v, w, x) {
    var l, g, q = !1,
        r = !1,
        A = function() {
            y();
            var c = function() {
                    $("#configCallback").on("configCallback", function(b, c) {
                        $("#configCallback").off();
                        a.noticeAp = 1 === c.ap ? !0 : !1
                    });
                    b.noticeApConfig("configCallback");
                    "TopPage" !== a.location ? b.setWebView() : ($("#commandDiv").on("saveDataCallback",
                        function(c, d) {
                            $("#commandDiv").off();
                            d ? (a.resumeData = d, a.responseSetStorage(d), z(d), a.questHelperId = d.userQuestBattleResultList[0].helpUserId, d.userQuestBattleResultList[0].questBattle.questBattleType && "HARD" == d.userQuestBattleResultList[0].questBattle.questBattleType && (a.mainQuestMode = "HARD"), location.href = "#/QuestBackground") : ($("#commandDiv").on("nativeCallback", function(a, c) {
                                $("#commandDiv").off();
                                n();
                                b.noticeRegist()
                            }), b.startTop())
                        }), b.checkQuestStored())
                },
                d = function() {
                    $("#commandDiv").on("nativeCallback",
                        function(b, d) {
                            $("#commandDiv").off();
                            a.nativeDownload = !1;
                            c()
                        })
                };
            a.nativeDownload = !0;
            if (162 < (window.app_ver.split(".").join("") | 0)) {
                var e = 0;
                $("#configCallback").on("configCallback", function(m, h) {
                    $("#configCallback").off();
                    e = h.movie ? h.movie : 0;
                    $("#commandDiv").on("nativeCallback", function(m, D) {
                        $("#commandDiv").off();
                        0 !== e ? (d(), b.downloadFile("movie", {
                            isVisibleCancel: !0,
                            description: !0,
                            note: !0
                        })) : (a.nativeDownload = !1, c())
                    });
                    b.downloadFile("common");
                    b.awakePurchase()
                });
                b.getDownloadConfig("configCallback")
            } else d(),
                b.downloadFile("common"), b.awakePurchase()
        },
        n = function() {
            g = f.getPageJson();
            a.setStyle(x);
            console.log("common.tutorialId", a.tutorialId);
            console.log("common.tutorialUtil", a.tutorialUtil);
            k.has(g.user, "id") || f.ajaxPost(a.linkList.createUser, null, function(c) {
                p.Model.extend({});
                a.responseSetStorage(c);
                var d = {};
                k.each("Sun Mon Tue Wed Thu Fri Sat".split(" "), function(a, b) {
                    d[a] = {};
                    d[a].isEnable = 1;
                    d[a].hour = 12;
                    d[a].min = 0
                });
                b.noticeSetWeekly(d);
                b.noticeApFullTurnOn();
                a.noticeAp = !0;
                b.noticeTurnOn({
                    tag1: 0,
                    tag2: 0,
                    tag3: 0
                })
            });
            b.setWebView();
            l = new B;
            a.globalMenuView && a.globalMenuView.removeView()
        },
        B = p.View.extend({
            events: function() {
                var b = {};
                b[a.cgti + " #touchScreen"] = this.touchScreen;
                b[a.cgti + " #clearBtn"] = this.cacheClear;
                b[a.cgti + " #opMovieBtn"] = this.opMovie;
                b[a.cgti + " #transferBtn"] = this.transferPop;
                b[a.cgti + " #terms"] = this.rulePopup;
                return b
            },
            initialize: function(a) {
                this.template = k.template(u);
                this.createDom()
            },
            render: function() {
                window.isDebug && k.findWhere(g.eventList, {
                    eventType: "AJ2018"
                }) && (g.aj2018 = !0);
                this.$el.html(this.template({
                    model: g
                }));
                return this
            },
            touchScreen: function(b) {
                b.preventDefault();
                a.isScrolled() || ("undefined" !== typeof g.gameUser ? "TU997" !== a.storage.user.get("tutorialId") && "TU999" !== a.storage.user.get("tutorialId") ? (a.tapBlock(!0), require(["js/util/TutorialUtil.js"], function(b) {
                    a.tutorialUtil = b;
                    a.tutorialId = a.tutorialUtil.getResumeId();
                    b.tutorialResume()
                })) : ($(a.ready.target).on("webkitAnimationEnd", function() {
                    $(a.ready.target).off();
                    $(a.ready.target).on("webkitAnimationEnd", function(b) {
                        "readyFadeOut" == b.originalEvent.animationName &&
                            (a.ready.target.className = "")
                    });
                    a.tutorialUtil = null;
                    a.tutorialId = null;
                    location.href = "#/MyPage"
                }), a.addClass(a.ready.target, "gameStartFadeIn")) : t())
            },
            cacheClear: function(c) {
                c && c.preventDefault();
                a.isScrolled() || q || (b.clearWebCache(!0), new a.PopupClass({
                    title: "Cache Clear",
                    content: "Cache has been cleared.",
                    closeBtnText: "Close"
                }), q = !0)
            },
            opMovie: function(c) {
                c && c.preventDefault();
                a.isScrolled() || (b.changeBg("web_black.jpg"), b.stopVoice(), a.androidKeyStop = !0, $(a.ready.target).on("webkitAnimationEnd", function() {
                    $(a.ready.target).off();
                    $(a.ready.target).on("webkitAnimationEnd", function(b) {
                        "readyFadeOut" == b.originalEvent.animationName && (a.ready.target.className = "")
                    });
                    b.endTop();
                    setTimeout(function() {
                            b.setWebView(!1);
                            a.ready.show();
                            b.stopBgm();
                            $("#commandDiv").on("nativeCallback", function(c, e) {
                                $("#commandDiv").off();
                                a.ready.target.className = "";
                                b.startTop();
                                $("#commandDiv").on("nativeCallback", function(c, d) {
                                    $("#commandDiv").off();
                                    a.androidKeyStop = !1;
                                    b.setWebView();
                                    a.ready.hide()
                                })
                            });
                            b.playMovie("resource/movie/other/op_movie.usm")
                        },
                        500)
                }), a.addClass(a.ready.target, "preNativeFadeIn"))
            },
            createDom: function() {
                a.content.append(this.render().el);
                a.doc.querySelector("#app_ver span").textContent = window.app_ver;
                a.ready.hide()
            },
            transferPop: function() {
                if (!a.isScrolled()) {
                    var b, d, e = this,
                        m = function() {
                            e.transferPop()
                        },
                        h = !1,
                        f = function(c) {
                            c.preventDefault();
                            a.isScrolled() || h || (h = !0, e.transferSubmit(b, d))
                        };
                    new a.PopupClass({
                        title: "Transfer Data",
                        content: a.doc.getElementById("transferInner").innerText,
                        popupType: "typeE",
                        exClass: "transferPop",
                        closeBtnText: "Cancel",
                        decideBtnText: "Transfer"
                    });
                    a.nativeKeyBoard("transferId", 15, 1);
                    a.nativeKeyBoard("transferPassword", 15, 1);
                    a.doc.getElementById("popupArea").getElementsByClassName("decideBtn")[0].addEventListener(a.cgti, function(c) {
                        c.preventDefault();
                        a.isScrolled() || (b = a.doc.getElementById("transferPopup").getElementsByClassName("personalId")[0].value, d = a.doc.getElementById("transferPopup").getElementsByClassName("password")[0].value, 8 > d.length || 15 < d.length ? new a.PopupClass({
                            title: "Transfer Data",
                            content: "Passwords must be 8-15 characters.",
                            popupType: "typeC",
                            closeBtnText: "OK"
                        }, null, null, m) : (new a.PopupClass({
                            title: "Transfer Data",
                            content: "Are you sure you wish to replace the existing data on this device with the transferred data?",
                            popupType: "typeE",
                            closeBtnText: "Cancel",
                            decideBtnText: "Transfer",
                            exClass: "transferCheck"
                        }, null, null, m), a.doc.getElementById("popupArea").getElementsByClassName("decideBtn")[0].addEventListener(a.cgti, f)))
                    }, !1)
                }
            },
            transferSubmit: function(c, d) {
                f.ajaxPost(a.linkList.userTransfer, {
                    personalId: c,
                    password: d
                }, function(c) {
                    "error" !== c.resultCode && new a.PopupClass({
                        title: "Transfer Data",
                        content: "Data has been transferred.",
                        closeBtnText: "Close",
                        popupType: "typeC"
                    }, null, null, function() {
                        b.endTop();
                        b.nativeReload("#/TopPage")
                    })
                })
            },
            rulePopup: function(c, d) {
                c.preventDefault();
                a.isScrolled() || (c = null, d && (c = function() {
                    t()
                }), new a.PopupClass({
                    title: "Terms of Use",
                    content: v,
                    popupType: "typeB"
                }, null, function() {
                    a.doc.getElementById("rulePolicyLink") && a.doc.getElementById("rulePolicyLink").addEventListener(a.cgti,
                        function(c) {
                            c.preventDefault();
                            a.isScrolled() || a.isDoubleTouch() || b.browserOpen("http://www.aniplex.co.jp/eng/privacy.html")
                        })
                }, c), a.scrollSet("rulesBase", "rulesPop"))
            }
        }),
        t = function() {
            function c() {
                function c(c) {
                    function d() {
                        var c = function(c) {
                                b.awakePurchase();
                                var d = function(c) {
                                    a.responseSetStorage(c);
                                    a.tapBlock(!0);
                                    require(["js/util/TutorialUtil.js"], function(c) {
                                        a.tutorialUtil = c;
                                        a.tutorialId = a.tutorialUtil.getResumeId();
                                        c.tutorialResume();
                                        setTimeout(function() {
                                            a.ready.target.className = "tutorialStart";
                                            b.setWebView(!0)
                                        }, 200)
                                    })
                                };
                                window.isBrowser && window.isDebug && !g.gameUser ? f.ajaxPost(a.linkList.prologueRegister, {
                                    tutorialId: "TU999"
                                }, function() {
                                    location.href = "#/MyPage"
                                }) : (d(c), localStorage.clear(), a.sfml = {})
                            },
                            d = {
                                userName: "?????"
                            };
                        r || (r = !0, f.ajaxPost(a.linkList.createGameUser, d, c))
                    }
                    c && a.responseSetStorage(c);
                    window.isBrowser ? (e && e.remove(), d()) : (e && e.remove(), $(a.ready.target).on("webkitAnimationEnd", function() {
                        b.endTop();
                        $(a.ready.target).off();
                        $(a.ready.target).on("webkitAnimationEnd", function(b) {
                            "readyFadeOut" ==
                            b.originalEvent.animationName && (a.ready.target.className = "")
                        });
                        $("#commandDiv").on("nativeCallback", function(b, c) {
                            c && "string" === typeof c && (b = {
                                tutorialId: c
                            }, "prologue" !== c ? f.ajaxPost(a.linkList.prologueRegister, b) : ($("#commandDiv").off(), d()))
                        });
                        setTimeout(function() {
                            var c = a.storage.user.get("tutorialId");
                            "OP010" === c && (c = "OP020");
                            "prologue" !== c ? b.startPrologue(c) : d();
                            b.setWebView(!1)
                        }, 500)
                    }), a.addClass(a.ready.target, "preNativeFadeIn"))
                }
                "OP000" == a.storage.user.get("tutorialId") ? f.ajaxPost(a.linkList.prologueRegister, {
                    tutorialId: "OP010"
                }, c) : c()
            }
            var d = function() {
                $(a.doc.querySelector("#rulePopupBtn")).on(a.cgti, function(a) {
                    l.rulePopup(a, !0)
                });
                $(a.doc.querySelector("#gameStartBtn")).on(a.cgti, function(b) {
                    b && b.preventDefault();
                    a.isScrolled() || ($(a.doc.querySelector("#gameStartBtn")).off(), c())
                })
            };
            if ("OP000" == a.storage.user.get("tutorialId")) var e = new a.PopupClass({
                title: "Start Game",
                content: w
            }, null, d);
            else c()
        },
        y = function() {
            var c = a.storage.user.toJSON(),
                d = a.storage.gameUser.toJSON();
            b.noticeRegist({
                tag1: c.purchaseTag,
                tag2: d.levelTag,
                tag3: d.progressTag
            })
        },
        z = function(b) {
            if (b) {
                var c = b.userQuestBattleResultList[0].questBattle;
                a.responseSetStorage(b);
                if (b = (b = a.storage.userSectionList.findWhere({
                        sectionId: c.sectionId
                    })) ? b.toJSON() : null) c = (c = a.storage.userChapterList.findWhere({
                    chapterId: b.section.genericId
                })) ? c.toJSON() : null, a.playChapter = c, a.playSection = b
            }
        };
    return {
        needModelIdObj: [{
            id: "user",
            refresh: !0
        }, {
            id: "gameUser",
            refresh: !0
        }, {
            id: "itemList"
        }, {
            id: "giftList"
        }, {
            id: "pieceList"
        }, {
            id: "userQuestAdventureList"
        }],
        fetch: function() {
            var c =
                this;
            b.setWebView(!1);
            b.stopMemoriaTop();
            b.endQuest();
            b.endArena();
            b.endL2d();
            b.hideMiniChara();
            b.popEventBranch();
            b.hideSubQuestBg();
            b.popEventSingleRaid();
            b.popEventStoryRaid();
            b.callTouchesClear();
            b.weekQuestTopUnset();
            b.stopComposeEffect();
            b.turnOffCamera();
            b.stopNormalGachaMemoria();
            b.formationPreviewRemove();
            b.enemyFormationPreviewRemove();
            b.endGachaAnimation();
            b.endPlayMovie();
            b.hideEventDungeon();
            b.hideEventRaid();
            if (window.g_sns && window.app_ver || window.isBrowser) f.pageModelGet(c.needModelIdObj);
            else {
                var d = 0,
                    e = function() {
                        d++;
                        3 < d ? (a.androidKeyStop = !0, b.setWebView(), new a.PopupClass({
                                title: "Connection error",
                                popupId: "resultCodeError",
                                content: "Please try again with a stronger connection.",
                                decideBtnText: "Reload",
                                canClose: !1
                            }, null, function() {
                                a.tapBlock(!1);
                                a.loading.hide();
                                $("#resultCodeError .decideBtn").on(a.cgti, function(a) {
                                    $("#resultCodeError .decideBtn").off();
                                    b.nativeReload("#/TopPage");
                                    window.isDebug && window.isBrowser && (location.href = "#/TopPage", location.reload())
                                })
                            })) : window.g_sns && window.app_ver ?
                            f.pageModelGet(c.needModelIdObj) : setTimeout(e, 500)
                    };
                setTimeout(e, 500)
            }
        },
        init: function() {
            g = f.getPageJson();
            var a = window.deleteAssetArr(),
                d = function() {
                    "undefined" !== typeof g.gameUser ? A() : ($("#commandDiv").on("nativeCallback", function(a, c) {
                        $("#commandDiv").off();
                        n();
                        b.noticeRegist()
                    }), b.startTop(), b.changeBg("web_black.jpg"))
                },
                e = function() {
                    $("#commandDiv").on("nativeCallback", function(c, f) {
                        $("#commandDiv").off();
                        f.isExist ? ($("#commandDiv").on("nativeCallback", function(b, c) {
                            $("#commandDiv").off();
                            a.shift();
                            0 < a.length ? e() : d()
                        }), c = 6E4 * ((new Date).getTime() / 6E4 | 0), require(["text!" + a[0].jsonFilePath + "?bust\x3d" + c], function(a) {
                            a = JSON.parse(a);
                            b.removeFile(a.list)
                        })) : (a.shift(), 0 < a.length ? e() : d())
                    });
                    b.existFile(a[0].confirmFileNames)
                };
            window.isBrowser ? n() : 0 < a.length ? e() : d()
        },
        remove: function(a) {
            l && l.remove();
            b.endTop();
            a()
        }
    }
});