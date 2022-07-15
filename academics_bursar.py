# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.osv import fields, osv
from openerp.tools.translate import _
import datetime
from datetime import date
import time
from openerp import SUPERUSER_ID,tools,netsvc
import openerp.addons.decimal_precision as dp

PAYMENT_PLAN_OPTIONS = [
    ('least', 'at least'),
    ('equal', 'equal to'),
]

# PAYMENT_PLAN_TYPES = [
#     ('percent', 'Percentage'),
#     ('fixed', 'Fixed Amount')
# ]

PAYMENT_PLAN_LINE_TYPES = [
    ('percent', 'Percentage'),
#     ('fixed', 'Fixed Amount'),
    ('balance', 'Balance')
]

PAYMENT_PLAN_STATES = [
    ('draft', 'Draft'),
    ('submitted', 'Submitted'),
    ('approved', 'Approved'),
    ('paid', 'Paid'),
    ('rejected', 'Rejected'),
    ('cancelled', 'Cancelled')
]

PAYMENT_PLAN_DATES = [
    ('start', 'Term Start Date'),
    ('registration_start', 'Registration Start Date'),
    ('registration_end', 'Registration End Date'),
    ('clearance', 'Clearance Date')
]

class account_invoice(osv.osv):
    _inherit = 'account.invoice'
    _columns = {
            'student': fields.boolean('Student'),
            'term_id': fields.many2one('aun.registrar.term', 'Term', readonly=True, states={'draft':[('readonly',False)]}, track_visibility = "onchange"),
            'detail_id': fields.many2one('detail.code','Detail Code', readonly=True, states={'draft':[('readonly',False)]}, track_visibility = "onchange"),
            'detail_name': fields.related('detail_id', 'desc', type='char', string="Detail Code", store=True, readonly=True),
        }

account_invoice()
    
class account_voucher(osv.osv):
    _inherit = 'account.voucher'
    _columns = {
            'student': fields.boolean('Student'),
            'term_id': fields.many2one('aun.registrar.term', 'Term', readonly=True, states={'draft':[('readonly',False)]}, track_visibility = "onchange"),
        }
    
    def validate_all_payments(self, cr, uid, ids, context=None):
        uid = SUPERUSER_ID
        records =  self.search(cr,uid,[('student','=',True),('state','=','draft')],order='date ASC')
        x = 1
        for rec in records:
            print x
            r = self.browse(cr,uid,rec)
            res = self.recompute_voucher_lines(cr, uid, [r.id], r.partner_id.id, r.journal_id.id, r.amount, r.company_id.currency_id.id, r.type, r.date)
            if 'line_cr_ids' in res['value']:
                i = 0
                for a in res['value']['line_cr_ids']:
                    arr = [0,0,{}]
                    arr[2] = a
                    res['value']['line_cr_ids'][i] = tuple(arr)
                    i = i + 1
            if 'line_dr_ids' in res['value']:
                j = 0
                for a in res['value']['line_dr_ids']:
                    arr = [0,0,{}]
                    arr[2] = a
                    res['value']['line_dr_ids'][j] = tuple(arr)
                    j = j + 1
            self.write(cr, uid, r.id, res['value'])
            wf_service = netsvc.LocalService("workflow")
            wf_service.trg_validate(SUPERUSER_ID, 'account.voucher', r.id, 'proforma_voucher', cr)
            x += 1
        return True
    
    def fix_payments(self, cr, uid, ids, context=None):
        uid = SUPERUSER_ID
        array = self.pool.get('res.partner').check_balance(cr, uid, [], context=None)
        #BAN/2014/0244
#         students = ['A00010047', 'A00010152', 'A00010167', 'A00010253', 'A00010254', 'A00010331', 'A00010379', 'A00010398', 'A00010437', 'A00010441', 'A00010488', 'A00010566', 'A00010636', 'A00010638', 'A00010640', 'A00010641', 'A00010670', 'A00010682', 'A00010712', 'A00010744', 'A00010786', 'A00011140', 'A00011244', 'A00011250', 'A00011256', 'A00011257', 'A00011271', 'A00011277', 'A00011285', 'A00011307', 'A00011330', 'A00011353', 'A00011368', 'A00011375', 'A00011381', 'A00011390', 'A00011398', 'A00011431', 'A00011442', 'A00011455', 'A00011483', 'A00011490', 'A00011499', 'A00011510', 'A00011517', 'A00011548', 'A00011561', 'A00011563', 'A00011578', 'A00011595', 'A00011602', 'A00011606', 'A00011607', 'A00011624', 'A00011630', 'A00011655', 'A00011659', 'A00011672', 'A00011689', 'A00011716', 'A00011719', 'A00011737', 'A00011784', 'A00011787', 'A00011799', 'A00012000', 'A00012215', 'A00012256', 'A00012260', 'A00012325', 'A00012349', 'A00012350', 'A00012351', 'A00012393', 'A00012402', 'A00012405', 'A00012423', 'A00012435', 'A00012474', 'A00012490', 'A00012514', 'A00012517', 'A00012586', 'A00012591', 'A00012593', 'A00012615', 'A00012635', 'A00012663', 'A00012669', 'A00012719', 'A00012721', 'A00012727', 'A00012766', 'A00012789', 'A00012810', 'A00012838', 'A00012840', 'A00012855', 'A00012877', 'A00012898', 'A00012931', 'A00012987', 'A00013043', 'A00013047', 'A00013089', 'A00013090', 'A00013097', 'A00013099', 'A00013120', 'A00013131', 'A00013141', 'A00013142', 'A00013144', 'A00013152', 'A00013165', 'A00013181', 'A00013215', 'A00013235', 'A00013268', 'A00013269', 'A00013284', 'A00013288', 'A00013302', 'A00013306', 'A00013312', 'A00013325', 'A00013339', 'A00013370', 'A00013382', 'A00013451', 'A00013456', 'A00013470', 'A00013471', 'A00013480', 'A00013544', 'A00013546', 'A00013556', 'A00013561', 'A00013562', 'A00013566', 'A00013574', 'A00013577', 'A00013578', 'A00013579', 'A00013580', 'A00013615', 'A00013619', 'A00013623', 'A00013632', 'A00013634', 'A00013637', 'A00013639', 'A00013658', 'A00013669', 'A00013673', 'A00013729', 'A00013733', 'A00013735', 'A00013749', 'A00013750', 'A00013752', 'A00013762', 'A00013763', 'A00013774', 'A00013778', 'A00013783', 'A00013794', 'A00013799', 'A00013801', 'A00013805', 'A00013809', 'A00013813', 'A00013837', 'A00013844', 'A00013851', 'A00013853', 'A00013921', 'A00013926', 'A00013937', 'A00013959', 'A00013978', 'A00013980', 'A00013986', 'A00014018', 'A00014019', 'A00014020', 'A00014064', 'A00014085', 'A00014088', 'A00014103', 'A00014106', 'A00014108', 'A00014109', 'A00014116', 'A00014125', 'A00014141', 'A00014182', 'A00014186', 'A00014187', 'A00014192', 'A00014193', 'A00014201', 'A00014206', 'A00014221', 'A00014226', 'A00014230', 'A00014231', 'A00014235', 'A00014238', 'A00014239', 'A00014255', 'A00014263', 'A00014314', 'A00014338', 'A00014350', 'A00014364', 'A00014371', 'A00014434', 'A00014443', 'A00014459', 'A00014463', 'A00014511', 'A00014524', 'A00014526', 'A00014528', 'A00014537', 'A00014554', 'A00014560', 'A00014562', 'A00014567', 'A00014571', 'A00014573', 'A00014585', 'A00014609', 'A00014616', 'A00014617', 'A00014627', 'A00014631', 'A00014632', 'A00014635', 'A00014648', 'A00014658', 'A00014662', 'A00014691', 'A00014692', 'A00014694', 'A00014697', 'A00014708', 'A00014716', 'A00014728', 'A00014740', 'A00014757', 'A00014760', 'A00014763', 'A00014774', 'A00014777', 'A00014788', 'A00014790', 'A00014791', 'A00014793', 'A00014795', 'A00014799', 'A00014801', 'A00014809', 'A00014810', 'A00014818', 'A00014819', 'A00014829', 'A00014831', 'A00014832', 'A00014833', 'A00014838', 'A00014851', 'A00014860', 'A00014881', 'A00014886', 'A00014895', 'A00014900', 'A00014901', 'A00014914', 'A00014925', 'A00014926', 'A00014930', 'A00014931', 'A00014938', 'A00014943', 'A00014946', 'A00014970', 'A00014978', 'A00014986', 'A00015007', 'A00015012', 'A00015020', 'A00015045', 'A00015047', 'A00015063', 'A00015100', 'A00015115', 'A00015129', 'A00015140', 'A00015151', 'A00015152', 'A00015158', 'A00015162', 'A00015182', 'A00015198', 'A00015203', 'A00015206', 'A00015216', 'A00015220', 'A00015238', 'A00015258', 'A00015286', 'A00015340', 'A00015349', 'A00015372', 'A00015378', 'A00015387', 'A00015395', 'A00015398', 'A00015403', 'A00015407', 'A00015410', 'A00015498', 'A00015508', 'A00015523', 'A00015524', 'A00015575', 'A00015576', 'A00015591', 'A00015598', 'A00015602', 'A00015609', 'A00015636', 'A00015645', 'A00015651', 'A00015652', 'A00015653', 'A00015654', 'A00015665', 'A00015676', 'A00015689', 'A00015693', 'A00015700', 'A00015703', 'A00015707', 'A00015711', 'A00015716', 'A00015720', 'A00015724', 'A00015725', 'A00015729', 'A00015739', 'A00015750', 'A00015758', 'A00015764', 'A00015765', 'A00015774', 'A00015775', 'A00015778', 'A00015781', 'A00015796', 'A00015799', 'A00015804', 'A00015807', 'A00015815', 'A00015818', 'A00015819', 'A00015822', 'A00015830', 'A00015872', 'A00015884', 'A00015889', 'A00015896', 'A00015898', 'A00015899', 'A00015900', 'A00015901', 'A00015902', 'A00015904', 'A00015905', 'A00015906', 'A00015907', 'A00015908', 'A00015909', 'A00015910', 'A00015911', 'A00015912', 'A00015921', 'A00015922', 'A00015923', 'A00015926', 'A00015939', 'A00015942', 'A00015951', 'A00015952', 'A00015957', 'A00015965', 'A00015968', 'A00015975', 'A00015985', 'A00015986', 'A00015995', 'A00015996', 'A00015997', 'A00016001', 'A00016012', 'A00016024', 'A00016058', 'A00016060', 'A00016110', 'A00016117', 'A00016144', 'A00016177', 'A00016180', 'A00016187', 'A00016213', 'A00016236', 'A00016246', 'A00016266', 'A00016290', 'A00016302', 'A00016304', 'A00016321', 'A00016325', 'A00016327', 'A00016454', 'A00016470', 'A00016482', 'A00016483', 'A00016493', 'A00016497', 'A00016499', 'A00016518', 'A00016524', 'A00016530', 'A00016546', 'A00016547', 'A00016550', 'A00016552', 'A00016555', 'A00016556', 'A00016558', 'A00016563', 'A00016578', 'A00016591', 'A00016593', 'A00016596', 'A00016610', 'A00016615', 'A00016616', 'A00016619', 'A00016629', 'A00016636', 'A00016650', 'A00016652', 'A00016659', 'A00016660', 'A00016669', 'A00016670', 'A00016671', 'A00016673', 'A00016674', 'A00016675', 'A00016680', 'A00016681', 'A00016682', 'A00016683', 'A00016688', 'A00016690', 'A00016695', 'A00016706', 'A00016710', 'A00016714', 'A00016724', 'A00016730', 'A00016731', 'A00016732', 'A00016734', 'A00016738', 'A00016740', 'A00016741', 'A00016752', 'A00016753', 'A00016768', 'A00016772', 'A00016774', 'A00016778', 'A00016779', 'A00016782', 'A00016787', 'A00016789', 'A00016790', 'A00016793', 'A00016797', 'A00016799', 'A00016804', 'A00016808', 'A00016811', 'A00016812', 'A00016813', 'A00016817', 'A00016824', 'A00016831', 'A00016843', 'A00016859', 'A00016865', 'A00016871', 'A00016873', 'A00016880', 'A00016885', 'A00016887', 'A00016893', 'A00016895', 'A00016922', 'A00016940', 'A00016953', 'A00016978', 'A00016980', 'A00016982', 'A00016989', 'A00017004', 'A00017006', 'A00017007', 'A00017010', 'A00017011', 'A00017016', 'A00017023', 'A00017025', 'A00017037', 'A00017050', 'A00017073', 'A00017075', 'A00017095', 'A00017102', 'A00017134', 'A00017137', 'A00017145', 'A00017161', 'A00017164', 'A00017189', 'A00017191', 'A00017197', 'A00017198', 'A00017203', 'A00017229', 'A00017248', 'A00017272', 'A00017273', 'A00017287', 'A00017295', 'A00017299', 'A00017303', 'A00017314', 'A00017349', 'A00017354', 'A00017356', 'A00017357', 'A00017370', 'A00017436', 'A00017437', 'A00017463', 'A00017542', 'A00017546', 'A00017567', 'A00017583', 'A00017944', 'A00017948', 'A00017955', 'A00017957', 'A00017958', 'A00017962', 'A00017964', 'A00017965', 'A00017971', 'A00017973', 'A00017975', 'A00017983', 'A00017984', 'A00017987', 'A00017991', 'A00017997', 'A00018009', 'A00018016', 'A00018018', 'A00018023', 'A00018030', 'A00018033', 'A00018035', 'A00018043', 'A00018047', 'A00018050', 'A00018054', 'A00018063', 'A00018073', 'A00018082', 'A00018083', 'A00018097', 'A00018102', 'A00018105', 'A00018106', 'A00018107', 'A00018109', 'A00018112', 'A00018116', 'A00018119', 'A00018124', 'A00018126', 'A00018133', 'A00018134', 'A00018141', 'A00018144', 'A00018149', 'A00018152', 'A00018154', 'A00018157', 'A00018158', 'A00018159', 'A00018160', 'A00018162', 'A00018169', 'A00018171', 'A00018172', 'A00018177', 'A00018186', 'A00018192', 'A00018197', 'A00018199', 'A00018204', 'A00018211', 'A00018242', 'A00018266', 'A00018280', 'A00018288', 'A00018299', 'A00018306', 'A00018312', 'A00018355', 'A00018378', 'A00018380', 'A00018393', 'A00018426', 'A00018431', 'A00018456', 'A00018480', 'A00018481', 'A00018482', 'A00018488', 'A00018494', 'A00018496', 'A00018497', 'A00018498', 'A00018500', 'A00018523', 'A00018527', 'A00018549', 'A00018550', 'A00018551', 'A00018557', 'A00018562', 'A00018563', 'A00018575', 'A00018584', 'A00018586', 'A00018608', 'A00018614', 'A00018617', 'A00018624', 'A00018629', 'A00018645', 'A00018648', 'A00018649', 'A00018665', 'A00018678', 'A00018687', 'A00018701', 'A00018703', 'A00018706', 'A00018713', 'A00018731', 'A00018735', 'A00018753']
#         students = ['A00015924']
#         print len(students)
#         array = [13341, 967, 13355, 13360, 13363, 13412, 13414, 13429, 13431, 13434, 13437, 13473, 13487, 13493, 13538, 13556, 13569, 975, 13603, 13606, 13609, 13615, 13624, 13626, 13629, 13633, 979, 13660, 980, 13671, 13677, 982, 13683, 13685, 13702, 13708, 13710, 13716, 13719, 984, 13730, 13756, 988, 13782, 13830, 995, 13842, 997, 13861, 13868, 13889, 1993, 13897, 13907, 13914, 13916, 13917, 13924, 1000, 13933, 13967, 13977, 1004, 10948, 10946, 17347, 13013, 10960, 10945, 18018, 17948, 10992, 10973, 10984, 13984, 1007, 1983, 1008, 14010, 14011, 1011, 14018, 1012, 1013, 1014, 1017, 14049, 14058, 14069, 14070, 1024, 14110, 14114, 14116, 14123, 14129, 14141, 1031, 1032, 14150, 14160, 14172, 14181, 1041, 1046, 14214, 1050, 14242, 14243, 1052, 14245, 1054, 1055, 14250, 14251, 1056, 14253, 1990, 1062, 14268, 14270, 14271, 14272, 14287, 14296, 14300, 14303, 1071, 1072, 1074, 14310, 1075, 1076, 1077, 14321, 14347, 1101, 1106, 1108, 1110, 1111, 18026, 1119, 1124, 1127, 1135, 1136, 1141, 1144, 1145, 14424, 14428, 1149, 1154, 1169, 1176, 1177, 1179, 14455, 1186, 1190, 1197, 1202, 1203, 14472, 1209, 1215, 1217, 1229, 1249, 1250, 1251, 1252, 1257, 14501, 1260, 1262, 1269, 1273, 1276, 1281, 1282, 1285, 1289, 1290, 1291, 14522, 1294, 1297, 1299, 1300, 1313, 1314, 1317, 1318, 1321, 1326, 1329, 1337, 1343, 1347, 1350, 1355, 14557, 1372, 2240, 1378, 1379, 1380, 1381, 1386, 1391, 1393, 18130, 14569, 1394, 1397, 1398, 1400, 14576, 1403, 1412, 1413, 1921, 1416, 1420, 1421, 1422, 1964, 1424, 1430, 14588, 14590, 1436, 14593, 1437, 1441, 1443, 14603, 1445, 1448, 1451, 1453, 14614, 1458, 14615, 1460, 1465, 1468, 1471, 1472, 14623, 1474, 1477, 14626, 1478, 1480, 10943, 1482, 1483, 1484, 1485, 1486, 1488, 1489, 1493, 1496, 1499, 1504, 1507, 1508, 1509, 1510, 1512, 1513, 1514, 1515, 1517, 1518, 1519, 1520, 1522, 1525, 1526, 1527, 14656, 1528, 1529, 14660, 1530, 1531, 1533, 1534, 1535, 1537, 1538, 1539, 1541, 1543, 14667, 1545, 10987, 18025, 1546]
#         for student in students:
#             i = self.pool.get('res.partner').search(cr,uid,[('name','=',student)])
#             array.append(i[0])
        print array
        records =  self.search(cr,uid,[('student','=',True),('state','=','posted'),('partner_id','in', array[0:30])],order='date ASC')
        total = len(records)
        print "total = " + str(total)
        x = 1
        for r in records:
            print str(x) + " of " + str(total)
            self.cancel_voucher(cr, 1, [r])
            self.action_cancel_draft(cr, 1, [r])
            r = self.browse(cr,uid,r)
#             res = self.recompute_voucher_lines(cr, uid, [r.id], r.partner_id.id, r.journal_id.id, r.amount, r.company_id.currency_id.id, r.type, r.date)
#             if 'line_cr_ids' in res['value']:
#                 i = 0
#                 for a in res['value']['line_cr_ids']:
#                     arr = [0,0,{}]
#                     arr[2] = a
#                     res['value']['line_cr_ids'][i] = tuple(arr)
#                     i = i + 1
#             if 'line_dr_ids' in res['value']:
#                 j = 0
#                 for a in res['value']['line_dr_ids']:
#                     arr = [0,0,{}]
#                     arr[2] = a
#                     res['value']['line_dr_ids'][j] = tuple(arr)
#                     j = j + 1
#             self.write(cr, uid, r.id, {'line_dr_ids': [(6, 0, [])],'line_cr_ids': [(6, 0, [])]})
            wf_service = netsvc.LocalService("workflow")
            wf_service.trg_validate(SUPERUSER_ID, 'account.voucher', r.id, 'proforma_voucher', cr)
            x += 1
            
        return True
    
    
    def write(self, cr, uid, ids, vals, context=None):
        if 'state' in vals:
            state = vals['state']
        else:
            return super(account_voucher, self).write(cr, uid, ids, vals, context=context)
        account_obj = self.pool.get('student.account')
#         payment_obj = self.pool.get('term.payments')
        if state == 'posted':
            pays = self.browse(cr, uid, ids)
            for pay in pays:
                if pay.student == True and pay.type == 'receipt' and pay.amount != 0.0:
                    c_ids = account_obj.search(cr, SUPERUSER_ID, [('student_id','=',pay.partner_id.id)])
                    if not c_ids:
                        c_ids = [account_obj.create(cr, SUPERUSER_ID, {
                                                   'student_id': pay.partner_id.id,
                                                   })]
#                     name = pay.journal_id.name + " Payment"
#                     payment_obj.create(cr, uid, {
#                                                    'clearance_id': c_ids[0],
#                                                    'name': name,
#                                                    'payment': pay.amount,
#                                                    'payment_id': pay.id,
#                                                    'term_id': pay.term_id.id,
#                                                    'date': pay.date
#                                                    })
#         elif state == 'cancel':
#             for i in ids:
#                 pay = self.browse(cr, uid, i)
#                 if pay.student == True:
#                     payments = payment_obj.search(cr, uid, [('payment_id','=',i)])
#                     if payments:
#                         payment_obj.unlink(cr, uid, payments)
        return super(account_voucher, self).write(cr, uid, ids, vals, context=context)

account_voucher()

class detail_category_code(osv.osv):
    _name = 'detail.category.code'
    _columns = {
            'name': fields.char('Code', size=4, required=True),
            'desc': fields.char('Description', size=32, required=True),
            }
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'This detail code category already exists')
        ]
detail_category_code()

class detail_code(osv.osv):
    _name = 'detail.code'
    _columns = {
            'category_id': fields.many2one('detail.category.code', 'Category', track_visibility = "onchange", required=True),
            'name': fields.char('Code', size=4, required=True),
            'desc': fields.char('Description', size=32, required=True),
            'priority': fields.integer('Priority'),
            'negative': fields.boolean('Allow Negative Balance After Clearance'),
            'refund': fields.boolean('Refundable'),
            'journal_id': fields.many2one('account.journal', 'Journal', required=True, domain=[('type','=','sale')], track_visibility='onchange'),
            'debit_acc': fields.many2one('account.account', 'Debit Account',required=True, domain=[('type','in',['receivable','payable'])], help="The debit account used for this detail code."),
            'income_acc': fields.many2one('account.account', 'Credit Account',required=True, help="The income account used for this detail code."),
            'fund_acc_id': fields.many2one('account.analytic.account', 'Fund Account', required=True, track_visibility='onchange'),
            'group_ids': fields.many2many('res.groups', 'rel_detail_group', 'detail_id', 'group_id', 'Groups')
            }
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'This detail code already exists')
        ]
detail_code()

class refund_rule(osv.osv):
    _name = 'refund.rule'
    _order = 'start_date ASC'
    
    def _check_start_end_dates(self, cr, uid, ids, context=None):
        rule = self.browse(cr, uid, ids,context=context)[0]
        if rule.start_date and rule.end_date:
            return rule.end_date > rule.start_date
        return True
    
    def _check_percent(self, cr, uid, ids, context=None):
        rule = self.browse(cr, uid, ids,context=context)[0]
        return rule.percent < 1 and rule.percent > 0
    
    _columns = {
            'fee_id': fields.many2one('fee.structure', 'Fee Structure', required=True),
            'start_date': fields.date('From',required=True),
            'end_date': fields.date('To',required=True),
            'percent': fields.float('Percentage', help="Enter a number between 0 and 1", required=True)
            }
    _constraints=[
        (_check_start_end_dates, 'Please verify that the term end date is greater than the start date.',['Start Date',' End Date']),
        (_check_percent, 'Please verify that the percentage is between 0 and 1',['Percent']),
    ]
refund_rule()

class academics_fees(osv.osv):
    _name = 'academics.fees'
    _inherit = ["mail.thread"]
    _columns = {
            'detail_id': fields.many2one('detail.code', 'Detail Code', track_visibility = "onchange", required=True),
            'name': fields.related('detail_id', 'desc', type='char', string='Description', readonly=True),
            'charge': fields.float('Charge', track_visibility = "onchange", required=True),
            'comp_fee_id': fields.many2one('fee.structure', 'Fee', track_visibility = "onchange"),
            'other_fee_id': fields.many2one('fee.structure', 'Fee', track_visibility = "onchange"),
#             'rec_account_id': fields.many2one('account.account', ' Receivable Account', domain = "[('type','=', 'receivable')]", track_visibility = "onchange", help="The Receivable account used for this Payment."),
        }
    def on_change_detail_code(self, cr, uid, ids, detail_id, context=None):
        code_obj = self.pool.get('detail.code')
        code = code_obj.browse(cr,uid,detail_id,context)
        return {'value': {'name': code.desc}}
    
academics_fees()

class room_fees(osv.osv):
    _name = 'room.fees'
    _description = 'Room Fees'
    _columns = {
            'fee_id': fields.many2one('fee.structure', 'Fee', track_visibility = "onchange"),
            'detail_id': fields.many2one('detail.code', 'Detail Code', track_visibility = "onchange", required=True),
            'room_type': fields.many2one('housing.room.type', 'Room Type', required=True),
            'charge': fields.float('Charge', required=True),
#             'rec_acc': fields.many2one('account.account', ' Receivable Account', domain = "[('type','=', 'receivable')]", required=True, help="The Receivable account used for housing."),
        }

room_fees()

class housing_meal_fees(osv.osv):
    _name = 'housing.meal.fees'
    _description = 'Meal Fees'
    _columns = {
            'fee_id': fields.many2one('fee.structure', 'Fee', track_visibility = "onchange"),
            'detail_id': fields.many2one('detail.code', 'Detail Code', track_visibility = "onchange", required=True),
            'meal_type': fields.many2one('housing.meal.type', 'Meal Type', required=True),
            'number': fields.float('Number of Meals', required=True),
            'charge': fields.float('Charge', required=True),
#             'rec_acc': fields.many2one('account.account', ' Receivable Account', domain = "[('type','=', 'receivable')]", required=True, help="The Receivable account used for housing."),
        }
housing_meal_fees()

class fee_structure(osv.osv):
    _name = 'fee.structure'
    _rec_name = 'term_id'
    _description = 'Fees Configuration'
    _inherit = ["mail.thread"]
    
    def _refund_rules(self, cr, uid, ids, context=None):
        rules = self.browse(cr, uid, ids,context=context)[0].refund_rules
        counter = 1
        a = len(rules)
        while counter < a:
            first_date = datetime.datetime.strptime(rules[counter-1].end_date, tools.DEFAULT_SERVER_DATE_FORMAT)
            first_date = str(first_date + datetime.timedelta(days=1))[:10]
            next_date = rules[counter].start_date
            if first_date != next_date:
                return False
            counter +=1
        return True
    
    def _make_editable(self, cr, uid, ids, name, arg, context=None):
        res = {}
        invoice_obj = self.pool.get('account.invoice')
        for structure in self.browse(cr, SUPERUSER_ID, ids, context=None):
            res[structure.id] = True
            invs = invoice_obj.search(cr,uid,[('term_id','=',structure.term_id.id),('state','!=','draft')])
            if invs:
                res[structure.id] = False  
        return res
    
    def on_change_level_program_id(self, cr, uid, ids, level_program_id, context=None):
        res = {}
        if level_program_id:
            res = {'value': {'major_id': False}}
        return res
    
    def on_change_major_id(self, cr, uid, ids, major_id, context=None):
        res = {}
        if major_id:
            res = {'value': {'level_program_id': False}}
        return res

    def on_change_fslevel(self,cr,uid,ids,level_id, context=None):
        res = {}
        if level_id:
            res = {'value': {'level_program_id': False}}
        return res
#         program_obj = self.pool.get('aun.registrar.level')
#         if not level_id:
#             return {}
#         level_id_obj = program_obj.browse(cr, uid, level_id)
#         return {'domain':{'level_program_id':[('level_id','=',level_id_obj.id)]}}


    _columns = {
            'term_id': fields.many2one('aun.registrar.term', 'Term', required=True, track_visibility = "onchange"),
            'level_id': fields.many2one('aun.registrar.level', 'Level', required=True, track_visibility = "onchange"),
            'tuition_detail_id': fields.many2one('detail.code', 'Detail Code', required=True, track_visibility = "onchange"),
            'tuition_price': fields.float('Price', required=True, track_visibility = "onchange"),
#             'tuition_rec_acc': fields.many2one('account.account', ' Receivable Account', domain = "[('type','=', 'receivable')]", required=True, track_visibility = "onchange", help="The Receivable account used for tuition."),
            'type': fields.selection([('credit','Per Credit'),('flat','Flat Rate')],'Fee Type', required=True, track_visibility = "onchange"), 
            'comp_fees': fields.one2many('academics.fees', 'comp_fee_id', 'Mandatory Fees', track_visibility = "onchange"),
            'housing_fees': fields.one2many('room.fees', 'fee_id', 'Housing Fees'),
            'refund_rules': fields.one2many('refund.rule', 'fee_id', 'Refund Rules'),
            'meal_fees': fields.one2many('housing.meal.fees', 'fee_id', 'Meal Fees'),
            'other_fees': fields.one2many('academics.fees', 'other_fee_id', 'Optional Fees'),
            'min_balance': fields.float('Minimum Balance for Clearance', track_visibility = "onchange"),
            'edit': fields.function(_make_editable, string='Editable', type='boolean', method=True, store=False, track_visibility="onchange"),
            'level_program_id': fields.many2one('registrar.program', 'Program', track_visibility = "onchange"),
            'major_id': fields.many2one('aun.registrar.major', 'Major', track_visibility = "onchange"),

        }
    _defaults={
            'type': 'credit',
        }
    
    _constraints=[
        (_refund_rules, 'The start date of a new line must be one day after the end date of the previous line.',['Refund Rules']),
    ]

    _sql_constraints = [
        ('term_uniq', 'unique(term_id,level_id)', 'Fee Structure for this term already exists!')
        ]
    
fee_structure()

class term_clearance(osv.osv):
    _name = 'term.clearance'
    _description = 'Term Clearance'
    _inherit = ["mail.thread"]
    _order = 'term_id DESC, student_id ASC'
    
    def case_unclear(self, cr, uid, ids, context=None):
        clearance = self.browse(cr, SUPERUSER_ID, ids, context=None)[0]
        if clearance.state == 'draft':
            raise osv.except_osv(_('Invalid'), _('This student is not cleared for the semester!'))
        self.write(cr, uid, ids, {'state': 'draft', 'date_clear': False}, context=context)
        return True
        
    def _get_clearance_values(self, cr, uid, ids, name, arg, context=None):
        res = {}
        uid = SUPERUSER_ID
        enr_obj = self.pool.get('aun.registrar.enrollment')
        room_obj = self.pool.get('housing.room.students')
        for clearance in self.browse(cr, SUPERUSER_ID, ids, context=None):
            res[clearance.id] = {}
            res[clearance.id]['credit_hours'] = 0.0
            res[clearance.id]['room_type'] = False
            res[clearance.id]['meal_plan'] = False
            enrs = enr_obj.browse(cr,uid,enr_obj.search(cr,uid,[('term_id','=',clearance.term_id.id),('student_id','=',clearance.student_id.id),('state','=','registered')]))
            for enr in enrs:
                res[clearance.id]['credit_hours'] += enr.credit
            room = room_obj.browse(cr,uid,room_obj.search(cr,uid,[('term_id','=',clearance.term_id.id),('student_id','=',clearance.student_id.id),('state','not in',['reject','cancel'])]))
            if room:
                res[clearance.id]['room_type'] = room[0].room_type.id
                res[clearance.id]['meal_plan'] = room[0].meal_id.id
        return res
    
    
    
    _columns = {
            'student_id': fields.many2one('res.partner', 'Student', domain=[('student','=',True)], required=True, readonly=True),
            'term_id': fields.many2one('aun.registrar.term', 'Term', required=True, readonly=True),
            'credit_hours': fields.function(_get_clearance_values, string='Credit Hours', type='float', method=True, multi='clearance', store=False, track_visibility="onchange"),
            'room_id': fields.function(_get_clearance_values, string='Room', type='many2one', method=True, relation='housing.room.students', multi='clearance', store=False, track_visibility="onchange"),
            'room_type': fields.function(_get_clearance_values, string='Room Type', type='many2one', method=True, relation='housing.room.type', multi='clearance', store=False, track_visibility="onchange"),
            'meal_plan': fields.function(_get_clearance_values, string='Meal Type', type='many2one', method=True, relation='housing.meal.type', multi='clearance', store=False, track_visibility="onchange"),
            'fee_charge': fields.boolean('Fee Charges', readonly=True),
            'credit_limit': fields.float('Credit Limit', digits=(3,2), track_visibility="onchange"),
            'payment_plan': fields.many2one('bursar.payment.plan.form', 'Payment Plan', readonly=True),
            'state': fields.selection([('draft','Not Cleared'), ('cleared','Cleared')],'State', readonly=True, track_visibility="onchange"),
            'date_clear': fields.date('Date Cleared'),
  	    	'create_uid':fields.many2one('res.users', 'Cleared By'),#added
    }
    _defaults={
        'state': 'draft',
        }
    
term_clearance()

class student_account(osv.osv):
    _name = 'student.account'
    _description = 'Student Account'
    _inherit = ["mail.thread"]
    _order = 'student_id ASC'

    def _amount_all(self, cr, uid, ids, name, args, context=None):
        res = {}
        for clearance in self.browse(cr, SUPERUSER_ID, ids, context=context):
            res[clearance.id] = {
                'total_charge': 0.0,
                'total_payment': 0.0,
#                 'balance': 0.0,
            }
            for charge in clearance.charges:
                res[clearance.id]['total_charge'] += charge.charge
            for payment in clearance.payments:
                res[clearance.id]['total_payment'] += payment.payment
#             res[clearance.id]['balance'] = res[clearance.id]['total_charge'] - res[clearance.id]['total_payment']
            
        return res
    

    _columns = {
            'student_id': fields.many2one('res.partner', 'Student ID', readonly=True, required=True, track_visibility = "onchange"),
            'applicant': fields.boolean('Applicant', readonly=True),
            'name': fields.related('student_id', 'name', type='char', relation="res.partner", string="Student"),
            'charges': fields.one2many('term.charges','clearance_id', 'Charges'),
            'payments': fields.related('student_id','payment_ids', type='one2many', relation='account.voucher', string='Payments', readonly=True, groups="academics.group_bursary_staff,academics.group_registrar_student"),
#             'balance': fields.function(_amount_all, type = 'float', digits_compute=dp.get_precision('Account'), string='Total Balance', track_visibility='onchange', multi='all'),
            'p_balance': fields.related('student_id', 'credit', type='float', relation="res.partner", string="Balance", store=False, readonly=True, track_visibility = "onchange"),
            'fname': fields.related('student_id', 'fname', type='char', relation="res.partner", string="First Name", store=False, readonly=True),
            'lname': fields.related('student_id', 'lname', type='char', relation="res.partner", string="Last Name", store=False, readonly=True),
            'payment_plan_id': fields.many2one('bursar.payment.plan.form', 'Active Payment Plan', readonly=True, track_visibility = "onchange"),
        }

    _sql_constraints = [
        ('student_uniq', 'unique(student_id)', 'Student account already exists!')
        ]
    
    ###Added
    def _check_student_campus_hold_status(self, cr, uid, student_id,):
        match_hold_id = []
        cr.execute("SELECT distinct aun_registrar_hold.name, aun_registrar_hold_assignment.student_id, aun_registrar_hold_assignment.is_active FROM student_account, aun_registrar_hold_assignment, aun_registrar_hold, term_charges, detail_code WHERE aun_registrar_hold_assignment.student_id = student_account.student_id  AND aun_registrar_hold.id = aun_registrar_hold_assignment.hold_id AND aun_registrar_hold_assignment.is_active = 't' AND aun_registrar_hold_assignment.active = 't' AND aun_registrar_hold.campusstore = 't' AND student_account.id = term_charges.clearance_id AND term_charges.detail_id = detail_code.id AND (detail_code.id = 53 OR detail_code.id = 63 OR detail_code.id = 62) AND date(term_charges.invoice_date) = date(now()) AND student_account.id=%s", (student_id))
        for match_hold_row in cr.fetchall():
            match_hold_id.append(match_hold_row[0])
        if match_hold_id:
            return False
        else:      
            return True
    _constraints=[
        (_check_student_campus_hold_status, 'This student has a Campus Store Hold, kindly contact the Bursar', ['Student(s)'])
    ]
    
    ###End
student_account()

class term_charges(osv.osv):
    _name = 'term.charges'
    _description = 'Term Charges'
    _inherit = ["mail.thread"]
    _order = 'term_id DESC, invoice_date DESC'
    
    def on_change_detail_code(self, cr, uid, ids, detail_id, context=None):
        if not detail_id:
            return {}
        code =self.pool.get('detail.code').browse(cr, uid, detail_id)
        user = self.pool.get('res.users').browse(cr, uid, uid)
        if not self.pool.get('ir.model.access').check_groups(cr, uid, "academics.group_bursary_staff"):
            if code.group_ids and (not(set(user.groups_id) & set(code.group_ids))):
                return {'value': {'detail_id': False,'name': False}, 'warning': {'title': _('Detail Code Restriction'), 'message': _('You are not allowed to charge a student with this detail code!')}}
        return {'value': {'name': code.desc}}
    
    def on_change_term_id(self, cr, uid, ids, student_id, detail_id, term_id, context=None):
        fee_obj = self.pool.get('fee.structure')
        acad_fee_obj = self.pool.get('academics.fees')
        student = self.pool.get('res.partner').browse(cr,uid,student_id)
        price = 0.0
        fee = fee_obj.browse(cr, SUPERUSER_ID, fee_obj.search(cr, SUPERUSER_ID, [('term_id','=',term_id),('level_id','=',student.level_id.id)]))
        if fee:
            fee = fee[0]
            detail_fee = (acad_fee_obj.browse(cr, SUPERUSER_ID, acad_fee_obj.search(cr, SUPERUSER_ID, [('comp_fee_id','=',fee.id),('detail_id','=',detail_id)])) or
            acad_fee_obj.browse(cr, SUPERUSER_ID, acad_fee_obj.search(cr, SUPERUSER_ID, [('other_fee_id','=',fee.id),('detail_id','=',detail_id)])))
            if detail_fee:
                price = detail_fee[0].charge
        else:
            warning = {
                        'title': ('Invalid'),
                        'message': ('No fee structure for this term, please contact the bursar!')
                        }
            return {'warning': warning}
        return {'value': {'charge': price}}
    
    def create(self, cr, uid, vals, context=None):
        fee_obj = self.pool.get('fee.structure')
        invoice_obj = self.pool.get('account.invoice')
        code_obj = self.pool.get('detail.code')
        invoice_line_obj = self.pool.get('account.invoice.line')
        code = code_obj.browse(cr,uid,vals['detail_id'],context)
        if vals['charge'] == 0.0:
            return True
        if 'invoice_date' not in vals:
            vals['invoice_date'] = date.today()
        res = super(term_charges, self).create(cr, uid, vals, context)
        charge = self.browse(cr,uid,res,context)
        if vals['charge'] < 0:
            if uid != SUPERUSER_ID:
                if code.refund:
                    if not self.pool.get('ir.model.access').check_groups(cr, uid, "academics.group_bursary_staff"):
                        raise osv.except_osv(_('Invalid'), _('You are not allowed reverse transactions!'))
                else:
                    raise osv.except_osv(_('Invalid'), _('This detail code is not refundable'))
        else:
            fee = fee_obj.browse(cr, SUPERUSER_ID, fee_obj.search(cr, SUPERUSER_ID, [('term_id','=',charge.term_id.id),('level_id','=',charge.clearance_id.student_id.level_id.id)]))
            if (fee):
                fee = fee[0]
            else:
                raise osv.except_osv(_('No Fee Structure!'), _('There is no fee structure for this term, please contact bursar!'))
            if code.negative == False:
                clearance_obj = self.pool.get('term.clearance')
                clearance = clearance_obj.browse(cr, SUPERUSER_ID, clearance_obj.search(cr, SUPERUSER_ID, [('term_id','=',charge.term_id.id),('student_id','=',charge.clearance_id.student_id.id)]))
                if clearance and vals['charge'] > (charge.clearance_id.student_id.credit * -1):
                    if clearance[0].state == 'cleared':
                        if clearance[0].payment_plan and clearance[0].payment_plan.state != 'paid':
                            sql = "SELECT SUM(charge) FROM term_charges WHERE term_id =" + str(charge.term_id.id) + 'and clearance_id =' + str (charge.clearance_id.id)
                            cr.execute(sql)
                            total_charges = cr.fetchone()
                            if clearance[0].payment_plan.amount_due - total_charges[0] < 0.0:
                                raise osv.except_osv(_('Invalid'), _('This transaction exceeds your active payment plan allowance by ₦'+ str(-(clearance[0].payment_plan.amount_due - total_charges[0]))))
                        if clearance[0].credit_limit > 0.0:
                            sql = "SELECT SUM(charge) FROM term_charges WHERE term_id =" + str(charge.term_id.id) + 'and clearance_id =' + str (charge.clearance_id.id)
                            cr.execute(sql)
                            total_charges = cr.fetchone()
                            if (clearance[0].credit_limit - total_charges[0]) < 0.0:
                                raise osv.except_osv(_('Invalid'), _('This transaction exceeds your current credit/scholarship limit allowance by ₦'+ str(-(clearance[0].credit_limit - total_charges[0]))))
                        else:
                            raise osv.except_osv(_('Insufficient Funds'), _('You do not have enough money in your student account to complete this action.'))
                    elif clearance[0].state != 'cleared' and clearance[0].payment_plan:
                        sql = "SELECT SUM(charge) FROM term_charges WHERE term_id =" + str(charge.term_id.id) + 'and clearance_id =' + str (charge.clearance_id.id)
                        cr.execute(sql)
                        total_charges = cr.fetchone()
                        if clearance[0].payment_plan.amount_due - total_charges[0] < 0.0:
                            raise osv.except_osv(_('Invalid'), _('This transaction exceeds your active payment plan allowance by ₦'+ str(-(clearance[0].payment_plan.amount_due - total_charges[0])) + '. Please adjust your payment plan before proceeding.'))
        invoice = invoice_obj.create(cr,SUPERUSER_ID,{
                               'name': vals['name'],
                               'partner_id': charge.clearance_id.student_id.id,
                               'state': "draft",
                               'account_id': charge.detail_id.debit_acc.id,
                               'term_id': vals['term_id'],
                               'student': 1,
                               'user_id': uid,
                               'date_invoice': vals['invoice_date'],
                               'detail_id' : vals['detail_id'],
                               'journal_id': charge.detail_id.journal_id.id
                               })
        invoice_line_obj.create(cr,SUPERUSER_ID,{
                               'invoice_id': invoice,
                               'quantity': 1,
                               'account_id': charge.detail_id.income_acc.id,
                               'account_analytic_id': charge.detail_id.fund_acc_id.id,
                               'name': vals['name'],
                               'price_unit': vals['charge']
                               })
        wf_service = netsvc.LocalService("workflow")
        wf_service.trg_validate(SUPERUSER_ID, 'account.invoice', invoice, 'invoice_open', cr)
        self.write(cr, uid, res, {'invoice_id': invoice})
        return res
    
        
    def unlink(self, cr, uid, ids, context=None):
        fee_obj = self.pool.get('fee.structure')
        invoice_obj = self.pool.get('account.invoice')
        d= str(date.today())
        for charge in self.browse(cr,uid,ids):
            fee = fee_obj.browse(cr,uid,fee_obj.search(cr,uid,[('term_id','=',charge.term_id.id),('level_id','=',charge.clearance_id.student_id.level_id.id)]))[0]
            percent = 0
            if fee.refund_rules:
                rules = fee.refund_rules
                if d < rules[0].start_date:
                    percent = 1
                else:
                    for rule in rules:
                        if rule.end_date >= d and d >= rule.start_date:
                            percent = rule.percent
                            break
            else:
                percent = 1
            if percent > 0:
                ref = self.refund_student(cr, uid, [charge.id], percent, context)
                refund = self.browse(cr,uid,ref)
                refund = refund.invoice_id
                if percent == 1:
                    inv = charge.invoice_id
                    if not inv.reconciled:
                        movelines = inv.move_id.line_id
                        reconcile_obj = self.pool.get('account.move.reconcile')
                        account_m_line_obj = self.pool.get('account.move.line')
                        period = inv.period_id.id
                        to_reconcile_ids = {}
                        for line in movelines:
                            if line.account_id.id == inv.account_id.id:
                                to_reconcile_ids[line.account_id.id] = [line.id]
                            if type(line.reconcile_id) != osv.orm.browse_null:
                                reconcile_obj.unlink(cr, uid, line.reconcile_id.id)
                        for tmpline in  refund.move_id.line_id:
                            if tmpline.account_id.id == inv.account_id.id:
                                to_reconcile_ids[tmpline.account_id.id].append(tmpline.id)
                        for account in to_reconcile_ids:
                            account_m_line_obj.reconcile(cr, uid, to_reconcile_ids[account],
                                            writeoff_period_id=period,
                                            writeoff_journal_id = inv.journal_id.id,
                                            writeoff_acc_id=inv.account_id.id
                                            )
                    osv.osv.unlink(self, cr, uid, ids, context=context)
                    osv.osv.unlink(self, cr, uid, ref, context=context)
        return True
    
    def refund_student(self, cr, uid, ids, percent, context=None):
        charge = self.browse(cr,uid,ids)[0]
        refund = self.create(cr,uid,{
                               'detail_id' : charge.detail_id.id,
                               'name': charge.name + " Refund",
                               'term_id': charge.term_id.id,
                               'charge':charge.charge * percent * -1,
                               'clearance_id': charge.clearance_id.id,
                               'invoice_date': charge.invoice_date
                               })
        return refund
    
    _columns = {
            'name': fields.char('Description', required=True),
            'charge': fields.float('Charge', required=True),
            'detail_id': fields.many2one('detail.code', 'Detail Code', required=True),
            'term_id': fields.many2one('aun.registrar.term', 'Term', required=True),
            'invoice_id': fields.many2one('account.invoice', 'Invoice', ondelete="cascade"),
            'clearance_id': fields.many2one('student.account', 'Student',required=True),
            'enrollment_id': fields.many2one('aun.registrar.enrollment', 'Enrollment'),
            'meal_id': fields.many2one('housing.room.students', 'Enrollment'),
            'payment_plan_id': fields.many2one('bursar.payment.plan.form', 'Payment Plan'),
            'create_date': fields.datetime('Date', readonly=True),
            'invoice_date': fields.date('Invoice Date'),
            'system':fields.boolean('System', readonly=True)
        }
term_charges()

class bursar_payment_plan(osv.osv):
    _name = "bursar.payment.plan"
    _order = "name"
    _inherit = ["mail.thread"]
    _description = "Payment Plan"
    
    def _validate_fields(self, cr, uid, ids, context=None):
        plan = self.browse(cr, uid, ids,context=context)[0]
        surcharge = False
        equal = []
        types = []
        options = []
        down = []
        total = 0.0
        for line in plan.line_ids:
            total+= line.value
            options.append(line.options)
            types.append(line.p_type)
            if line.surcharge > 0.0:
                surcharge = True
            if line.equal:
                equal.append(line)
            if line.is_down_payment:
                down.append(line)
                
        if len(down) > 1:
            raise osv.except_osv(_('Invalid'), _('Down payment lines must not be more than one.'))
        if surcharge and not plan.surcharge_detail_id:
            raise osv.except_osv(_('Invalid'), _('Service Charge Detail Code must be set if service charge is more than 0'))
        if plan.late_payment_fee < 0:
            raise osv.except_osv(_('Invalid'), _('Late Payment Fee cannot be a negative value!'))
        if plan.late_payment_fee > 0 and not plan.late_detail_id:
            raise osv.except_osv(_('Invalid'), _('Late Payment Detail Code must be set if late payment charge is more than 0'))
        if len(equal) == 1:
            raise osv.except_osv(_('Invalid'), _('Equal Installments must be more than one'))
        if len(equal) > 1:
            i = 1
            valid = True
            while i < len(equal):
                if equal[0].p_type != equal[i].p_type:
                    valid = False
                    break
                if equal[0].options != equal[i].options:
                    valid = False
                    break
                if equal[0].value != equal[i].value:
                    valid = False
                    break
                i +=1
            if valid == False:
                raise osv.except_osv(_('Invalid'), _('Type, Option and Value on equal lines must be the same!'))
        if 'least' in options and 'balance' not in types:
            raise osv.except_osv(_('Invalid'), _("At least one installment type must be 'balance' if any payment option is 'at least'"))
        if 'least' not in options and 'balance' not in types and total != 1:
            raise osv.except_osv(_('Invalid'), _('The values of all the payment lines must be equal to 1 (100%)'))
        return True
    
    _columns = {
        'name': fields.char('Name', size=64, required=True, track_visibility = "onchange"),
        'late_detail_id': fields.many2one('detail.code', 'Detail Code', track_visibility = "onchange"),
        'late_payment_fee': fields.float('Charge', track_visibility = "onchange"),
        'active': fields.boolean('Active', track_visibility = "onchange", help="If the active field is set to False, it will allow you to hide the payment plan without removing it."),
        'note': fields.text('Description', track_visibility = "onchange",required=True), 
        'surcharge_detail_id': fields.many2one('detail.code', 'Detail Code', track_visibility = "onchange"),
        'line_ids': fields.one2many('bursar.payment.plan.line', 'payment_id', 'Installments', track_visibility = "onchange"),
    }

    _constraints=[
        (_validate_fields, 'Invalid Configuration',['Form']),
    ]
    _defaults = {
        'active': True
    }
bursar_payment_plan()

class bursar_payment_plan_line(osv.osv):
    _name = "bursar.payment.plan.line"
    _description = "Payment Plan"
    _inherit = ["mail.thread"]
    _order = 'is_down_payment DESC'
    
    def on_change_type(self, cr, uid, ids, p_type, context=None):
        if p_type == 'balance':
            return {'value': {'options': [],'value':0}}
        return True
    
    def on_change_down_payment(self, cr, uid, ids, is_down_payment, context=None):
        if is_down_payment == True:
            return {'value': {'date_from': 'clearance'}}
        return True
    
    def _validate_fields(self, cr, uid, ids, context=None):
        line = self.browse(cr, uid, ids,context=context)[0]
        if line.p_type == 'percent':
            if line.value > 1 or line.value < 0:
                raise osv.except_osv(_('Invalid'), _('Installment Percentage must be between 0 and 1, e.g 60% will be 0.60'))
        if line.surcharge > 1 or line.surcharge < 0:
            raise osv.except_osv(_('Invalid'), _('Service Charge must be between 0 and 1, e.g 60% will be 0.60'))
        return True
    
    _columns = {
        'payment_id': fields.many2one('bursar.payment.plan', 'Payment Plan', required=True, ondelete='cascade'),
        'is_down_payment': fields.boolean('Is Down Payment'),
        'days': fields.integer('Days', track_visibility="onchange"),
        'date_from': fields.selection(PAYMENT_PLAN_DATES, 'Date', track_visibility="onchange"),
        'p_type': fields.selection(PAYMENT_PLAN_LINE_TYPES, 'Type', required=True, track_visibility="onchange"),
        'options': fields.selection(PAYMENT_PLAN_OPTIONS, 'Option', track_visibility="onchange"),
        'value': fields.float('Value', track_visibility = "onchange"),
        'after': fields.char('Payment', readonly=True),
        'surcharge': fields.float('Service Charge', track_visibility = "onchange"),
        'equal': fields.boolean('Equal?', track_visibility = "onchange")
    }
    _defaults = {
        'after': ' days after '
    }
    _constraints=[
        (_validate_fields, 'Invalid Configuration',['Form']),
    ]
bursar_payment_plan_line()

class bursar_payment_plan_form(osv.osv):
    _name = "bursar.payment.plan.form"
    _inherit = ["mail.thread", 'ir.needaction_mixin']
    _description = "Payment Plan Application"
    
    def _needaction_domain_get (self, cr, uid, context=None):
        if self.pool.get('ir.model.access').check_groups(cr, uid, "academics.group_bursar"):
            return [('state','=','submitted')]
        return False
    
    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        reads = self.browse(cr, uid, ids, context=context)
        res = []
        for record in reads:
            name = record.student_id.name + '-' + record.payment_id.name + '-' + record.term_id.name_get()[0][1]
            res.append((record['id'], name))
        return res
    
    def create(self, cr, uid, vals, context=None):
        dup = self.search(cr,uid,[('student_id','=',vals['student_id']),('term_id','=',vals['term_id']),('state','not in',['cancelled','rejected'])])
        if (dup):
            raise osv.except_osv(_('Invalid'), _('You cannot have multiple payment plans in one term'))
        vals['state'] = 'submitted'
        res = super(bursar_payment_plan_form, self).create(cr, uid, vals, context)
        group = self.pool.get('ir.model.data').get_object(cr, uid, 'academics', 'group_bursar')
        group = cr.execute("select uid from res_groups_users_rel WHERE gid=(%s)" %group.id)
        s = cr.fetchall()
        group = []
        for a in s:
            group.append(a[0])
        student = self.pool.get('res.partner').browse(cr,uid,[vals['student_id']])[0]
        if student.user_ids:
            group.append(student.user_ids[0].id)
        else:
            raise osv.except_osv(_("This student does not have a user account, Contact Administrator"), student.name)
        self.message_subscribe_users(cr, SUPERUSER_ID, [res] , group, context=context)
        return res
    
    def on_change_student_id(self, cr, uid, ids, student_id, context=None):
        if student_id:
            stud_obj = self.pool.get('res.partner')
            student = stud_obj.browse(cr,uid,student_id)
        return {'value': {'term_id': [],'fname': student.fname, 'lname':student.lname}}
    
    def on_change_term_id(self, cr, uid, ids, term_id, student_id, context=None):
        if term_id:
            clearance_obj = self.pool.get('student.account')
            charge_obj = self.pool.get('term.charges')
            term_obj = self.pool.get('aun.registrar.term')
            student = self.pool.get('res.partner').browse(cr,uid,student_id,context)
            fee_obj = self.pool.get('fee.structure')
            clearance = clearance_obj.search(cr,uid, [('student_id','=',student_id)])[0]
            fee = fee_obj.browse(cr, uid, fee_obj.search(cr, uid, [('term_id','=',term_id),('level_id','=',student.level_id.id)]),context=None)
            if (fee):
                fee = fee[0]
            else:
                warning = {
                            'title': ('Invalid'),
                            'message': ('No fee structure for this term, please contact the bursar!')
                        }
                return {'value': {'term_id': []},'warning': warning}
            if clearance:
                total = 0.0
                charges = charge_obj.browse(cr, uid, charge_obj.search(cr, uid, [('term_id','=',term_id),('clearance_id','=',clearance)]),context=None)
                for charge in charges:
                    total += charge.charge
                term = term_obj.browse(cr,uid,term_id)
                l_terms = term_obj.search(cr,uid, [('code','>',term.code)])
                other = 0.0
                for l_term in l_terms:
                    o_charges = charge_obj.browse(cr, uid, charge_obj.search(cr, uid, [('term_id','=',l_term),('clearance_id','=',clearance)]),context=None)
                    for o_charge in o_charges:
                        other += o_charge.charge
                balance = student.credit - other
                if balance > total:
                    warning = {
                            'title': ('Invalid'),
                            'message': ('You are not qualified for a payment plan because you owe N' + str(balance - total) + ' from previous terms. ')
                        }
                    return {'value': {'term_id': []},'warning': warning}
                total = total + fee.min_balance
            if total > 0:
                return {'value': {'payment_id': [],'total_charge': total,'amount':total}}
            else:
                warning = {
                            'title': ('Invalid'),
                            'message': ('You do not have any charges for this term!')
                        }
                return {'value': {'term_id': []},'warning': warning}
        else:
            return True
        
    def on_change_amount(self, cr, uid, ids, amount, total_charge, context=None):
#         if amount and total_charge and amount < total_charge:
#             warning = {
#                             'title': ('Invalid'),
#                             'message': ('You have charges of N ' + str(total_charge) +' for this term, The amount requested must be greater than or equal to this amount')
#                         }
#             return {'value': {'amount': total_charge},'warning': warning}
        return True
        
    def on_change_payment_id(self, cr, uid, ids, payment_id, total_charge, term_id, student_id, context=None):
        lines = []
        note = ''
        if payment_id:
            plan_obj = self.pool.get('bursar.payment.plan')
            term_obj = self.pool.get('aun.registrar.term')
            plan = plan_obj.browse(cr, uid, payment_id)
            note = plan.note
            total = total_charge
            i = 1
            bal = 0.0
            balance = []
            term = term_obj.browse(cr,uid,term_id)
            for line in plan.line_ids:
                if line.p_type == 'balance':
                    balance.append(line)
                else:
                    if line.p_type == 'percent':
                        amount = total * line.value
                        bal += amount
                    if line.date_from == 'start':
                        s_date = term.start_date
                    elif line.date_from == 'registration_start':
                        s_date = term.reg_start
                    elif line.date_from == 'registration_end':
                        s_date = term.reg_end  
                    elif line.date_from == 'clearance':
                        s_date = datetime.datetime.now().strftime('%Y-%m-%d')   
                    due_date =  datetime.datetime.strptime(s_date[:10], tools.DEFAULT_SERVER_DATE_FORMAT)+ datetime.timedelta(days=(line.days))
                    surcharge = line.surcharge * amount
                    if line.is_down_payment == False:
                        name = 'Installment ' + str(i)
                    else: 
                        name = 'Down Payment'
                    lines.append({'amount': amount,
                                  'min_amount': amount,
                                  'surcharge': surcharge,
                                  'total': amount + surcharge,
                                  'name': name,
                                  'max_date': str(due_date)[:10],
                                  'due_date': str(due_date)[:10],
                                  'config_line_id': line.id
                                  })
                    amount += amount
                    if line.is_down_payment == False:
                        i +=1
            if balance:
                bal = (total - bal) / len(balance)
                for line in balance:
                    if line.date_from == 'start':
                        s_date = term.start_date
                    elif line.date_from == 'registration_start':
                        s_date = term.reg_start
                    elif line.date_from == 'registration_end':
                        s_date = term.reg_end  
                    elif line.date_from == 'clearance':
                        s_date = datetime.datetime.now().strftime('%Y-%m-%d')
                        if s_date < term.start_date:
                            s_date = term.start_date
                    due_date =  datetime.datetime.strptime(s_date[:10], tools.DEFAULT_SERVER_DATE_FORMAT)+ datetime.timedelta(days=(line.days))
                    surcharge = line.surcharge * bal
                    if line.is_down_payment == False:
                        name = 'Installment ' + str(i)
                    else: 
                        name = 'Down Payment'
                    lines.append({'amount': bal,
                                  'surcharge': surcharge,
                                  'total': bal + surcharge,
                                  'name': 'Installment ' + str(i),
                                  'max_date': str(due_date)[:10],
                                  'due_date': str(due_date)[:10],
                                  'config_line_id': line.id
                                  })
                    if line.is_down_payment == False:
                        i +=1
#         else:
#             raise osv.except_osv(_('No Charges'), _('You have no charges for this semester, please see bursar!'))
        
        return {'value': {'note': note, 'installment_ids': lines}}
    
    def _check_total(self, cr, uid, ids, context=None):
        plan = self.browse(cr, uid, ids,context=context)[0]
        if plan.state not in ['cancelled','paid']:
            total = 0.0
            equals = []
            e_names = []
            for line in plan.installment_ids:
                if line.config_line_id.equal == True:
                    equals.append(line.amount)
                    e_names.append(line.name)
                if plan.state == 'approved':
                    total += line.amount
                else :
                    total += line.amount
            if len(set(equals)) > 1:
                e_names = ' and '.join(e_names)
                raise osv.except_osv(_('Check Installment Amounts'), _(e_names + ' must be equal!'))
    
            if str(total) != str(plan.amount):
                print str(total)
                print str(plan.amount)
                raise osv.except_osv(_('Check Installment Amounts'), _('Your payment installments are not equal to the total charge!'))
        return True
    
    def on_change_down_payment(self, cr, uid, ids, down_payment, payment_id, context=None):
        charge = 0
        if down_payment and payment_id:
            plan_obj = self.pool.get('bursar.payment.plan')
            plan = plan_obj.browse(cr,uid,payment_id)
            charge = plan.down_surcharge * down_payment
        return {'value': {'down_surcharge': charge}}
    
    def _get_term_charge(self, cr, uid, ids, name, args, context=None):
        res = {}
        uid = SUPERUSER_ID
        for plan in self.browse(cr, uid, ids, context=context):
            clearance_obj = self.pool.get('student.account')
            charge_obj = self.pool.get('term.charges')
            fee_obj = self.pool.get('fee.structure')
            clearance = clearance_obj.search(cr,SUPERUSER_ID, [('student_id','=',plan.student_id.id)])[0]
            fee = fee_obj.browse(cr, uid, fee_obj.search(cr, uid, [('term_id','=',plan.term_id.id),('level_id','=',plan.student_id.level_id.id)]),context=None)[0]
            if clearance:
                total = 0.0
                charges = charge_obj.browse(cr, uid, charge_obj.search(cr, uid, [('term_id','=',plan.term_id.id),('clearance_id','=',clearance)]),context=None)
                for charge in charges:
                    total += charge.charge
                total = total + fee.min_balance
                res[plan.id] = total
        return res
       
    def _get_term_balance(self, cr, uid, ids, name, args, context=None):
        res = {}
        uid = SUPERUSER_ID
        for plan in self.browse(cr, uid, ids, context=context):
            clearance_obj = self.pool.get('student.account')
            charge_obj = self.pool.get('term.charges')
            term_obj = self.pool.get('aun.registrar.term')
            fee_obj = self.pool.get('fee.structure')
            clearance = clearance_obj.search(cr,uid, [('student_id','=',plan.student_id.id)])[0]
            fee = fee_obj.browse(cr, uid, fee_obj.search(cr, uid, [('term_id','=',plan.term_id.id),('level_id','=',plan.student_id.level_id.id)]),context=None)[0]
            if clearance:
                l_terms = term_obj.search(cr,uid, [('code','>',plan.term_id.code)])
                other = 0.0
                for l_term in l_terms:
                    o_charges = charge_obj.browse(cr, uid, charge_obj.search(cr, uid, [('term_id','=',l_term),('clearance_id','=',clearance)]),context=None)
                    for o_charge in o_charges:
                        other += o_charge.charge
                balance = plan.student_id.credit - other
                total = balance
                res[plan.id] = total
#                 if total <= 0 and plan.state != 'paid':
#                     self.write(cr,SUPERUSER_ID, plan.id, {'state': 'paid', 'active': False})
        return res
    
    def _get_amount_due(self, cr, uid, ids, name, args, context=None):
        res = {}
        for plan in self.browse(cr, uid, ids, context=context):
            total = 0.0
            for line in plan.installment_ids:
                total += line.total
            res[plan.id] = total
        return res
    
    def unlink(self, cr, uid, ids, context=None):
        self.case_cancel(cr,uid,ids)
        return True
    
    def case_cancel(self, cr, uid, ids, context=None):
        plan = self.browse(cr, uid, ids, context=context)[0]
        clearance_obj = self.pool.get('term.clearance')
        clearance = clearance_obj.browse(cr, SUPERUSER_ID, clearance_obj.search(cr, SUPERUSER_ID, [('term_id','=',plan.term_id.id),('student_id','=',plan.student_id.id)]))
        if clearance:
            if clearance[0].state == 'cleared':
                raise osv.except_osv(_('Invalid'), _('You cannot cancel a payment plan after student has done clearance for the term'))
            else:
                clearance_obj.write(cr,uid,clearance[0].id,{'payment_plan':[]})
        if plan.surcharge_ids:
            charge_obj = self.pool.get('term.charges')
            for surcharge in plan.surcharge_ids:
                charge_obj.unlink(cr,SUPERUSER_ID,[surcharge.id])
        self.write(cr, uid, ids, {'state': 'cancelled', 'active': False}, context=context)
        return True
    
    def case_reject(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'rejected', 'active': False}, context=context)
        return True
    
    def case_approve(self, cr, uid, ids, context=None):
        #Create invoice for surcharge
        plan = self.browse(cr, uid, ids, context=context)[0]
        line_obj = self.pool.get('bursar.payment.plan.form.line')
        for line in plan.installment_ids:
            line_obj.write(cr,uid,line.id,{'f_surcharge': line.surcharge})
        charge_obj = self.pool.get('term.charges')
        account_obj = self.pool.get('student.account')
        account = (account_obj.search(cr, uid, [('student_id','=',plan.student_id.id)])
                                             or 
                     account_obj.create(cr, uid, {'student_id': plan.student_id.id}))
        surcharges = []
        for line in plan.installment_ids:
            if line.surcharge > 0.0:
                surcharges.append({'amount': line.surcharge, 'date': line.due_date})
        res = {}
        for surcharge in surcharges:
            charge_obj.create(cr, SUPERUSER_ID,{
                               'detail_id' : plan.payment_id.surcharge_detail_id.id,
                               'name': plan.payment_id.surcharge_detail_id.desc,
                               'term_id': plan.term_id.id,
                               'charge':surcharge['amount'],
                               'invoice_date': surcharge['date'],
                               'payment_plan_id': ids[0],
                               'clearance_id': account[0] if type(account) == list else account,
                               })
        res['state'] = 'approved'
        self.write(cr, uid, ids, res)
        # Add payment plan to clearance
        clearance_obj = self.pool.get('term.clearance')
        clearance = clearance_obj.search(cr,uid, [('term_id','=',plan.term_id.id),('student_id','=',plan.student_id.id)])
        if clearance:
            clearance_obj.write(cr,uid,clearance,{'payment_plan': plan.id})
        else:
            raise osv.except_osv(_('Invalid'), _('This Student Has No Courses Registered For This Term!'))
        return True

    _columns = {
        'student_id': fields.many2one('res.partner','Student', domain="[('student','=',True)]", required=True),
        'fname': fields.related('student_id', 'fname', type='char', relation="res.partner", string="First Name", store=False, readonly=True),
        'lname': fields.related('student_id', 'lname', type='char', relation="res.partner", string="Last Name", store=False, readonly=True),
        'term_id': fields.many2one('aun.registrar.term','Term', required=True),
        'note': fields.related('payment_id', 'note', type='text', string="Description", store=False, readonly=True),
        'payment_id': fields.many2one('bursar.payment.plan', 'Payment Plan', required=True, track_visibility="onchange"),
        'amount': fields.float('Total Amount', digits=(3,2), required=True, track_visibility="onchange"),
        'total_charge': fields.function(_get_term_charge, type = 'float', digits_compute=dp.get_precision('Account'), string='Total Charge', track_visibility='onchange'),
        'balance': fields.function(_get_term_balance, type = 'float', digits_compute=dp.get_precision('Account'), string='Balance', track_visibility='onchange'),
        'installment_ids': fields.one2many('bursar.payment.plan.form.line', 'payment_id', 'Payments'),
        'state': fields.selection(PAYMENT_PLAN_STATES, 'State', required=True, track_visibility="onchange"),
        'amount_due': fields.function(_get_amount_due, type = 'float', digits_compute=dp.get_precision('Account'), string='Amount Due', track_visibility='onchange'),
        'surcharge_ids': fields.one2many('term.charges', 'payment_plan_id', 'Surcharges'),
        'override': fields.boolean('Override'),
        'active': fields.boolean('Active')
    }
    
    _constraints=[
        (_check_total, 'Your payment installments are not equal to the total charge!',['Total Charge']),
    ]
    _defaults={
            'state': 'draft',
            'active': True
        }
bursar_payment_plan_form()

class bursar_payment_plan_form_line(osv.osv):
    _name = "bursar.payment.plan.form.line"
    _inherit = ["mail.thread"]
    _description = "Payment Plan Application"
    
    def _get_surcharge(self, cr, uid, ids, name, args, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = {
                'total': 0.0,
                'surcharge': 0.0,
            }
            amount = 0.0
            if line.payment_id.state != 'approved':
                charge = line.config_line_id.surcharge * line.amount
            else:
                charge = line.f_surcharge
            res[line.id]['surcharge'] = charge
            res[line.id]['total'] = charge + line.amount
            total_charge = line.payment_id.total_charge
            if line.config_line_id.p_type == 'percent':
                amount = total_charge * line.config_line_id.value
#             elif line.config_line_id.p_type == 'fixed':
#                 amount = line.config_line_id.value
            res[line.id]['min_amount'] = amount
        return res
    
    def on_change_amount(self, cr, uid, ids, amount, config_line_id, context=None):
        line_obj = self.pool.get('bursar.payment.plan.line')
        line = line_obj.browse(cr,uid,config_line_id)
        charge = line.surcharge * amount
        total = charge + amount
        return {'value': {'surcharge': charge,'total':total}}
    
    def _check_date(self, cr, uid, ids, context=None):
        line = self.browse(cr, uid, ids,context=context)[0]
        if not line.payment_id.override:
            if line.due_date > line.max_date:
                max_date = time.strftime("%a %b %d %Y",time.strptime(line.max_date,"%Y-%m-%d"))
                raise osv.except_osv(_('Invalid Due Date on '+ line.name), _('Please select a date less than or equal to ' + max_date))
        return True
    
    def _check_amount(self, cr, uid, ids, context=None):
        line = self.browse(cr, uid, ids,context=context)[0]
        if not line.payment_id.override:
            if line.config_line_id.p_type == 'percent':
                if line.config_line_id.options == 'equal':
                    if line.amount != line.min_amount:
                        raise osv.except_osv(_('Invalid Amount on '+ line.name), _('Your Payment must be equal to N' + str(line.min_amount)))
                elif line.config_line_id.options == 'least':
                    if line.amount < line.min_amount:
                        raise osv.except_osv(_('Invalid Amount on '+ line.name), _('Your Payment must be at least N' + str(line.min_amount)))
#         elif line.config_line_id.p_type == 'fixed':
#             if line.config_line_id.options == 'equal':
#                 if line.amount != line.min_amount:
#                     raise osv.except_osv(_('Invalid Amount on '+ line.name), _('Your Payment must be equal to N' + str(line.min_amount)))
#             elif line.config_line_id.options == 'least':
#                 if line.amount < line.min_amount:
#                     raise osv.except_osv(_('Invalid Amount on '+ line.name), _('Your Payment must be at least N' + str(line.min_amount)))

        return True
    
    _columns = {
        'name': fields.char('Name', required = True, readonly=True),
        'payment_id': fields.many2one('bursar.payment.plan.form', 'Payment Plan', required=True, ondelete='cascade'),
        'amount': fields.float('Installment Amount', track_visibility = "onchange", required=True),
        'min_amount': fields.function(_get_surcharge, type = 'float', digits_compute=dp.get_precision('Account'), string='Min Amount', multi='all'),
        'surcharge': fields.function(_get_surcharge, type = 'float', digits_compute=dp.get_precision('Account'), string='Service Charge', track_visibility='onchange', multi='all'),
        'f_surcharge': fields.float('Service Charge', digits_compute=dp.get_precision('Account'), readonly=True),
        'total': fields.function(_get_surcharge, type = 'float', digits_compute=dp.get_precision('Account'), string='Total Amount Due', track_visibility='onchange', multi='all'),
        'due_date': fields.date('Due Date', track_visibility = "onchange", required=True),
        'max_date': fields.date('Max Date', required=True),
        'config_line_id': fields.many2one('bursar.payment.plan.line', 'Configuration Line', required=True),
    }
    _constraints=[
        (_check_date, 'Check Due Date',['Due Date']),
        (_check_amount, 'Check Amount',['Amount']),
    ]
bursar_payment_plan_form()