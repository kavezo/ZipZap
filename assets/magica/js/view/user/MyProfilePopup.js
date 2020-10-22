define("underscore backbone backboneCommon ajaxControl cardUtil command".split(" "), function(h, r, a, k, t, p) {
    var l, e, f, m = function() {
            var c = function(b) {
                require(["text!template/user/MyProfilePopup.html"], function(g) {
                    l || (l = h.template(g));
                    console.log(b);
                    window.isLocal && (b = JSON.parse(b));
                    new a.PopupClass({
                        content: "",
                        popupType: "typeB",
                        exClass: "userProfile"
                    });
                    a.doc.createDocumentFragment();
                    g = a.doc.createElement("div");
                    f = a.storage.gameUser.toJSON();
                    var n = [];
                    for (i = 1; 7 > i; i++)
                        if (b.userDeck["userCardId" + i]) {
                            var d =
                                h.findWhere(b.userCardList, {
                                    id: b.userDeck["userCardId" + i]
                                });
                            d.attNum = b.userDeck["questPositionId" + i];
                            n.push(d)
                        } d = {};
                    d.now = a.storage.userStatusList.findWhere({
                        statusId: "BTP"
                    }).get("point");
                    d.max = a.storage.userStatusList.findWhere({
                        statusId: "MAX_BTP"
                    }).get("point");
                    var c = a.storage.userItemList.findWhere({
                            itemId: "ARENA_COIN"
                        }),
                        c = c ? c.toJSON().quantity : 0,
                        e = a.isRankingRunning(k.getPageJson().eventList);
                    g.innerHTML = l({
                        model: f,
                        profile: b,
                        support: n,
                        bp: d,
                        arenaCoin: c,
                        rankingRunning: e
                    });
                    a.doc.getElementById("popupArea").getElementsByClassName("popupTextArea")[0].appendChild(g);
                    a.doc.getElementById("myProfExp").getElementsByClassName("exInner")[0].style.width = a.doc.getElementById("exp").getElementsByClassName("gaugeInner")[0].style.width;
                    a.doc.getElementById("myProfExp").getElementsByClassName("exLeft")[0].textContent = a.doc.getElementById("exp").getElementsByClassName("pointWrap")[0].innerText;
                    a.doc.getElementById("myProfStone").innerHTML = a.doc.getElementById("money").innerHTML;
                    a.addClass(a.doc.getElementById("myProfStone").getElementsByClassName("pointWrap")[0], "pointFrame");
                    a.doc.getElementById("followImageWrap").getElementsByClassName("messageInner")[0].textContent = f.comment;
                    secondFrgmnt = null;
                    a.doc.getElementById("myProfile").getElementsByClassName("miniBtn")[0].addEventListener(a.cgti, q);
                    p.getBaseData(a.getNativeObj())
                })
            };
            window.isLocal ? require(["text!/magica/json/friend/user/1.json"], function(a) {
                c(a)
            }) : k.ajaxSimpleGet(a.linkList.followerProfile, a.storage.gameUser.toJSON().userId, c)
        },
        q = function(c) {
            c.preventDefault();
            a.isScrolled() || require(["text!template/user/MyProfilePopup2.html"],
                function(b) {
                    e || (e = h.template(b));
                    new a.PopupClass({
                        title: "Edit Comment",
                        content: "",
                        popupType: "typeC"
                    }, null, null, m);
                    a.doc.createDocumentFragment();
                    b = a.doc.createElement("div");
                    b.innerHTML = e({
                        model: f
                    });
                    a.doc.getElementById("popupArea").getElementsByClassName("popupTextArea")[0].appendChild(b);
                    a.nativeKeyBoard("commentInput", 50, 0, "textCount");
                    var c = !1;
                    a.doc.getElementById("commentDecide").addEventListener(a.cgti, function(b) {
                        b.preventDefault();
                        a.isScrolled() || c || (c = !0, b = {
                                comment: a.doc.getElementById("commentInput").value
                            },
                            k.ajaxPost(a.linkList.editComment, b, function(b) {
                                "error" !== b.resultCode && (a.responseSetStorage(b), new a.PopupClass({
                                    title: "Edit Comment",
                                    content: "Comment Edited.",
                                    closeBtnText: "OK",
                                    popupType: "typeC"
                                }, null, null, m))
                            }))
                    })
                })
        };
    return {
        instantPopup: function(a) {
            m()
        }
    }
});