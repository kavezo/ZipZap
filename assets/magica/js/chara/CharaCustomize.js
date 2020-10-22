define("underscore backbone backboneCommon ajaxControl command text!template/chara/CharaCustomize.html text!template/chara/CharaGiftParts.html text!template/chara/CharaCustomizePopup.html text!css/chara/CharaCustomize.css text!css/chara/CharaCommon.css cardUtil CharaCommon".split(" "), function(l, q, a, m, f, v, w, x, y, z, r, c) {
    var t = null,
        n, h, u = q.Model.extend({}),
        A = {
            RANK_1: 1E4,
            RANK_2: 1E5,
            RANK_3: 3E5,
            RANK_4: 1E6,
            RANK_5: "-"
        },
        B = q.View.extend({
            initialize: function(a) {
                this.giftViews = [];
                this.template = l.template(v);
                this.createDom()
            },
            events: function() {
                var b = {};
                b[a.cgti + " #mainBtn"] = this.customRunFunc;
                return b
            },
            render: function() {
                this.$el.html(this.template(m.getPageJson()));
                return this
            },
            createDom: function() {
                a.content.prepend(this.render().el);
                this.createView()
            },
            createView: function() {
                a.setGlobalView();
                a.firstNaviCheck(n);
                a.tapBlock(!1);
                a.ready.hide()
            },
            viewUpdate: function() {
                var b = c.charaDataView.model.toJSON().card.rank,
                    g = c.charaDataView.rareMaxFlag,
                    d = c.charaDataView.lvMaxFlag,
                    k = a.doc.querySelector(".descText");
                this.canEvolve && d ? (a.addClass(a.doc.querySelector("#giftWrap"), "canEvolve"), a.removeClass(a.doc.querySelector("#mainBtn"), "off"), a.removeClass(a.doc.querySelector("#richeWrap"), "hide"), a.doc.querySelector(".needRiche").textContent = A[b]) : (a.removeClass(a.doc.querySelector("#giftWrap"), "canEvolve"), a.addClass(a.doc.querySelector("#mainBtn"), "off"), a.addClass(a.doc.querySelector("#richeWrap"), "hide"), a.doc.querySelector(".needRiche").textContent = 0);
                k.textContent = this.canEvolve ? "" : "Set Material(s)";
                this.canEvolve &&
                    !d && (k.textContent = "Level Insufficient to be Awakened");
                g && (a.removeClass(a.doc.querySelector("#giftWrap"), "canEvolve"), a.addClass(a.doc.querySelector("#mainBtn"), "off"), a.addClass(a.doc.querySelector("#richeWrap"), "hide"), a.doc.querySelector(".needRiche").textContent = 0, k.textContent = "Cannot be Awakened anymore")
            },
            customRunFunc: function(b) {
                b.preventDefault();
                if (!a.isScrolled())
                    if (b = Number(a.doc.querySelector(".needRiche").textContent), Number(a.doc.querySelector(".hasRiche").textContent) < b) new a.PopupClass({
                        title: "Cannot be Awakened",
                        content: "Insufficient CC",
                        closeBtnText: "Close",
                        param: {
                            width: "490px",
                            height: "360px",
                            top: "-webkit-calc(50% - 189px)",
                            left: "-webkit-calc(50% - 245px)"
                        },
                        popupType: "original",
                        popupId: "composeConfirm",
                        showCurtain: !1
                    }, null, null, function() {
                        a.removeClass(c.charaDataView.el, "popupOpen");
                        a.removeClass(c.curtainView.el, "show");
                        a.removeClass(a.doc.querySelector(".needRiche"), "c_red")
                    }), a.addClass(c.charaDataView.el, "popupOpen"), a.addClass(c.curtainView.el, "show"), a.addClass(a.doc.querySelector(".needRiche"), "c_red");
                    else {
                        var g = c.charaDataView.model.toJSON();
                        b = g.chara.name;
                        g.chara.title && (b += "(" + g.chara.title + ")");
                        new a.PopupClass({
                            title: "Awaken",
                            content: "\x3cp\x3eAre you sure you want to \x3cbr\x3eAwaken " + b + "?\x3c/p\x3e",
                            closeBtnText: "Close",
                            decideBtnText: "OK",
                            param: {
                                width: "490px",
                                height: "360px",
                                top: "-webkit-calc(50% - 189px)",
                                left: "-webkit-calc(50% - 245px)"
                            },
                            popupType: "original",
                            popupId: "composeConfirm",
                            showCurtain: !1
                        }, null, function() {
                            $("#composeConfirm .decideBtn").on(a.cgti, function(b) {
                                b.preventDefault();
                                a.isScrolled() || (a.androidKeyStop = !0, $("#composeConfirm .decideBtn").off(), a.g_popup_instance.remove(), b = {}, b.userCardId = g.userCardId, m.ajaxPost(a.linkList.userCardEvolve, b, function(b) {
                                    a.responseSetStorage(b);
                                    var d;
                                    l.each(b.userCardList, function(a) {
                                        1 == a.level && (d = a)
                                    });
                                    var e = r.addExStatus($.extend(d, b.userCharaList[0]));
                                    n.userGiftList = a.storage.userGiftList.toJSON();
                                    var k = {
                                        evolution: b.evolution
                                    };
                                    $(a.ready.target).on("webkitAnimationEnd", function() {
                                        f.hideMiniChara();
                                        $(a.ready.target).off();
                                        $(a.ready.target).on("webkitAnimationEnd",
                                            function(b) {
                                                "readyFadeOut" == b.originalEvent.animationName && (a.ready.target.className = "")
                                            });
                                        f.changeBg("web_black.jpg");
                                        f.stopBgm();
                                        setTimeout(function() {
                                            a.removeClass(c.charaDataView.el, "popupOpen");
                                            a.removeClass(c.curtainView.el, "show");
                                            f.setWebView(!1);
                                            f.startEvolution(k)
                                        }, 500)
                                    });
                                    a.addClass(a.ready.target, "preNativeFadeIn");
                                    $("#commandDiv").on("nativeCallback", function(d) {
                                        $("#commandDiv").off();
                                        f.changeBg(a.background);
                                        f.startBgm(a.bgm);
                                        c.charaDataView.model.set(e);
                                        c.charaImgView && c.charaImgView.model.set({
                                            displayCardId: e.displayCardId
                                        });
                                        d = a.storage.userCardListEx.findWhere({
                                            id: g.id
                                        });
                                        d.clear({
                                            silent: !0
                                        });
                                        d.set(e);
                                        a.doc.querySelector(".hasRiche").textContent = b.gameUser.riche;
                                        c.showMiniChara(e.card.miniCharaNo, !1, !0);
                                        d = {
                                            type: "evolve"
                                        };
                                        d.before = g;
                                        d.after = e;
                                        d = new c.CharaResultView({
                                            model: new u(d)
                                        });
                                        $("#overlapContainer").append(d.render().el);
                                        if (h.giftViews.length) {
                                            var k = p();
                                            h.viewUpdate();
                                            l.each(h.giftViews, function(a, b) {
                                                a.model.clear({
                                                    silent: !0
                                                });
                                                a.model.set(k[b].toJSON())
                                            })
                                        }
                                        setTimeout(function() {
                                            c.charaListView.cardSort.multiSort();
                                            f.getBaseData(a.getNativeObj())
                                        }, 0);
                                        f.setWebView();
                                        a.ready.target.className = ""
                                    })
                                }))
                            })
                        }, function() {
                            a.removeClass(c.charaDataView.el, "popupOpen");
                            a.removeClass(c.curtainView.el, "show")
                        });
                        a.addClass(c.charaDataView.el, "popupOpen");
                        a.addClass(c.curtainView.el, "show");
                        b = a.doc.createElement("div");
                        b.id = "confirmCardWrap";
                        b.className = "flexBox";
                        var d = l.template(a.doc.querySelector("#evolveCharaTemp").innerText);
                        $(b).html(d(g));
                        d = a.doc.querySelector(".popupTextArea p");
                        a.doc.querySelector(".popupTextArea").insertBefore(b,
                            d);
                        f.getBaseData(a.getNativeObj())
                    }
            }
        }),
        C = q.View.extend({
            className: function() {
                var a = "giftWrap se_decide pos_" + this.model.get("target");
                return a = this.model.get("isSet") ? a + " set" : a + (this.model.get("canSet") ? " canSet" : " off")
            },
            events: function() {
                var b = {};
                b[a.cgti] = this.giftDetail;
                return b
            },
            initialize: function(a) {
                this.parentView = h;
                this.template = l.template(w);
                this.listenTo(this.model, "change", this.modelChange)
            },
            render: function() {
                this.$el.html(this.template({
                    model: this.model.toJSON(),
                    img: a.imgData
                }));
                return this
            },
            giftDetail: function(b) {
                b.preventDefault();
                if (!a.isScrolled() && (b = this.model.toJSON(), b.giftId && !b.isSet)) {
                    b.exClass = "setPopup";
                    b.popupType = "typeE";
                    var g = this;
                    b.param = {
                        width: "490px",
                        height: "360px",
                        top: "-webkit-calc(50% - 189px)",
                        left: "-webkit-calc(50% - 245px)"
                    };
                    new a.PopupClass(b, x, function() {
                        f.getBaseData(a.getNativeObj());
                        $(".setPopup .questSearchBtn").on(a.cgti, function(b) {
                            b.preventDefault();
                            a.isScrolled() || ($(".setPopup .questSearchBtn").off(), a.g_popup_instance.remove(), a.searchQuestGiftId = b.currentTarget.dataset.giftid,
                                a.charaListCustomizeSelectId = c.charaDataView.model.toJSON().id, location.href = "#/SearchQuest")
                        });
                        $(".setPopup .decideBtn").on(a.cgti, function(b) {
                            b = {};
                            b.userCardId = c.charaDataView.model.toJSON().userCardId;
                            b.target = g.model.toJSON().target;
                            a.androidKeyStop = !0;
                            a.tapBlock(!0);
                            m.ajaxPost(a.linkList.userCardCustomize, b, function(b) {
                                a.g_popup_instance && a.g_popup_instance.remove();
                                a.responseSetStorage(b);
                                b = b.userCardList[0];
                                var d = a.storage.userCharaList.findWhere({
                                        userCardId: b.id
                                    }).toJSON(),
                                    k = r.addExStatus($.extend(b,
                                        d));
                                n.userGiftList = a.storage.userGiftList.toJSON();
                                var m = g.el;
                                b = m.getElementsByClassName("effectWrap")[0];
                                a.doc.querySelector(".bonusResultWrap");
                                g.el.getElementsByClassName("bonusWrap");
                                $(b).on("webkitAnimationEnd", function() {
                                    c.charaDataView.model.set(k);
                                    var b = a.storage.userCardListEx.findWhere({
                                        id: k.id
                                    });
                                    b.clear({
                                        silent: !0
                                    });
                                    b.set(k)
                                });
                                a.addClass(b, "anim");
                                setTimeout(function() {
                                    var b = g.model.toJSON().bonusCodeDisp,
                                        d = g.model.toJSON().bonusNum;
                                    c.playCustomizeEffect(b, d);
                                    f.startSe(1121);
                                    a.addClass(m,
                                        "set");
                                    a.removeClass(m, "canSet");
                                    b = 1500;
                                    window.isBrowser && (b = 0);
                                    setTimeout(function() {
                                        if (h.giftViews.length) {
                                            var b = p();
                                            h.viewUpdate();
                                            l.each(h.giftViews, function(d, c) {
                                                d.model.clear({
                                                    silent: !0
                                                });
                                                d.model.set(b[c].toJSON());
                                                f.getBaseData(a.getNativeObj())
                                            })
                                        }
                                        a.androidKeyStop = !1;
                                        a.tapBlock(!1)
                                    }, b)
                                }, 800)
                            })
                        })
                    })
                }
            },
            modelChange: function() {
                this.render();
                this.el.className = this.className()
            }
        }),
        D = {
            HP: "HP",
            ATTACK: "ATK",
            DEFENSE: "DEF",
            ACCEL: "Accele",
            BLAST: "Blast",
            CHARGE: "Charge"
        },
        p = function() {
            for (var b = !0, g = [], d = 0,
                    k = c.charaDataView.model.toJSON(); 6 > d;) {
                var e = {};
                e.target = d + 1;
                e.isSet = k["customized" + (d + 1)] || !1;
                e.giftId = k.card.cardCustomize["giftId" + (d + 1)] || null;
                e.needNum = k.card.cardCustomize["giftNum" + (d + 1)] || 0;
                e.bonusCode = k.card.cardCustomize["bonusCode" + (d + 1)] || null;
                e.bonusNum = k.card.cardCustomize["bonusNum" + (d + 1)] / 10 || null;
                e.bonusCode && (e.bonusCodeDisp = D[e.bonusCode]);
                var f = a.storage.userGiftList.findWhere({
                        giftId: e.giftId
                    }) || a.storage.giftList.findWhere({
                        id: e.giftId
                    }),
                    f = f ? f.toJSON() : {
                        quantity: 0
                    };
                e.name = f.gift ?
                    f.gift.name : f.name;
                e.hasNum = f.quantity;
                e.hasNum = e.hasNum || 0;
                e.canSet = e.giftId ? e.hasNum < e.needNum ? !1 : !0 : !1;
                e.giftId && !e.isSet && (b = !1);
                g.push(new u(e));
                d = d + 1 | 0
            }
            h.canEvolve = b;
            return g
        },
        E = function() {
            var b = p();
            h.viewUpdate();
            var c = a.doc.createDocumentFragment();
            l.each(b, function(a, b) {
                a = new C({
                    model: a
                });
                h.giftViews.push(a);
                c.appendChild(a.render().el)
            });
            a.doc.getElementById("giftWrapInner").appendChild(c);
            f.getBaseData(a.getNativeObj())
        };
    return {
        needModelIdObj: [{
                id: "user"
            }, {
                id: "gameUser"
            }, {
                id: "itemList"
            },
            {
                id: "userItemList"
            }, {
                id: "userStatusList"
            }, {
                id: "userCardList"
            }, {
                id: "userDoppelList"
            }, {
                id: "userCharaList"
            }, {
                id: "userLive2dList"
            }, {
                id: "giftList"
            }, {
                id: "userGiftList"
            }, {
                id: "userGiftList"
            }, {
                id: "pieceList"
            }, {
                id: "userPieceList"
            }, {
                id: "userPieceSetList"
            }, {
                id: "userDeckList"
            }, {
                id: "userSectionList"
            }, {
                id: "userQuestBattleList"
            }
        ],
        fetch: function(a) {
            t = a ? a : null;
            m.pageModelGet(this.needModelIdObj)
        },
        init: function() {
            a.setStyle(y + z);
            n = m.getPageJson();
            r.createCardList();
            h = new B;
            c.charaViewInit(t);
            E();
            f.getBaseData(a.getNativeObj());
            a.tapBlock(!1);
            var b = c.charaDataView.model.toJSON().card.miniCharaNo;
            c.showMiniChara(b)
        },
        startCommand: function() {},
        charaSelect: function(b) {
            c.charaSelect(b);
            b = c.charaDataView.model.toJSON().card.miniCharaNo;
            c.showMiniChara(b);
            if (h.giftViews.length) {
                var g = p();
                h.viewUpdate();
                l.each(h.giftViews, function(a, b) {
                    a.model.clear({
                        silent: !0
                    });
                    a.model.set(g[b].toJSON())
                });
                f.getBaseData(a.getNativeObj())
            }
        },
        remove: function(b) {
            a.removeClass(a.doc.querySelector("#richeWrap"), "hide");
            a.doc.querySelector(".needRiche").textContent =
                0;
            c.charaViewRemove();
            h && (h.giftViews.length && l.each(h.giftViews, function(a, b) {
                a.remove()
            }), h.trigger("remove"), h.remove());
            b()
        },
        charaCommon: function() {
            return c
        }
    }
});