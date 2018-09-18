! function(t, e, i, a) {
    "use strict";
    var s = "imageMarker",
        n = {
            drag_disabled: !1
        };

    function r(e, i) {
        this.$element = t(e), this.settings = t.extend({}, n, i), this._defaults = n, this._name = s, this._markers = [], this.$left_box = null, this.$right_box = null, this.$drag_box = null, this.init()
    }
    t.extend(r.prototype, {
        init: function() {
            this.renderMarkup(), this.bindListeners()
        },
        renderMarkup: function() {
            var e = t('<div class="image-marker-container"></div>'),
                i = t('<div class="image-marker-container__box image-marker-container__box--left"></div>'),
                a = this.$left_box = t('<div class="image-marker-container__box__content"></div>'),
                s = t('<div class="image-marker-container__box image-marker-container__box--right"></div>'),
                n = this.$right_box = t('<div class="image-marker-container__box__content"></div>'),
                r = t('<div class="image-marker-container__box image-marker-container__box--image"></div>'),
                o = this.$drag_box = t('<div class="image-marker-container__box image-marker-container__box--drag"></div>'),
                d = t('<img class="image-marker-container__img"/>'),
                h = function(e, i) {
                    var a = i.draggable,
                        s = t(this).find(".image-marker-container__box__content"),
                        n = t.data(a[0], "marker");
                    return t(this).height() < s.height() + t(a).height() ? a.draggable("option", "revert", !0) : t(this).hasClass("image-marker-container__box--left") && 1 == n.col ? a.draggable("option", "revert", !0) : t(this).hasClass("image-marker-container__box--left") || 2 != n.col ? (n.col = t(this).hasClass("image-marker-container__box--left") ? 1 : 2, void t(a).detach().css({
                        top: 0,
                        left: 0
                    }).appendTo(s)) : a.draggable("option", "revert", !0)
                };
            i.append(a).droppable({
                accept: ".image-marker__text-box",
                drop: h
            }), s.append(n).droppable({
                accept: ".image-marker__text-box",
                drop: h
            }), d.attr("src", this.settings.src), r.append(d).append(o), e.append(i).append(s).append(r), this.$element.append(e)
        },
        bindListeners: function() {
            this.$element.on("add_marker", function(t, e) {
                this.addTextbox(e)
            }.bind(this)), this.$element.on("get_markers", function(t, e) {
                e(Array.prototype.concat.apply([], this._markers))
            }.bind(this))
        },
        addTextbox: function(e) {
            var i = t('<div class="image-marker__text-box"></div>'),
                a = t('<div class="image-marker__dot"></div>'),
                s = t('<div class="image-marker__line"></div>'),
                n = this.$left_box,
                r = function() {
                    var r = i.parent()[0] == n[0] ? i.parent().width() - 4 : 4,
                        o = i.offset().left + r,
                        d = a.offset().left + a.width() / 2,
                        h = i.offset().top + i.height() / 2,
                        l = a.offset().top + a.height() / 2,
                        c = Math.sqrt((o - d) * (o - d) + (h - l) * (h - l)),
                        _ = Math.atan2(h - l, o - d) * (180 / Math.PI);
                    _ >= 90 && _ < 180 && (h -= h - l), _ > 0 && _ < 90 && (o -= o - d, h -= h - l), _ <= 0 && _ > -90 && (o -= o - d), s.queue(function() {
                        t(this).offset({
                            top: h,
                            left: o
                        }), t(this).dequeue()
                    }).queue(function() {
                        t(this).width(c), t(this).dequeue()
                    }).queue(function() {
                        t(this).rotate(_), t(this).dequeue()
                    }), e.pos.x = parseInt(a.css("left")), e.pos.y = parseInt(a.css("top"))
                };
            var  o = t('<span class="image-marker__text-box__title" contenteditable="true">tieng_nhat</span>');
            e.tieng_nhat && o.text(e.tieng_nhat), o.on("change keydown paste input", function() {
                e.tieng_nhat = o.text()
            }), i.append(o);
            var d = t('<span class="image-marker__text-box__content" contenteditable="true">tts</span>');
            return e.tts && d.text(e.tts), d.on("change keydown paste input", function() {
                e.tts = d.text()
            }), i.append(d), e.className && (i.addClass(e.className), a.addClass(e.className), s.addClass(e.className)), 1 == e.col ? this.mountTo(this.$left_box, i, a, s, r, e) : 2 == e.col ? this.mountTo(this.$right_box, i, a, s, r, e) : this.mountTo(this.$left_box, i, a, s, r, e) ? e.col = 1 : this.mountTo(this.$right_box, i, a, s, r, e) ? e.col = 2 : void 0
        },
        mountTo: function(e, i, a, s, n, r) {
            if (i.css({
                    visibility: "hidden"
                }), e.append(i), e.height() > e.parent().height()) return i.remove(), !1;
            this.settings.drag_disabled || t('<div class="image-marker__text-box__close-btn">X</div>').on("click", function() {
                var t = this._markers.indexOf(r);
                this._markers.splice(t, 1), i.remove(), a.remove(), s.remove(), this.$element.trigger("drag_all"), this.$element.trigger("drag_all")
            }.bind(this));
            return i.css({
                visibility: "visible"
            }), r.pos || (r.pos = {
                x: i.parent()[0] == this.$left_box[0] ? 0 : this.$drag_box.width() - 20,
                y: i.offset().top - i.parent().offset().top + i.height() / 2 - 10
            }), a.css({
                top: r.pos.y + "px",
                left: r.pos.x + "px"
            }), this.$drag_box.append(s).append(a), a.draggable({
                containment: "parent",
                distance: 0,
                delay: 0,
                disabled: this.settings.drag_disabled
            }, {
                drag: n
            }), this.$element.on("drag_all", n), this.settings.drag_disabled || i.draggable({
                revert: !0
            }, {
                start: function() {
                    a.css({
                        visibility: "hidden"
                    }), s.css({
                        visibility: "hidden"
                    })
                },
                stop: function() {
                    this.$element.trigger("drag_all"), this.$element.trigger("drag_all"), a.css({
                        visibility: "visible"
                    }), s.css({
                        visibility: "visible"
                    })
                }.bind(this)
            }), t.data(i[0], "marker", r), n(), n(), this._markers.push(r), !0
        }
    }), t.fn[s] = function(e) {
        return this.each(function() {
            t.data(this, "plugin_" + s) || t.data(this, "plugin_" + s, new r(this, e))
        })
    }, t.fn.rotate = function(e) {
        return t(this).css({
            transform: "rotate(" + e + "deg)"
        }), t(this)
    }
}(jQuery, window, document);