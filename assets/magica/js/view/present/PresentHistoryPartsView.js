define(["underscore","backbone","backboneCommon","ajaxControl"],function(e,d,c,f){return d.View.extend({tagName:"div",className:"present commonFrame4",initialize:function(a){this.listenTo(this.parentView,"filter",this.filter);this.listenTo(this.parentView,"removeChildView",this.removeView);this.listenTo(this.model,"change",this.removeView)},render:function(){var a=this.model.toJSON(),b;"CARD"===a.presentType&&(b=c.storage.userCharaList.findWhere({charaId:(a.cardId+"").substr(0,4)|0}),b=b.toJSON().chara.defaultCard);
this.filter();this.$el.html(this.template({model:a,card:b}));return this},filter:function(){var a=this.model.toJSON();"ALL"==this.originType||this.originType==a.originType?c.removeClass(this.el,"hide"):c.addClass(this.el,"hide")},removeView:function(){this.off();this.remove()}})});