define("underscore backbone backboneCommon ajaxControl command text!template/chara/CharaCompose.html text!css/chara/CharaCompose.css text!css/chara/CharaCommon.css cardUtil CharaCommon".split(" "), function(f, r, a, u, l, F, G, H, k, e) {
    var B = null,
        p = r.Model.extend(),
        C, c, K = r.View.extend({
            events: function() {
                var b = {};
                b[a.cgti + " #mainBtn"] = this.mainFunc;
                b[a.cgti + " #resetBtn"] = this.resetFunc;
                return b
            },
            initialize: function(a) {
                this.useItemObj = {};
                this.useItemSelectNum = 0;
                this.previewLvMaxFlag = !1;
                this.template = f.template(F);
                this.createDom()
            },
            render: function() {
                this.$el.html(this.template(u.getPageJson()));
                return this
            },
            createDom: function() {
                a.content.prepend(this.render().el);
                v.prototype.template = f.template($("#useItemControllerTemp").text());
                this.createView()
            },
            createView: function() {
                w.prototype.template = f.template($("#ItemTemp").text());
                w.prototype.parentView = this;
                I();
                a.setGlobalView();
                a.ready.hide()
            },
            mainFunc: function(b) {
                b.preventDefault();
                if (!a.isScrolled())
                    if (b = e.charaDataView.model.toJSON(), b.level == b.maxLevel) new a.PopupClass({
                        title: "Can't Enhance",
                        content: "Max Lvl. reached.",
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
                        a.removeClass(e.charaDataView.el, "popupOpen");
                        a.removeClass(e.curtainView.el, "show")
                    }), a.addClass(e.charaDataView.el, "popupOpen"), a.addClass(e.curtainView.el, "show");
                    else if (0 === c.useItemSelectNum) new a.PopupClass({
                    title: "Can't Enhance",
                    content: "Select Materials",
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
                    a.removeClass(e.charaDataView.el, "popupOpen");
                    a.removeClass(e.curtainView.el, "show")
                }), a.addClass(e.charaDataView.el, "popupOpen"), a.addClass(e.curtainView.el, "show");
                else {
                    var d = a.storage.gameUser.toJSON().riche;
                    if (parseInt(a.doc.querySelector(".needRiche").textContent) > d) new a.PopupClass({
                        title: "Can't Enhance",
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
                        a.removeClass(e.charaDataView.el, "popupOpen");
                        a.removeClass(e.curtainView.el, "show");
                        a.removeClass(a.doc.querySelector(".needRiche"), "c_red")
                    }), a.addClass(e.charaDataView.el, "popupOpen"), a.addClass(e.curtainView.el, "show"), a.addClass(a.doc.querySelector(".needRiche"), "c_red");
                    else {
                        d = b.chara.name;
                        b.chara.title && (d += "(" + b.chara.title + ")");
                        var g = new a.PopupClass({
                            title: "Enhance",
                            content: "\x3cdiv id\x3d'useItemList'\x3e\x3c/div\x3e\x3cp class\x3d'text'\x3eAre you sure you want to\x3cbr\x3eEnhance " + d + "?\x3c/p\x3e",
                            closeBtnText: "Cancel",
                            decideBtnText: "OK",
                            param: {
                                width: "490px",
                                height: "360px",
                                top: "-webkit-calc(50% - 189px)",
                                left: "-webkit-calc(50% - 245px)"
                            },
                            popupType: "original compose",
                            popupId: "composeConfirm",
                            showCurtain: !1
                        }, null, function() {
                            console.log(c.useItemObj);
                            var b = f.template($("#useItemConfirm").text());
                            $("#useItemList").html(b({
                                useItemObj: c.useItemObj
                            }));
                            var d = 0;
                            f.each(c.useItemObj, function(a, b) {
                                d++
                            });
                            8 < d && (a.addClass(a.doc.querySelector("#useItemList .useItemScrollInner"), "scrollWrap"), a.scrollSet("useItemScrollOuter", "useItemScrollInner"));
                            $("#composeConfirm .decideBtn").on(a.cgti, function(b) {
                                b.preventDefault();
                                a.isScrolled() || (a.androidKeyStop = !0, J(), a.removeClass(a.doc.querySelector("#topWrap"), "type2"), $("#composeConfirm .decideBtn").off(), g.remove(), a.removeClass(e.charaDataView.el, "popupOpen"),
                                    a.removeClass(e.curtainView.el, "show"))
                            })
                        }, function() {
                            a.removeClass(e.charaDataView.el, "popupOpen");
                            a.removeClass(e.curtainView.el, "show")
                        });
                        a.addClass(e.charaDataView.el, "popupOpen");
                        a.addClass(e.curtainView.el, "show")
                    }
                }
            },
            resetFunc: function(b) {
                b.preventDefault();
                a.isScrolled() || (c.useItemObj = {}, c.useItemSelectNum = 0, y(), c.trigger("itemSelectReset"), a.removeClass(a.doc.querySelector("#topWrap"), "type2"), a.addClass(a.doc.querySelector("#lv .arrow"), "hide"), a.addClass(a.doc.querySelector("#lv .after"),
                    "hide"))
            },
            itemWrapUpdate: function() {
                var b = "." + e.charaDataView.model.toJSON().card.attributeId.toLowerCase() + "Wrap";
                f.each(this.el.querySelectorAll(".itemWrapInner .wrap"), function(b, g) {
                    b.classList.contains("allWrap") || a.removeClass(b, "bonusIcon")
                });
                a.addClass(this.el.querySelector(b), "bonusIcon");
                e.charaDataView && (e.charaDataView.lvMaxFlag ? a.addClass(a.doc.querySelector("#itemWrap"), "selectMax") : this.previewLvMaxFlag ? a.addClass(a.doc.querySelector("#itemWrap"), "selectMax") : a.removeClass(a.doc.querySelector("#itemWrap"),
                    "selectMax"));
                0 < this.useItemSelectNum ? a.removeClass(a.doc.querySelector("#mainBtn"), "off") : a.addClass(a.doc.querySelector("#mainBtn"), "off")
            },
            needRicheUpdate: function() {
                var b = e.charaDataView.model.toJSON(),
                    b = k.getComposeCost(b.card.rank, b.level, c.useItemObj);
                a.doc.querySelector(".needRiche").textContent = b
            }
        }),
        L = {
            1: "1",
            "1.5": "2",
            2: "3"
        },
        J = function() {
            a.tapBlock(!0);
            var b = {};
            b.userCardId = e.charaDataView.model.toJSON().id;
            b.useItem = c.useItemObj;
            u.ajaxPost(a.linkList.userCardCompose, b, function(b) {
                a.responseSetStorage(b);
                var g = Number(L[b.composeEffect]) || 1;
                c.useItemObj = {};
                c.useItemSelectNum = 0;
                c.trigger("itemSelectReset");
                c.itemWrapUpdate();
                var d = e.charaDataView.model.toJSON(),
                    t = b.userCardList[0],
                    f = b.userCharaList ? b.userCharaList[0] : a.storage.userCharaList.findWhere({
                        userCardId: d.id
                    }).toJSON(),
                    t = k.addExStatus($.extend(t, f));
                e.richeView.model.set(b);
                a.doc.querySelector(".needRiche").textContent = "0";
                var f = d.level,
                    m = t.level,
                    n = M(f, m, d.experience + k.exArr[f - 1], t.experience + k.exArr[m - 1]),
                    h = a.doc.querySelector(".expGaugeInner"),
                    q = a.doc.querySelector("#afterLv");
                l.startSe(1007);
                $(h).on("transitionend", function(a) {
                    n.lvDef--;
                    0 <= n.lvDef ? ($(q).trigger("lvUp"), setTimeout(function() {
                        h.style.transitionDuration = "0s";
                        h.style.width = 0;
                        $(h).trigger("gaugeReset")
                    }, 30)) : $(h).trigger("resultAnimeComp")
                });
                $(q).on("lvUp", function(b) {
                    a.removeClass(a.doc.querySelector("#sdChara .lvUpTxt"), "show");
                    setTimeout(function() {
                        a.addClass(a.doc.querySelector("#sdChara .lvUpTxt"), "show")
                    }, 20);
                    q.innerText = parseInt(q.innerText) + 1
                });
                $(h).on("gaugeReset",
                    function() {
                        l.startSe(1007);
                        setTimeout(function() {
                            h.style.transitionDuration = n.duration;
                            n.lvDef ? h.style.width = "100%" : n.resultRatio ? h.style.width = n.resultRatio + "%" : $(h).trigger("resultAnimeComp")
                        }, 30)
                    });
                $(h).on("resultAnimeComp", function() {
                    $(q).off();
                    $(h).off();
                    setTimeout(function() {
                        var c = t;
                        e.charaDataView.model.set(c);
                        a.storage.userCardListEx.findWhere({
                            id: c.id
                        }).set(c);
                        a.addClass(a.doc.querySelector("#afterLv"), "c_gold");
                        a.doc.querySelector(".hasRiche").textContent = b.gameUser.riche;
                        l.stopComposeEffect();
                        e.playComposeResultEffect(g);
                        setTimeout(function() {
                            a.tapBlock(!1);
                            if (d.level == c.level) a.androidKeyStop = !1;
                            else {
                                var b = {
                                    type: "level"
                                };
                                b.before = d;
                                b.after = c;
                                b = new e.CharaResultView({
                                    model: new p(b)
                                });
                                $("#overlapContainer").append(b.render().el);
                                e.charaListView.cardSort.multiSort();
                                l.getBaseData(a.getNativeObj());
                                a.tapBlock(!1)
                            }
                        }, 1500)
                    }, 750)
                });
                $("#tapBlock").on(a.cgti, function() {
                    $(h).trigger("resultAnimeComp");
                    h.style.transitionDuration = "0s";
                    h.style.width = n.resultRatio + "%";
                    q.innerText = m
                });
                q.textContent =
                    f;
                a.doc.querySelector(".expGaugeInner2").style.width = "0%";
                setTimeout(function() {
                    h.style.transitionDuration = n.duration;
                    h.style.width = n.lvDef ? "100%" : n.resultRatio + "%";
                    e.playComposeEffect()
                }, 100)
            })
        },
        v = r.View.extend({
            initialize: function() {
                this.listenTo(c, "removeView", this.removeView)
            },
            checkUseItemNum: function() {
                var b = e.charaDataView.model.toJSON(),
                    d = b.level,
                    g = b.maxLevel,
                    x = b.experience,
                    f = b.chara.attributeId,
                    l = c.useItemObj,
                    m = a.doc.querySelector("#useComposeItem .item").id;
                console.log("charaData", b);
                return k.getCanUseComposeItemNum(d, g, x, f, l, m)
            },
            events: function() {
                var b = {};
                b[a.cgti + " .plusBtn"] = this.itemSetFunc;
                b[a.cgti + " .minusBtn"] = this.itemSetFunc;
                b[a.cgti + " .maxBtn"] = this.itemSetFunc;
                b["input #useItemSlider"] = this.sliderFunc;
                return b
            },
            sliderFunc: function(b) {
                console.log(b.currentTarget.value);
                this.itemView.itemSelectFunc(null, b.currentTarget.value - this.itemView.selectNum);
                a.doc.querySelector("#useComposeItem .selectNum").innerText = this.itemView.selectNum;
                this.checkController()
            },
            render: function() {
                this.$el.html(this.template());
                var a = this.itemView.model.toJSON().quantity,
                    d = this.checkUseItemNum();
                this.canUseItemNum = a < d ? a : d;
                this.checkController();
                a = this.el.querySelector("#useItemSlider");
                a.max = this.canUseItemNum;
                a.value = this.itemView.selectNum;
                return this
            },
            checkController: function() {
                console.log(this.canUseItemNum);
                0 < this.itemView.selectNum ? a.removeClass(this.el.querySelector(".minusBtn"), "off") : a.addClass(this.el.querySelector(".minusBtn"), "off");
                this.itemView.selectNum === this.canUseItemNum || c.previewLvMaxFlag ? (a.addClass(this.el.querySelector(".plusBtn"),
                    "off"), a.addClass(this.el.querySelector(".maxBtn"), "off")) : (a.removeClass(this.el.querySelector(".plusBtn"), "off"), a.removeClass(this.el.querySelector(".maxBtn"), "off"))
            },
            itemSetFunc: function(b) {
                b.preventDefault();
                if (!a.isScrolled() && !b.currentTarget.classList.contains("off")) {
                    var d = this.itemView;
                    switch (b.currentTarget.dataset.type) {
                        case "plus":
                            this.itemView.itemSelectFunc(null, 1);
                            console.log("plus");
                            break;
                        case "minus":
                            this.itemView.itemSelectFunc(null, -1);
                            console.log("minus");
                            break;
                        case "max":
                            this.itemView.itemSelectFunc(null,
                                this.canUseItemNum - this.itemView.selectNum), console.log("max")
                    }
                    a.doc.querySelector("#useItemSlider").value = d.selectNum;
                    a.doc.querySelector("#useComposeItem .selectNum").innerText = d.selectNum;
                    this.checkController()
                }
            },
            removeView: function() {
                this.off();
                this.remove()
            }
        }),
        D = ["N", "P", "PP"],
        D = ["N", "P", "PP"],
        w = r.View.extend({
            className: function() {
                console.log(this.model);
                var a = this.model.toJSON().itemAtt.toLowerCase() + "Wrap";
                "ALL" == this.model.toJSON().itemAtt && (a += " bonusIcon");
                return "wrap flexBox " + a
            },
            initialize: function() {
                this.listenTo(this.parentView,
                    "removeView", this.removeView);
                this.createView()
            },
            render: function() {
                this.$el.html(this.template({
                    model: this.model.toJSON()
                }));
                this.el.appendChild(this.itemPartsNode);
                return this
            },
            createView: function() {
                var b = this.model.toJSON();
                z.prototype.parentView = this;
                z.prototype.template = f.template($("#ItemPartsTemp").text());
                var d = a.doc.createDocumentFragment();
                f.each(D, function(a, c) {
                    console.log();
                    b[a] || (b[a] = new p({
                        itemRank: a,
                        itemId: "COMPOSE_ITEM_" + b.itemAtt + ("N" === a ? "" : "_" + a),
                        quantity: 0
                    }));
                    b[a].set({
                        itemRank: a
                    }, {
                        silent: !0
                    });
                    a = new z({
                        model: b[a]
                    });
                    d.appendChild(a.render().el)
                });
                this.itemPartsNode = d
            },
            removeView: function() {
                this.off();
                this.remove()
            }
        }),
        A, z = r.View.extend({
            id: function() {
                return this.model.toJSON().itemId
            },
            className: function() {
                var a = "item";
                0 === this.model.get("quantity") && (a += " off");
                return a
            },
            attributes: function() {
                return {
                    "data-itemrank": this.model.toJSON().itemRank
                }
            },
            events: function() {
                var b = {};
                b[a.cgti] = this.itemSelectFunc;
                b.touchstart = this.itemPopTimerStart;
                return b
            },
            initialize: function() {
                this.selectNum =
                    0;
                this.listenTo(this.model, "change", this.render);
                this.listenTo(this.parentView.parentView, "removeView", this.removeView);
                this.listenTo(this.parentView.parentView, "itemSelectReset", this.itemNumReset)
            },
            render: function() {
                this.$el.html(this.template({
                    model: this.model.toJSON()
                }));
                this.el.className = this.className();
                return this
            },
            itemPopTimerStart: function(b) {
                if (!(b.currentTarget.classList.contains("off") || c.previewLvMaxFlag && "0" === b.currentTarget.querySelector(".selectNum").innerText)) {
                    var d = this;
                    A = setTimeout(function() {
                        a.isScrolled() ||
                            (console.log(d.el), new a.PopupClass({
                                title: "Select the Amount of Gems",
                                content: "",
                                decideBtnText: "Select",
                                param: {
                                    width: "656px",
                                    height: "406px",
                                    bottom: "-webkit-calc(50% - 171px)",
                                    left: "-webkit-calc(50% - 245px)"
                                },
                                popupType: "original",
                                popupId: "useComposeItem",
                                showCurtain: !1,
                                canClose: !1
                            }, null, function() {
                                l.startSe(1002);
                                a.doc.querySelector("#useComposeItem .popupTextArea").appendChild(d.el.cloneNode(!0));
                                v.prototype.itemView = null;
                                v.prototype.itemView = d;
                                d.itemControllerView = new v;
                                a.doc.querySelector("#useComposeItem .popupTextArea").appendChild(d.itemControllerView.render().el);
                                $("#useComposeItem .decideBtn").on(a.cgti, function(b) {
                                    b.preventDefault();
                                    a.isScrolled() || a.g_popup_instance.popupView.close()
                                })
                            }, function() {
                                d.itemControllerView.removeView();
                                delete d.itemControllerView;
                                a.removeClass(e.charaDataView.el, "popupOpen");
                                a.removeClass(e.curtainView.el, "show")
                            }), a.addClass(e.charaDataView.el, "popupOpen"), a.addClass(e.curtainView.el, "show"))
                    }, 800)
                }
            },
            itemSelectFunc: function(b, d) {
                clearTimeout(A);
                if (b && (b.preventDefault(), a.isScrolled() || a.g_popup_instance || b.currentTarget.classList.contains("off"))) return;
                var g = this.model.toJSON();
                b = this.el;
                if (g.item && !e.charaDataView.lvMaxFlag) {
                    b.getElementsByClassName("selectNum");
                    var g = g.itemId,
                        x = Number(this.el.querySelector(".hasNum span").innerText);
                    if (void 0 !== d) c.useItemSelectNum -= this.selectNum, this.selectNum += d, c.useItemSelectNum += this.selectNum, c.useItemObj[g] = this.selectNum, 0 == this.selectNum && delete c.useItemObj[g], 0 < this.selectNum ? a.addClass(b, "show") : a.removeClass(b, "show");
                    else if (!c.previewLvMaxFlag && this.selectNum < x) l.startSe(1002), c.useItemSelectNum +=
                        1, this.selectNum += 1, c.useItemObj[g] = this.selectNum, 1 == this.selectNum && a.addClass(b, "show");
                    else return;
                    y();
                    this.itemNumDispUpdate();
                    0 < c.useItemSelectNum ? a.addClass(a.doc.querySelector("#topWrap"), "type2") : a.removeClass(a.doc.querySelector("#topWrap"), "type2")
                }
            },
            itemNumReset: function() {
                this.selectNum = 0;
                var b = this.el.getElementsByClassName("selectNum")[0];
                b && (a.removeClass(b.parentNode, "show"), b.innerText = "0");
                b = this.model.toJSON().itemId;
                delete c.useItemObj[b]
            },
            itemNumDispUpdate: function() {
                this.el.getElementsByClassName("selectNum")[0].innerText =
                    this.selectNum
            },
            removeView: function() {
                this.itemControllerView && this.itemControllerView.removeView();
                this.off();
                this.remove()
            }
        }),
        I = function() {
            var b = N(C.userItemList);
            console.log("composeItemObj", b);
            var d = a.doc.createDocumentFragment();
            f.each(E, function(a) {
                a = new w({
                    model: new p(b[a])
                });
                d.appendChild(a.render().el)
            });
            a.doc.querySelector(".itemWrapInner").appendChild(d)
        },
        E = "FIRE WATER TIMBER LIGHT DARK ALL".split(" "),
        N = function(b) {
            var d = {};
            a.storage.userItemList.each(function(a, b) {
                var c = a.toJSON();
                "COMPOSE" ==
                (c.item ? c.item.itemType : "") && (b = c.itemId.split("_")[2], "object" !== typeof d[b] && (d[b] = {}, d[b].itemAtt = b), c = c.itemId.split("_")[3] || "N", d[b][c] = a)
            });
            console.log(a.storage.userItemList.findWhere({
                itemId: "COMPOSE_ITEM_FIRE"
            }));
            f.each(E, function(b) {
                d[b] || (d[b] = {}, d[b].itemAtt = b, d[b].N = a.storage.userItemList.findWhere({
                        itemId: "COMPOSE_ITEM_" + b
                    }) || new p({
                        itemId: "COMPOSE_ITEM_" + b,
                        quantity: 0
                    }), d[b].P = a.storage.userItemList.findWhere({
                        itemId: "COMPOSE_ITEM_" + b + "_P"
                    }) || new p({
                        itemId: "COMPOSE_ITEM_" + b + "_P",
                        quantity: 0
                    }),
                    d[b].PP = a.storage.userItemList.findWhere({
                        itemId: "COMPOSE_ITEM_" + b + "_PP"
                    }) || new p({
                        itemId: "COMPOSE_ITEM_" + b + "_PP",
                        quantity: 0
                    }))
            });
            return d
        },
        y = function() {
            var b = e.charaDataView.model.toJSON(),
                d = b.card.attributeId,
                g = b.card.rank,
                f = b.level,
                l = b.maxLevel,
                p = c.useItemObj;
            if (0 === c.useItemSelectNum) a.addClass(a.doc.querySelector("#lv .arrow"), "hide"), a.addClass(a.doc.querySelector("#lv .after"), "hide"), c.needRicheUpdate(), c.previewLvMaxFlag = !1, c.itemWrapUpdate(), a.doc.querySelector(".expGaugeInner2").style.width =
                "0%";
            else {
                c.itemWrapUpdate();
                a.removeClass(a.doc.querySelector("#lv .arrow"), "hide");
                a.removeClass(a.doc.querySelector("#lv .after"), "hide");
                for (var m = b.experience + k.exArr[f - 1], d = k.getComposeExp(g, f, d, p), m = m + d, g = d = f; g <= l - 1;) {
                    if (k.exArr[g] < m) d = g + 1;
                    else break;
                    g = g + 1 | 0
                }
                c.previewLvMaxFlag = b.maxLevel == d ? !0 : !1;
                c.itemWrapUpdate();
                $("#afterLv").text(d);
                c.needRicheUpdate();
                b = (m - k.exArr[f - 1]) / (k.exArr[f] - k.exArr[f - 1]) * 100;
                100 <= b && (b = 100);
                a.doc.querySelector(".expGaugeInner2").style.width = b + "%"
            }
        },
        M = function(a,
            d, c, e) {
            c = {};
            c.lvDef = d - a;
            c.resultRatio = Math.floor((e - k.exArr[d - 1]) / (k.exArr[d] - k.exArr[d - 1]) * 100);
            c.duration = (c.lvDef ? 1.8 / c.lvDef : 1.8) + "s";
            return c
        };
    return {
        needModelIdObj: [{
            id: "user"
        }, {
            id: "gameUser"
        }, {
            id: "itemList"
        }, {
            id: "userItemList"
        }, {
            id: "userStatusList"
        }, {
            id: "userCharaList"
        }, {
            id: "userCardList"
        }, {
            id: "userDeckList"
        }, {
            id: "userDoppelList"
        }, {
            id: "userLive2dList"
        }, {
            id: "userPieceList"
        }, {
            id: "userPieceSetList"
        }, {
            id: "userChapterList"
        }, {
            id: "userSectionList"
        }, {
            id: "userQuestBattleList"
        }],
        charaSelect: function(b) {
            e.charaSelect(b);
            b = e.charaDataView.model.toJSON().card.miniCharaNo;
            e.showMiniChara(b);
            c.useItemObj = {};
            c.useItemSelectNum = 0;
            a.doc.querySelector("#topWrap") && a.removeClass(a.doc.querySelector("#topWrap"), "type2");
            y();
            c.trigger("itemSelectReset")
        },
        fetch: function(a) {
            B = a ? a : null;
            u.pageModelGet(this.needModelIdObj)
        },
        init: function() {
            a.setStyle(G + H);
            C = u.getPageJson();
            k.createCardList();
            c = new K;
            e.charaViewInit(B);
            c.itemWrapUpdate();
            a.scrollSet("itemViewWrap", "itemWrapInner");
            a.removeClass(a.doc.querySelector("#richeWrap"),
                "hide");
            a.tapBlock(!1);
            var b = e.charaDataView.model.toJSON().card.miniCharaNo;
            e.showMiniChara(b)
        },
        startCommand: function() {},
        remove: function(b) {
            clearTimeout(A);
            a.addClass(a.doc.querySelector("#lv .arrow"), "hide");
            a.addClass(a.doc.querySelector("#lv .after"), "hide");
            a.doc.querySelector(".expGaugeInner2").style.width = "0%";
            e.charaViewRemove();
            c && (c.trigger("removeView"), c.remove());
            b()
        },
        charaCommon: function() {
            return e
        }
    }
});