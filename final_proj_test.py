import unittest
from final_proj import *

class TestFunction(unittest.TestCase):
    global JS_list,job3,job
    job='Data Analyst'
    JS_list=[]
    job1=Jobsum("Network Analyst","Tata Technologies","Auburn Hills, MI","$40 - $45 an hour","Use data necessary to answer business questions including data from data warehouse, operational systems, Hadoop, and external sources....")
    JS_list.append(job1)
    job2=Jobsum("Network Analyst","Tata Technologies","Auburn Hills, MI","$40 - $45 an hour","Use data necessary to answer business questions including data from data warehouse, operational systems, Hadoop, and external sources....")
    JS_list.append(job2)
    job3=Jobsum("Business Analyst","New York Jets","Florham Park, NJ 07932","Not available","Familiarity with data modeling and Extract / Transform / Load (ETL) processes a plus. Design and supervise historical and predictive analytical data models (e.g...")
    JS_list.append(job3)
    
    def test_check_unique_in_list(self):
        results=check_unique_in_list(JS_list)
        self.assertEqual(len(results),2)
        self.assertIn(job3,results)

    def test_research_results(self):
        results=init_update_insert_db_for_job(job,30)
        self.assertEqual(len(results),30)

DBNAME='jobs.db'
class TestDatabase(unittest.TestCase):
    global DBNAME
    def test_table_names(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
        statement='''
            SELECT name FROM sqlite_master WHERE type='table'
        '''
        table=cur.execute(statement)
        table_list=table.fetchall()
        table_name_list=[]
        for i in table_list:
            table_name_list.append(i[0])
        self.assertIn('Area',table_name_list)
        self.assertIn('Series',table_name_list)
        self.assertIn('Summary',table_name_list)
        conn.close()

    def test_Area_table(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
        statement='''
            SELECT AreaName
            FROM Area
            WHERE AreaName like '%South%'
        '''
        results=cur.execute(statement)
        results_list=results.fetchall()
        self.assertIn(('South',),results_list)
        self.assertEqual(len(results_list),7)

        statement='''
            SELECT COUNT(*)
            FROM Area
        '''
        results= cur.execute(statement)
        count=results.fetchone()[0]
        self.assertEqual(count, 58)

        conn.close()
    def test_Series_table(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
        statement='''
            SELECT ItemCode
            FROM Series
            WHERE AreaCode = '0000'
        '''
        results=cur.execute(statement)
        results_list=results.fetchall()
        self.assertIn(('SA0',),results_list)
        self.assertEqual(len(results_list),808)

        statement='''
            SELECT COUNT(*)
            FROM Series
        '''
        results= cur.execute(statement)
        count=results.fetchone()[0]
        self.assertEqual(count, 6745)

        conn.close()
    def test_Summary_table(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
        statement='''
            SELECT COUNT(*),Period
            FROM Summary
            GROUP by Period
        '''
        results=cur.execute(statement)
        results_list=results.fetchall()
        self.assertIn((14486,'M06'),results_list)
        self.assertEqual(len(results_list),16)

        statement='''
            SELECT Value
            FROM Summary
            ORDER BY Value desc
        '''
        results= cur.execute(statement)
        results_list=results.fetchall()
        self.assertEqual(len(results_list), 226701)
        self.assertGreater(results_list[0][0],640)

        conn.close()

    def test_DataAnalyst_table(self):
        Job=job
        Job=Job.replace(' ','')
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
        statement='''
            SELECT name FROM sqlite_master WHERE type='table'
        '''
        table=cur.execute(statement)
        table_list=table.fetchall()
        table_name_list=[]
        for i in table_list:
            table_name_list.append(i[0])
        if Job in table_name_list:
            conn = sqlite3.connect(DBNAME)
            cur = conn.cursor()
            statement='SELECT JobTitle FROM '+Job
            results=cur.execute(statement)
            results_list=results.fetchall()
            title_list=[]
            for i in results_list:
                title_list.append(i[0])
            self.assertIn(job,title_list)
        conn.close()

unittest.main()
