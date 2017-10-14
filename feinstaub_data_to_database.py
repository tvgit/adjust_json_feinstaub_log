# -*- coding: utf-8 -*-
# 2017_05_25-11_34_35 generated by: >pyprogen.py<
# >5297844881f21af0624b379c060d8998< 

# YOUR code resides in THIS module.

import lib.x_CAParser as x_CAParser
import lib.ppg_utils  as p_utils
from   lib.ppg_log    import p_log_init, p_log_start, p_log_this, p_log_end

import lib.x_glbls
import fnmatch
import string
import os
import objectpath
import json

import sqlite3
import time
import csv
from operator import itemgetter, attrgetter, methodcaller
import datetime


cnt_files = 0
cnt_lines = 0

cnt_files_fail = 0
cnt_lines_fail = 0


# 'confargs' are your configuration parameters / cmdline arguments
confargs = lib.x_glbls.arg_ns


class Data(object):
    def __init__(self):
        self.ip        = ''
        self.unix_time = ''
        self.esp8266id = ''
        self.software_version = ''
        self.zeit      = ''
        self.datum     = ''
        self.uhrzeit   = ''
        self.humidity  = ''
        self.temperature = ''
        self.SDS_P1    = ''
        self.SDS_P2    = ''
        self.line_nr   = ''

    def data_print(self):
        print self.ip,
        print self.unix_time,
        print self.esp8266id,
        print self.software_version,
        print self.zeit,
        print self.datum,
        print self.uhrzeit,
        print self.humidity,
        print self.temperature,
        print self.SDS_P1,
        print self.SDS_P2,
        print self.line_nr


# https://pymotw.com/2/sqlite3/

def create_table(fn_db):
    print 'Creating schema'
    with sqlite3.connect(fn_db) as conn:
        schema = "CREATE TABLE fstb(unix_time INTEGER, esp8266id STRING, software_version STRING," \
                 "zeit, datum, uhrzeit, humidity REAL, temperature REAL, SDS_P1 REAL, SDS_P2 REAL, line_number INTEGER, " \
                 "PRIMARY KEY(esp8266id, unix_time));"
        conn.executescript(schema)
        schema = """
        CREATE TABLE saved_files(saved_file STRING PRIMARY KEY, unix_time INTEGER, date_time STRING, lines INTEGER, 
                 cnt INTEGER, cnt_ok INTEGER, cnt_fail INTEGER);"""
        conn.executescript(schema)


def make_sqlite_db(fn_db, make_new_db = False):
    # +/- testing :
    if make_new_db:
        p_utils.p_file_delete(fn_db)

    msge = 'checking database: >' + fn_db + '<'
    print msge
    p_log_this(msge)

    if not os.path.exists(fn_db) :
        print 'create_table: >' + fn_db + '<'
        # conn = sqlite3.connect(fn_db)
        # conn.close()
        create_table(fn_db)
    # conn.close() # Not necessary because of 'with'


def delete_fn_in_db(db_fn, db_table, data_file_name):
    # Delete >data_file_name< in >db_fn<, >db_table<
    sql  = "DELETE FROM " + db_table + " WHERE "
    sql += " saved_file = '" + str(data_file_name) + "' ; "
    print sql; p_log_this(sql)

    with sqlite3.connect(db_fn) as conn:
        cursor = conn.execute(sql)
        return True
    print ' failed !!!'
    return False


def check_fn_in_db(db_fn, db_table, data_file_name):
    # If >data_file_name< is in db return >True<
    msge = 'Check if filename of data_file: >' + data_file_name + '< is in database: >' + db_fn + '<.'
    print msge
    # p_log_this(msge)
    sql = "SELECT * FROM " + db_table
    sql += " WHERE "
    sql += " saved_file = '" + str(data_file_name) + "' ; "
    print sql ,
    p_log_this(sql)

    with sqlite3.connect(db_fn) as conn:
        cursor = conn.execute(sql)
        for row in cursor.fetchall():
            date_time = row[0]
            print ' ok: ' + date_time
            return True
    print ' failed -> '
    return False


def check_fn_data_in_db(db_fn, db_table, data_file_name, cnt_lines, cnt_ele):
    # If       all data from file named 'fn' is completely in db => return >date_time<
    # If only some data from file named 'fn' is in db            => return >Null<
    msge = 'Check if all values from data_file: >' + data_file_name + '< are in database: >' + db_fn + '<.'
    print msge
    # p_log_this(msge)
    sql = "SELECT date_time FROM " + db_table
    sql += " WHERE "
    sql += " saved_file = '" + str(data_file_name) + "' AND "
    sql += " lines = '" + str(cnt_lines) + "' AND "
    sql += " cnt = '" + str(cnt_ele) + "' ;   "
    print sql,
    p_log_this(sql)

    with sqlite3.connect(db_fn) as conn:
        cursor = conn.execute(sql)
        for row in cursor.fetchall():
            date_time = row[0]
            print ' ok: ' + date_time
            return date_time
    print ' failed !!!'
    return


def insert_fn_in_db(db_fn, db_table, data_file_name, cnt_lines, cnt, cnt_ok, cnt_fail):
    msge = 'Insert name of data_file: >' + data_file_name + '< into database: >' + db_fn + '<.'
    print msge
    p_log_this(msge)
    unix_time = int(time.time())
    date_time = datetime.datetime.fromtimestamp(int(unix_time)).strftime('%Y-%m-%d %H:%M:%S')

    sql  = "INSERT INTO " + db_table
    sql += " (saved_file, unix_time, date_time, lines, cnt, cnt_ok, cnt_fail )"
    sql += " VALUES ('" + data_file_name + "', '" + str(unix_time) + "', '" + date_time + "', '"
    sql += str(cnt_lines) + "', '" + str(cnt) + "', '" + str(cnt_ok) + "', '" + str(cnt_fail) + "')"
    # print sql

    with sqlite3.connect(db_fn) as conn:
        ret_val = conn.execute(sql)


def check_all_values_ok(ele):
    "Sind alle Werte != None? (Manchmal, d.h. bei den ersten Files, fehlt zB esp8266id)"
    # print dir(ele)
    for property, value in vars(ele).iteritems():
        # print property, ": ", value
        if not value:
            # print property, ": ", value, "   ",
            msge = str (property) + ": " + str (value) + " fehlt!  "
            p_log_this(msge); print msge
            return False
    return True


def insert_data_in_db(table, db_fn, db_table, data_file_name):
    cnt = 0; cnt_ok = 0 ; cnt_fail = 0
    with sqlite3.connect(db_fn) as conn:
        for ele in table:
            # print_data_ele(ele)
            cnt += 1    # counts line of (!) table (not of file)


            # Dumme Korrektur: erst mit der File >20170605.log< werden sowohl ip-Adresse
            # als auch esp8266id aufgezeichnet. Aber beide Daten werden zur späteren Identifikation der Sensoren
            # benötigt. => bis zum 2017-06-05 also diese Daten substituieren.

            limit = int(1496613625)
#            if (int(ele.unix_time) <= limit) and (ele.ip == "192.168.2.102") and (ele.esp8266id is None):
            if (int(ele.unix_time) <= limit) and (ele.esp8266id is None):
                if (ele.ip  == "http://192.168.2.101"):
                    ele.esp8266id = "2326588"
                else:
                    ele.esp8266id = "3912953"

            if check_all_values_ok(ele):
                sql = "INSERT INTO " + db_table
                sql += " (unix_time, esp8266id, software_version," +\
                          " zeit, datum, uhrzeit," + \
                          " humidity, temperature, SDS_P1, SDS_P2, line_number)"
                sql += " VALUES ('" + str(ele.unix_time) + "', '" + str(ele.esp8266id) + "', '" + str(ele.software_version)
                sql += "', '" + ele.zeit + "', '" + ele.datum + "', '" + ele.uhrzeit
                sql += "', '" + ele.humidity + "', '" + ele.temperature + "', '" + ele.SDS_P1 + "', '" + ele.SDS_P2
                sql += "', '" + str(ele.line_nr) + "')"
                # print sql
                try:
                    ret_val = conn.execute(sql)
                    if ret_val != -1:
                        cnt_ok += 1
                    else:
                        mssge = data_file_name + ': INSERT failed: line number:' + str(cnt)
                        p_utils.p_terminal_mssge_note_this(mssge)
                        mssge = 'conn.execute(sql) == -1: ' + sql
                        p_utils.p_terminal_mssge_note_this(mssge)
                        cnt_fail += 1
                except:
                    mssge = data_file_name + ': INSERT failed: line number:' + str(cnt)
                    p_utils.p_terminal_mssge_note_this(mssge)
                    p_utils.p_terminal_mssge_note_this('SQL: >' + sql + '<')
                    cnt_fail += 1
                    # print sql, ret_val
            else:
                mssge = data_file_name + ': line not inserted: table line number:' + str(cnt) + ' (Some val == None)'
                p_utils.p_terminal_mssge_note_this(mssge)
                cnt_fail += 1

    # print data_file_name, cnt, cnt_ok , cnt_fail
    msge = 'insert_data_in_db(): insert values from: >' + data_file_name + '< to database: >' + db_fn + '<.'
    print msge
    p_log_this(msge)
    msge = 'insert_data_in_db(): table has ' + str(len(table)) + ' values'
    print msge
    p_log_this(msge)

    msge = 'insert_data_in_db(): cnt, cnt_ok, cnt_fail: ' + str(cnt) + ' ' + str(cnt_ok) + ' ' + str(cnt_fail)
    print msge
    p_log_this(msge)
    return cnt, cnt_ok, cnt_fail


def get_data_files(feinstaub_dir):
    # returns filenames in >feinstaub_dir< that correspond to '*.log'.
    fn_s = p_utils.p_dir_return_paths_of_level(path=feinstaub_dir, level=1, do_log=True)
    log_files = []
    for fn in fn_s:
        if fnmatch.fnmatch(fn, '*.log'):
            log_files.append(fn)
            print fn

    # return log_files[0:2]
    return log_files


def adjust_feinstaub_logfiles(feinstaub_dir):
    # korrigiert Formatierungsfehler in den frühen YYYYMMDD.log Datenfiles
    # - durch mich ()rh hineingebracht
    # nicht mehr nötig

    # print msge, feinstaub_dir
    p_log_this(msge)
    log_files = get_data_files(feinstaub_dir)

    for log_file_name in log_files:
        org_log_file_name = log_file_name[:-4] + ".org"
        tmp_log_file_name = log_file_name[:-4] + ".tmp"

        log_file = p_utils.p_file_open(log_file_name, mode='r')
        tmp_file = p_utils.p_file_open(tmp_log_file_name, mode='w')
        if p_utils.p_file_exists(tmp_log_file_name):
            for line in iter(log_file):
                pos = string.find(line, ',"unix_time":')
                line = line[:pos] + '"' + line[pos:]
                pos = string.find(line, '"ip":') + len('"ip":')
                line = line[:pos] + '"' + line[pos:]
                tmp_file.write(line)
                # print line [:60]
                # print line.find('"ip":'), line[:30]
            p_utils.p_file_close(tmp_file)
        p_utils.p_file_close(log_file)

        os.rename(log_file_name, org_log_file_name)
        os.rename(tmp_log_file_name, log_file_name)

        print log_file_name
        print org_log_file_name
        print tmp_log_file_name


# https://stackoverflow.com/questions/1373164/how-do-i-create-a-variable-number-of-variables
def val_fetch_from_tree_sensor(obj, json_tree, var_name, new_name):
    # Gets from jsontree the value of element 'varname' and stores it
    # to instance of class Data (== obj) - if new_name is given under the name 'new_name'
    if new_name:
        setattr(obj, new_name, json_tree.execute("$." + var_name))
        return getattr(obj, new_name)
    else:
        setattr(obj, var_name, json_tree.execute("$." + var_name))
        return getattr(obj, var_name)


def val_fetch_from_tree_sensor_data (obj, json_tree, var_name):
    # Gets from jsontree the value of element 'varname', IF IT IS ELEMENT OF AN GENERATOR...
    # ... and stores it to instance of class Data (== obj)
    # - if new_name is given under the name 'new_name'
    query_str = "$.daten.sensordatavalues[@.value_type is " + var_name + "].value"
    value_type_generator = json_tree.execute(query_str)
    # val_set(obj, var_name, list(value_type_generator)[0]),
    setattr(obj, var_name, list(value_type_generator)[0]),
    return getattr(obj, var_name)


def write_csv (table, fn_csv):
    if p_utils.p_file_make(fn_csv, print_message=False):
        f_csv = p_utils.p_file_open(fn_csv, mode= 'wb')
        header_str = ('unix_time', 'esp8266id', 'zeit' , 'datum' , 'uhrzeit', 'humidity', 'temperature', 'SDS_P1', 'SDS_P2')
        # print header_str
        try:
            # writer = csv.writer(f_csv, quoting=csv.QUOTE_NONNUMERIC, lineterminator='\n')
            writer = csv.writer(f_csv, quoting=csv.QUOTE_NONNUMERIC)
            writer.writerow((header_str))

            for row in table:
                # line = (row.esp8266id, row.datum, row.uhrzeit, row.humidity, row.temperature, row.SDS_P1, row.SDS_P2)
                # writer.writerow((line))

                writer.writerow(
                    (
                    row.unix_time,
                    row.esp8266id,
                    row.zeit,
                    row.datum,
                    row.uhrzeit,
                    row.humidity,
                    row.temperature,
                    row.SDS_P1,
                    row.SDS_P2
                    )
                )
        finally:
            p_utils.p_file_close(f_csv)
    else:
        p_utils.p_terminal_mssge_error(fn_csv)


def process_single_json_data_file(data_file_name):
    # In >data_table< werden die Daten zwischengespeichert, bevor sie in die Datenbank geschrieben werden.
    data_table = []
    cnt_line = 0 ; cnt_ele = 0 ; cnt_fail_01 = 0 ; cnt_fail_02 = 0
    mssge_01 = '' ; mssge_02 = ''
    with open(data_file_name, 'r') as f:
        p_log_this('processing: >' + data_file_name + '<')
        for line in f:
            cnt_line += 1
            ele = Data()
            # delete leading comma:
            if line[0] == ',': line = line[1:]
            try:  # to transform JSON-Data to data_table
                json_data = json.loads(line)
                json_tree = objectpath.Tree(json_data)
                try:
                    val_fetch_from_tree_sensor(ele, json_tree, 'ip', 'ip'),
                    # print json_tree.execute('$.datum')   # == query JSON string for item: >datum<
                    val_fetch_from_tree_sensor(ele, json_tree, 'time', 'unix_time'),

                    val_fetch_from_tree_sensor(ele, json_tree, 'daten.esp8266id', 'esp8266id'),
                    # print '$.daten.esp8266id', json_tree.execute('$.daten.esp8266id')
                    val_fetch_from_tree_sensor(ele, json_tree, 'daten.software_version', 'software_version'),
                    # print 'software_version', json_tree.execute('$.daten.software_version')

                    val_fetch_from_tree_sensor(ele, json_tree, 'datum', ''),
                    val_fetch_from_tree_sensor(ele, json_tree, 'zeit', 'uhrzeit'),

                    # query for first element of dict:

                    # query_str = "$.daten.sensordatavalues[@.value_type is 'SDS_P1'].value"
                    # value_type_generator = json_tree.execute(query_str)
                    # print val_set(ele, 'SDS_P1', list(value_type_generator)[0]),

                    val_fetch_from_tree_sensor_data(ele, json_tree, 'SDS_P1'),
                    val_fetch_from_tree_sensor_data(ele, json_tree, 'SDS_P2'),
                    val_fetch_from_tree_sensor_data(ele, json_tree, 'temperature'),
                    val_fetch_from_tree_sensor_data(ele, json_tree, 'humidity')

                    HrMnSec = ele.uhrzeit.split(':')
                    if len(HrMnSec[0]) == 1:
                        HrMnSec[0] = '0' + HrMnSec[0]
                        ele.uhrzeit = ':'.join(HrMnSec)
                    ele.zeit = ele.datum + ' ' + ele.uhrzeit
                    # print ele.zeit

                    ele.line_nr = cnt_line
                    data_table.append(ele)
                    cnt_ele += 1
                except:
                    cnt_fail_01 += 1
                    mssge_01 = data_file_name + ': ' + line + str(cnt_fail_01) + ' ERROR process_single_json_data_file() ... val_fetch_*()'
            except:
                cnt_fail_02 += 1
                mssge_02 = data_file_name  + ': ' + line + str(cnt_fail_02) + ' ERROR process_single_json_data_file() ... json.loads()'

    if mssge_01:
        p_utils.p_terminal_mssge_note_this(mssge_01)
        p_log_this(mssge_01)

    if mssge_02:
        p_utils.p_terminal_mssge_note_this(mssge_02)
        p_log_this(mssge_02)

    mssge = 'process_single_json_data_file: >' + data_file_name + '<; lines total:' + str(cnt_line)
    p_log_this(mssge); print mssge
    # cnt_line == lines in file;
    # data_table    == data_table of ele (objects of type Data)
    # cnt_ele   == cnt   of ele (objects of type Data)
    return cnt_line, data_table, cnt_ele


def process_all_json_data_files(feinstaub_dir, fn_db):
    # Macht aus JSON Files eine große SQL-Tabelle.
    # - für jede Data-File im Daten-Dir:
    #   - für jede Zeile:
    #     - transformiere die JSON-Struktur in eine Python-Liste
    #     - hänge diese Liste an eine interne python-Tabelle
    #   - wenn Data-File vollständig gelesen:
    #     - wenn Daten dieser File noch nicht in SQL-Tabelle:
    #       speichere sie in der SQL-Tabelle
    # Kern ist die Format-Unwandlung JSON -> orthogonale aber nicht normierte SQL-Tabelle
    #
    msge = 'Dir of JSON -Data files: >' + str(feinstaub_dir) + '<'
    p_log_this(msge)
    table = []
    # dir = r'\\RB3-WORK\lighttpd\Feinstaublog'
    data_files = get_data_files(feinstaub_dir)
    # data_files = [r'.\feinstaublog\20170603.log']
    cnt_files = 0 ;  cnt_ele = 0;  cnt_ok = 0
    for data_file_name in sorted(data_files):
        if p_utils.p_file_exists(data_file_name):
            cnt_files += 1
            mssge = 'File #' + str(cnt_files) + '  ' + data_file_name
            p_utils.p_terminal_mssge_note_this(mssge)

            table[:] = []
            # cnt_line == lines in file;
            # table    == table of ele (objects of type Data)
            # cnt_ele  == cnt   of ele (objects of type Data)
            cnt_lines, table, cnt_ele = process_single_json_data_file(data_file_name)

            # https://wiki.python.org/moin/HowTo/Sorting
            tmp_table = sorted(table, key=attrgetter('unix_time', 'esp8266id'))
            table [:] = []; table = tmp_table
            # print ' len(table): ', len(table), ' nach tmp_table = sorted(table, ... )'

            # make new csv-file with identical fn but extension == 'csv':
            # fn_csv = ('.').join(data_file_name.split('.')[:-1]) + '.csv'
            # fn_csv = os.path.normpath(fn_csv)
            # print fn_csv
            # write_csv(table, fn_csv)

            data_file_base_name = os.path.basename(os.path.normpath(data_file_name))
            # Sind die Daten schon in der sqlite-Tabelle? <=> insertdate != ''
            insert_date = check_fn_data_in_db(fn_db, 'saved_files', data_file_base_name, cnt_lines, cnt_ele)

            if not insert_date:
                msge = '>' + data_file_name + '<: data will be inserted!'
                print msge; p_log_this(msge)
                # Hier und jetzt werden die Daten in die Tabelle geschrieben:
                cnt, cnt_ok, cnt_fail = insert_data_in_db(table, fn_db, 'fstb', data_file_name)
                if check_fn_in_db(fn_db, 'saved_files', data_file_base_name):
                    msge = "deleting: " + data_file_base_name +  " from: "  + fn_db
                    print msge; p_log_this(msge)
                    delete_fn_in_db(fn_db, 'saved_files', data_file_base_name)
                insert_fn_in_db(fn_db, 'saved_files', data_file_base_name, cnt_lines, cnt, cnt_ok, cnt_fail)
            else:
                msge = '>' + data_file_name + '<: already inserted (' + insert_date + ')'
                print msge; p_log_this(msge)
        else:
            p_utils.p_terminal_mssge_error('File not found: ' + data_file_name)



def main():
    p_log_this('begin')
    # eval_confargs()
    # adjust_feinstaub_logfiles(confargs.dir)

    # fn_db = r'C:\tmp\sqlite\feinstaub_0011.db'
    fn_db = r'feinstaub_0011.db'
    fn_db = os.path.normpath(fn_db)

    # (make_new_db = True) => Alte Datenbank wird gelöscht und neue db frisch angelegt
    make_sqlite_db(fn_db = fn_db, make_new_db = False)
    # make_sqlite_db(fn_db = fn_db, make_new_db = True)
    process_all_json_data_files(confargs.dir, fn_db)

    # inspire_some_file_operations()
    p_log_this('end')


if __name__ == "__main__":
    p_utils.p_program_name_and_dir_print()
    p_log_init(log_dir = 'log', log_fn = r'feinstaub_data_to_database.log')
    p_log_start()

    # read commandline arguments:
    x_CAParser.x_parser()

    # optional reading of cfg-file: (r' == raw string) 
    x_CAParser.x_parser('--conf-file', r'.\cfg\adjust_feinstaub_json.cfg')

    main()

    p_log_end()
    p_utils.p_terminal_mssge_success()
    # p_utils.p_terminal_mssge_note_this()
    # p_utils.p_terminal_mssge_error()
    p_utils.p_exit()

    # You may use >pyinstaller.exe< to dist your program:
    # pyinstaller.exe --onefile feinstaub_data_to_database.py

# 2017_05_25-11_34_35