# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import babel.dates
import collections
from datetime import datetime, timedelta
from dateutil import parser
from dateutil import rrule
from dateutil.relativedelta import relativedelta
import logging
from operator import itemgetter
import pytz
import re
import time
import uuid

from odoo import api, fields, models
from odoo import tools
from odoo.tools.translate import _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError


_logger = logging.getLogger(__name__)


def is_calendar_id(record_id):
    return len(str(record_id).split('-')) != 1

class Event(models.Model):
    _name = 'hh.event'
    _description = "Event"

    name = fields.Char('Meeting Subject', required=True, states={'done': [('readonly', True)]})

    state = fields.Selection([('draft', 'Unconfirmed'), ('open', 'Confirmed')], string='Status', readonly=True,
                             track_visibility='onchange', default='draft')

    alarm_ids = fields.Many2many('hh.alarm', 'hh_alarm_hh_event_rel', string='Reminders',
                                 ondelete="restrict", copy=False)

    start = fields.Datetime('Start', required=True, help="Start date of an event, without time for full days events")

    stop = fields.Datetime('Stop', required=True, help="Stop date of an event, without time for full days events")

    start_datetime = fields.Datetime('Start DateTime', compute='_compute_dates', inverse='_inverse_dates', store=True,
                                     states={'done': [('readonly', True)]}, track_visibility='onchange')

    stop_datetime = fields.Datetime('End Datetime', compute='_compute_dates', inverse='_inverse_dates', store=True,
                                    states={'done': [('readonly', True)]},
                                    track_visibility='onchange')  # old date_deadline
    active = fields.Boolean('Active', default=True,
                            help="If the active field is set to false, it will allow you to hide the event alarm information without removing it.")

    duration = fields.Float('Duration', states={'done': [('readonly', True)]},default=0.01)

    description = fields.Char('Nội dung')

    action = fields.Char('Action detail')

    action_id = fields.Integer('Action ID')


    @api.multi
    @api.depends('start', 'stop')
    def _compute_dates(self):
        """ Adapt the value of start_date(time)/stop_date(time) according to start/stop fields and allday. Also, compute
            the duration for not allday meeting ; otherwise the duration is set to zero, since the meeting last all the day.
        """
        for meeting in self:
            meeting.start_date = False
            meeting.start_datetime = meeting.start
            meeting.stop_date = False
            meeting.stop_datetime = meeting.stop

    @api.multi
    def _inverse_dates(self):
        for meeting in self:
            meeting.start = meeting.start_datetime
            meeting.stop = meeting.stop_datetime

    @api.model
    def _default_partners(self):
        """ When active_model is res.partner, the current partners should be attendees """
        partners = self.env.user.partner_id
        active_id = self._context.get('active_id')
        if self._context.get('active_model') == 'res.partner' and active_id:
            if active_id not in partners.ids:
                partners |= self.env['res.partner'].browse(active_id)
        return partners

    partner_ids = fields.Many2many('res.partner', 'hh_event_res_partner_rel', string='Attendees',
                                   states={'done': [('readonly', True)]}, default=_default_partners)

    display_time = fields.Char('Event Time', compute='_compute_display_time')

    @api.multi
    def _compute_display_time(self):
        for meeting in self:
            meeting.display_time = self._get_display_time(meeting.start, False)

    # @api.multi
    # @api.depends('start_datetime')
    # def _compute_display_start(self):
    #     for meeting in self:
    #         meeting.display_start = meeting.start_datetime

    @api.onchange('start_datetime', 'duration')
    def _onchange_duration(self):
        if self.start_datetime:
            start = fields.Datetime.from_string(self.start_datetime)
            self.start = self.start_datetime
            self.stop = fields.Datetime.to_string(start + timedelta(hours=self.duration))

    @api.model
    def _get_display_time(self, start,  zallday):
        """ Return date and time (from to from) based on duration with timezone in string. Eg :
                1) if user add duration for 2 hours, return : August-23-2013 at (04-30 To 06-30) (Europe/Brussels)
                2) if event all day ,return : AllDay, July-31-2013
        """
        timezone = self._context.get('tz')
        if not timezone:
            timezone = self.env.user.partner_id.tz or 'UTC'
        timezone = tools.ustr(timezone).encode('utf-8')  # make safe for str{p,f}time()

        # get date/time format according to context
        format_date, format_time = self.with_context(tz=timezone)._get_date_formats()

        # convert date and time into user timezone
        date = fields.Datetime.context_timestamp(self.with_context(tz=timezone), fields.Datetime.from_string(start))

        # convert into string the date and time, using user formats
        date_str = date.strftime(format_date).decode('utf-8')
        time_str = date.strftime(format_time).decode('utf-8')

        if zallday:
            display_time = _("AllDay , %s") % (date_str)
        else:

            display_time = _(u"%s lúc %s ") % (
                date_str,
                time_str,
            )

        return display_time

    @api.model
    def _get_date_formats(self):
        """ get current date and time format, according to the context lang
            :return: a tuple with (format date, format time)
        """
        lang = self._context.get("lang")
        lang_params = {}
        if lang:
            record_lang = self.env['res.lang'].search([("code", "=", lang)], limit=1)
            lang_params = {
                'date_format': record_lang.date_format,
                'time_format': record_lang.time_format
            }

        # formats will be used for str{f,p}time() which do not support unicode in Python 2, coerce to str
        format_date = lang_params.get("date_format", '%B-%d-%Y').encode('utf-8')
        format_time = lang_params.get("time_format", '%I-%M %p').encode('utf-8')
        return (format_date, format_time)

    def _get_duration(self, start, stop):
        """ Get the duration value between the 2 given dates. """
        if start and stop:
            diff = fields.Datetime.from_string(stop) - fields.Datetime.from_string(start)
            if diff:
                duration = float(diff.days) * 24 + (float(diff.seconds) / 3600)
                return round(duration, 2)
            return 0.0

    @api.multi
    def write(self, values):
        # compute duration, only if start and stop are modified
        if not 'duration' in values and 'start' in values and 'stop' in values:
            values['duration'] = self._get_duration(values['start'], values['stop'])
        # process events one by one
        for meeting in self:
            # special write of complex IDS
            new_ids = []

            real_ids = [int(meeting.id)]

            # new_meetings = self.browse(new_ids)
            real_meetings = self.browse(real_ids)
            all_meetings = real_meetings
            super(Event, real_meetings).write(values)


            # attendees_create = False
            # if values.get('partner_ids', False):
            #     attendees_create = all_meetings.with_context(
            #         dont_notify=True).create_attendees()  # to prevent multiple notify_next_alarm

            # Notify attendees if there is an alarm on the modified event, or if there was an alarm
            # that has just been removed, as it might have changed their next event notification
            if not self._context.get('dont_notify'):
                if len(meeting.alarm_ids) > 0 or values.get('alarm_ids'):
                    partners_to_notify = meeting.partner_ids.ids
                    self.env['hh.alarm_manager'].notify_next_alarm(partners_to_notify)

        return True

    @api.model
    def create(self, values):
        if not 'user_id' in values:  # Else bug with quick_create when we are filter on an other user
            values['user_id'] = self.env.user.id

        # compute duration, if not given
        if not 'duration' in values:
            values['duration'] = self._get_duration(values['start'], values['stop'])

        meeting = super(Event, self).create(values)


        # Notify attendees if there is an alarm on the created event, as it might have changed their
        # next event notification
        if not self._context.get('dont_notify'):
            if len(meeting.alarm_ids) > 0:
                self.env['hh.alarm_manager'].notify_next_alarm(meeting.partner_ids.ids)
        return meeting

    @api.multi
    def unlink(self, can_be_deleted=True):
        # Get concerned attendees to notify them if there is an alarm on the unlinked events,
        # as it might have changed their next event notification
        events = self.search([('id', 'in', self.ids), ('alarm_ids', '!=', False)])
        partner_ids = events.mapped('partner_ids').ids

        records_to_exclude = self.env['hh.event']
        records_to_unlink = self.env['hh.event']

        for meeting in self:
            if can_be_deleted:  # if  ID REAL
                records_to_unlink |= self.browse(int(meeting.id))
            else:
                records_to_exclude |= meeting

        result = False
        if records_to_unlink:
            result = super(Event, records_to_unlink).unlink()
        if records_to_exclude:
            result = records_to_exclude.with_context(dont_notify=True).write({'active': False})

        # Notify the concerned attendees (must be done after removing the events)
        self.env['hh.alarm_manager'].notify_next_alarm(partner_ids)
        return result

class AlarmManager(models.AbstractModel):

    _name = 'hh.alarm_manager'

    def get_next_potential_limit_alarm(self, alarm_type, seconds=None, partner_id=None):
        result = {}
        delta_request = """
            SELECT
                rel.hh_event_id, max(alarm.duration_minutes) AS max_delta,min(alarm.duration_minutes) AS min_delta
            FROM
                hh_alarm_hh_event_rel AS rel
            LEFT JOIN hh_alarm AS alarm ON alarm.id = rel.hh_alarm_id
            WHERE alarm.type = %s
            GROUP BY rel.hh_event_id
        """
        base_request = """
                    SELECT
                        cal.id,
                        cal.start - interval '1' minute  * calcul_delta.max_delta AS first_alarm,
                        cal.stop - interval '1' minute  * calcul_delta.min_delta as last_alarm,
                        cal.start as first_event_date,
                        cal.stop as last_event_date,
                        calcul_delta.min_delta,
                        calcul_delta.max_delta
                    FROM
                        hh_event AS cal
                    RIGHT JOIN calcul_delta ON calcul_delta.hh_event_id = cal.id
             """

        filter_user = """
                RIGHT JOIN hh_event_res_partner_rel AS part_rel ON part_rel.hh_event_id = cal.id
                    AND part_rel.res_partner_id = %s
        """

        # Add filter on alarm type
        tuple_params = (alarm_type,)

        # Add filter on partner_id
        if partner_id:
            base_request += filter_user
            tuple_params += (partner_id, )

        # Upper bound on first_alarm of requested events
        first_alarm_max_value = ""
        if seconds is None:
            # first alarm in the future + 3 minutes if there is one, now otherwise
            first_alarm_max_value = """
                COALESCE((SELECT MIN(cal.start - interval '1' minute  * calcul_delta.max_delta)
                FROM hh_event cal
                RIGHT JOIN calcul_delta ON calcul_delta.hh_event_id = cal.id
                WHERE cal.start - interval '1' minute  * calcul_delta.max_delta > now() at time zone 'utc'
            ) + interval '3' minute, now() at time zone 'utc')"""
        else:
            # now + given seconds
            first_alarm_max_value = "(now() at time zone 'utc' + interval '%s' second )"
            tuple_params += (seconds,)

        self._cr.execute("""
                    WITH calcul_delta AS (%s)
                    SELECT *
                        FROM ( %s WHERE cal.active = True ) AS ALL_EVENTS
                       WHERE ALL_EVENTS.first_alarm < %s
                         AND ALL_EVENTS.last_event_date > (now() at time zone 'utc')
                   """ % (delta_request, base_request, first_alarm_max_value), tuple_params)

        for event_id, first_alarm, last_alarm, first_meeting, last_meeting, min_duration, max_duration in self._cr.fetchall():
            result[event_id] = {
                'event_id': event_id,
                'first_alarm': first_alarm,
                'last_alarm': last_alarm,
                'first_meeting': first_meeting,
                'last_meeting': last_meeting,
                'min_duration': min_duration,
                'max_duration': max_duration
                # ,
                # 'rrule': rule
            }

        return result

    @api.model
    def get_next_notif(self):
        partner = self.env.user.partner_id
        all_notif = []

        if not partner:
            return []

        all_meetings = self.get_next_potential_limit_alarm('notification', partner_id=partner.id)
        time_limit = 3600 * 24  # return alarms of the next 24 hours
        for event_id in all_meetings:
            max_delta = all_meetings[event_id]['max_duration']
            meeting = self.env['hh.event'].browse(event_id)
            # if meeting.recurrency:
            #     b_found = False
            #     last_found = False
            #     for one_date in meeting._get_recurrent_date_by_event():
            #         in_date_format = one_date.replace(tzinfo=None)
            #         last_found = self.do_check_alarm_for_one_date(in_date_format, meeting, max_delta, time_limit,
            #                                                       'notification', after=partner.calendar_last_notif_ack)
            #         if last_found:
            #             for alert in last_found:
            #                 all_notif.append(self.do_notif_reminder(alert))
            #             if not b_found:  # if it's the first alarm for this recurrent event
            #                 b_found = True
            #         if b_found and not last_found:  # if the precedent event had alarm but not this one, we can stop the search fot this event
            #             break
            # else:
            in_date_format = fields.Datetime.from_string(meeting.start)
            last_found = self.do_check_alarm_for_one_date(in_date_format, meeting, max_delta, time_limit,
                                                          'notification', after= partner.alarm_last_notif_ack
                                                                            )
            if last_found:
                for alert in last_found:
                    all_notif.append(self.do_notif_reminder(alert))
        return all_notif

    def do_notif_reminder(self, alert):
        alarm = self.env['hh.alarm'].browse(alert['alarm_id'])
        meeting = self.env['hh.event'].browse(alert['event_id'])

        if alarm.type == 'notification':
            message = '%s\n%s'%(meeting.display_time,meeting.description)

            delta = alert['notify_at'] - datetime.now()
            delta = delta.seconds + delta.days * 3600 * 24

            return {
                'event_id': meeting.id,
                'title': meeting.name,
                'message': message,
                'action':meeting.action,
                'action_id':meeting.action_id,
                'timer': delta,
                'notify_at': fields.Datetime.to_string(alert['notify_at']),
            }

    def notify_next_alarm(self, partner_ids):
        """ Sends through the bus the next alarm of given partners """
        notifications = []
        users = self.env['res.users'].search([('partner_id', 'in', tuple(partner_ids))])
        for user in users:
            notif = self.sudo(user.id).get_next_notif()
            notifications.append([(self._cr.dbname, 'hh.alarm', user.partner_id.id), notif])
        if len(notifications) > 0:
            self.env['bus.bus'].sendmany(notifications)

    def do_check_alarm_for_one_date(self, one_date, event, event_maxdelta, in_the_next_X_seconds, alarm_type, after=False, missing=False):
        """ Search for some alarms in the interval of time determined by some parameters (after, in_the_next_X_seconds, ...)
            :param one_date: date of the event to check (not the same that in the event browse if recurrent)
            :param event: Event browse record
            :param event_maxdelta: biggest duration from alarms for this event
            :param in_the_next_X_seconds: looking in the future (in seconds)
            :param after: if not False: will return alert if after this date (date as string - todo: change in master)
            :param missing: if not False: will return alert even if we are too late
            :param notif: Looking for type notification
            :param mail: looking for type email
        """
        result = []
        # TODO: remove event_maxdelta and if using it
        if one_date - timedelta(minutes=(missing and 0 or event_maxdelta)) < datetime.now() + timedelta(seconds=in_the_next_X_seconds):  # if an alarm is possible for this date
            for alarm in event.alarm_ids:
                if alarm.type == alarm_type and \
                    one_date - timedelta(minutes=(missing and 0 or alarm.duration_minutes)) < datetime.now() + timedelta(seconds=in_the_next_X_seconds) and \
                        (not after or one_date - timedelta(minutes=alarm.duration_minutes) > fields.Datetime.from_string(after)):
                        alert = {
                            'alarm_id': alarm.id,
                            'event_id': event.id,
                            'notify_at': one_date - timedelta(minutes=alarm.duration_minutes),
                        }
                        result.append(alert)
        return result

class Alarm(models.Model):
    _name = 'hh.alarm'
    _description = 'Event alarm'

    @api.depends('interval', 'duration')
    def _compute_duration_minutes(self):
        for alarm in self:
            if alarm.interval == "minutes":
                alarm.duration_minutes = alarm.duration
            elif alarm.interval == "hours":
                alarm.duration_minutes = alarm.duration * 60
            elif alarm.interval == "days":
                alarm.duration_minutes = alarm.duration * 60 * 24
            else:
                alarm.duration_minutes = 0

    _interval_selection = {'minutes': 'Minute(s)', 'hours': 'Hour(s)', 'days': 'Day(s)'}

    name = fields.Char('Name', required=True)
    type = fields.Selection([('notification', 'Notification'), ('email', 'Email')], 'Type', required=True, default='email')
    duration = fields.Integer('Amount', required=True, default=1)
    interval = fields.Selection(list(_interval_selection.iteritems()), 'Unit', required=True, default='hours')
    duration_minutes = fields.Integer('Duration in minutes', compute='_compute_duration_minutes', store=True, help="Duration in minutes")

    @api.onchange('duration', 'interval')
    def _onchange_duration_interval(self):
        display_interval = self._interval_selection.get(self.interval, '')
        self.name = str(self.duration) + ' ' + display_interval

    # def _update_cron(self):
    #     try:
    #         cron = self.env['ir.model.data'].sudo().get_object('calendar', 'ir_cron_scheduler_alarm')
    #     except ValueError:
    #         return False
    #     return cron.toggle(model=self._name, domain=[('type', '=', 'email')])

    @api.model
    def create(self, values):
        result = super(Alarm, self).create(values)
        # self._update_cron()
        return result

    @api.multi
    def write(self, values):
        result = super(Alarm, self).write(values)
        # self._update_cron()
        return result

    @api.multi
    def unlink(self):
        result = super(Alarm, self).unlink()
        # self._update_cron()
        return result