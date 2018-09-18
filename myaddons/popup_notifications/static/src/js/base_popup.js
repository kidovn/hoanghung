openerp.popup_notifications = function(instance) {
    var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;

instance.web.WebClient = instance.web.WebClient.include({

    check_popup_notifications: function () {
        var self = this;
        this.rpc('/popup_notifications/notify')
        .done(
            function (notifications) {
                _.each(notifications,  function(notif) {
                    setTimeout(function() {
                        if ($('.o_notification p#p_id').filter(function () {
                            return $(this).html() == notif.id;
                        }).length) {
                            return;
                        } // prevent displaying same notifications
                        notif.title = QWeb.render('popup_title', {'title': notif.title, 'id': notif.id});
                        notif.message += QWeb.render('popup_footer');
                        if(self.notification_manager) {
                            notif_elem = self.notification_manager.notify(notif.title, notif.message, true);
                            notif_elem.$el.find(".link2showed").on('click',function() {
                                notif_elem.destroy(true);
                                self.rpc("/popup_notifications/notify_ack", {'notif_id': notif.id});
                            });
                        }

                    }, 1000); // #TODO check original module
                });
            }
        )
        .fail(function (err, ev) {
            if (err.code === -32098) {
                // Prevent the CrashManager to display an error
                // in case of an xhr error not due to a server error
                ev.preventDefault();
            }
        });
    },

    start: function (parent) {
        var self = this;
        self._super(parent);
        // console.log('qweqwe');
        $(document).ready(function () {
            self.check_popup_notifications();
            setInterval( function() {
                // console.log('Working!');
                self.check_popup_notifications();
            }, 300 * 1000);
        });
    },

})};
