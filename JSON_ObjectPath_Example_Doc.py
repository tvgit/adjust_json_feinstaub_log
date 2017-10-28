# -*- coding: utf-8 -*-

import StringIO
import string
import json
import objectpath


json_src = '''
{
"a":10,
"a_0":{"bd_1":1, "bd_2":2, "bd_3":3},
"a_1":{"b_list":[1,2,3]},
"a_2":{"b_list_dict_2":[{"c_200":200},{"c_201":201},{"c_202":202}]},
"a_3":{"b_list_dict_3":[{"c_300":300, "c_301":301},{"c_302":302, "c_303":303},{"c_304":304, "c_305":305}]},
"a_4":{"b_list_dict_4":[{"c_400":400, "c_401":401},{"c_402":402, "c_403":403},{"c_404":404, "c_405":405},406,407]}}
'''

json_file     = StringIO.StringIO(json_src)
json_data     = json_file.read()           # read the json data text file
json_data_str = json.loads(json_data)      # convert it into json data

def print_query(json_objectpath_tree, query_str):
    """ print query-string, result type and result of a query to an objectpath_tree     
    """
    result          = json_objectpath_tree.execute(query_str)  # result of query
    result_str      = string.lstrip(str(result))               # result of query as string
    result_type     = type(result)                             # type of result
    result_type_str = str(result_type)                         # type of result as string

    # first some formatting ...
    if (len(result_type_str) % 2 == 1):
        result_type_str = result_type_str + ' '
    rslt_type_spcs = '. ' * ((20 - len(result_type_str)) // 2) + '  '

    if (len(query_str) % 2 == 1):
        query_str = query_str + ' '
    query_spcs = '. ' * ((46 - len(query_str)) // 2)
    if (len(query_spcs) % 2 == 0):
        query_spcs = '' + query_spcs

    # ... here's the beef:
    # now print finally the result ( == result_str)
    print query_str + '  ' + query_spcs + result_type_str + rslt_type_spcs,
    print result_str

    # but notice: result may be a generator object!
    if ('generator' in result_type_str) :
        value_type_generator = result
        print query_str + '  ' + query_spcs + result_type_str + rslt_type_spcs,
        # Do the trick! Convert generator to list:
        result_str = list(value_type_generator)
        # Convert list to string:
        print str(result_str)

if __name__ == "__main__":
    print 'json_data_str: ' + json.dumps(json_data_str, sort_keys=True) + '\n'
    print 'json_data_str: ' + json.dumps(json_data_str, sort_keys=True, indent=2)

    objectpath_tree = objectpath.Tree(json_data_str)

    print '\nShow types:'
    print_query(objectpath_tree, '$.a')
    print_query(objectpath_tree, '$.a_0.bd_1')
    print_query(objectpath_tree, '$.a_0.bd_2')
    print_query(objectpath_tree, '$.a_0')
    print_query(objectpath_tree, '$.a_1')
    print_query(objectpath_tree, '$.a_1.*')
    print_query(objectpath_tree, '$.a_1.b_list')

    print '\nList:'
    print_query(objectpath_tree, '$.a_2.b_list_dict_2')
    print_query(objectpath_tree, '$.a_2.b_list_dict_2[0]')
    print_query(objectpath_tree, '$.a_2.b_list_dict_2[1]')
    print_query(objectpath_tree, '$.a_2.b_list_dict_2[-1]')
    #print_query(objectpath_tree, '$.a_2.b_list_dict_2[0:1]')  # ERROR ?!
    #print_query(objectpath_tree, '$.a_2.b_list_dict_2[0:2]')  # ERROR ?!
    print_query(objectpath_tree, '$.a_2.b_list_dict_2[@.c_201 is 201]')

    print '\nList of dict:'
    print_query(objectpath_tree, '$.a_3.b_list_dict_3')
    print_query(objectpath_tree, '$.a_3.b_list_dict_3[0]')
    print_query(objectpath_tree, '$.a_3.b_list_dict_3[1]')
    print_query(objectpath_tree, '$.a_3.b_list_dict_3[-1]')
    print_query(objectpath_tree, '$.a_3.b_list_dict_3[@]')
    print_query(objectpath_tree, '$.a_3.b_list_dict_3[@].c_301')
    print_query(objectpath_tree, '$.a_3.b_list_dict_3[@.c_300 is 300].*')
    print_query(objectpath_tree, '$.a_3.b_list_dict_3[@.c_300 is 300].c_301')

    print '\nList:'
    print_query(objectpath_tree, '$.a_4.b_list_dict_4')

    print '\nShow everything:'
    print_query(objectpath_tree, '$.*')
    print_query(objectpath_tree, '$..*')


